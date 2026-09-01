const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: Record<string, unknown>;

  constructor(message: string, status: number, code?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// In-memory access token storage (never exposed in localStorage for security)
let _inMemoryAccessToken: string | null = null;
let _refreshPromise: Promise<string | null> | null = null;

export function getAccessToken(): string | null {
  return _inMemoryAccessToken;
}

export function setAccessToken(token: string | null): void {
  _inMemoryAccessToken = token;
}

async function refreshAccessToken(): Promise<string | null> {
  if (_refreshPromise) {
    return _refreshPromise;
  }

  _refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include', // Sends HttpOnly refresh_token cookie
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        setAccessToken(null);
        return null;
      }

      const data = await response.json();
      if (data.access_token) {
        setAccessToken(data.access_token);
        return data.access_token;
      }
      setAccessToken(null);
      return null;
    } catch {
      setAccessToken(null);
      return null;
    } finally {
      _refreshPromise = null;
    }
  })();

  return _refreshPromise;
}

function getAuthHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = {
    'Accept': 'application/json',
    ...customHeaders,
  };
  if (_inMemoryAccessToken) {
    headers['Authorization'] = `Bearer ${_inMemoryAccessToken}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = 'An unexpected error occurred';
    let code = 'UNKNOWN_ERROR';
    let details: Record<string, unknown> | undefined = undefined;

    try {
      const errorData = await response.json();
      if (errorData.error) {
        errorMessage = errorData.error.message || errorMessage;
        code = errorData.error.code || code;
        details = errorData.error.details;
      } else if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((d: { msg?: string }) => d.msg).join(', ');
        }
      }
      if (errorData.error_code) {
        code = errorData.error_code;
      }
    } catch {
      errorMessage = response.statusText || errorMessage;
    }

    throw new ApiError(errorMessage, response.status, code, details);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

async function fetchWithAuth<T>(
  url: string,
  options: RequestInit,
  retryOn401 = true
): Promise<T> {
  const reqHeaders = getAuthHeaders(options.headers as Record<string, string>);
  const response = await fetch(url, {
    ...options,
    headers: reqHeaders,
    credentials: 'include', // Always send cookies for auth sessions
  });

  // If unauthorized and request is not already an auth endpoint, attempt silent token refresh
  if (response.status === 401 && retryOn401 && !url.includes('/auth/login') && !url.includes('/auth/refresh') && !url.includes('/auth/register')) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      // Retry original request with fresh access token
      const retryHeaders = {
        ...reqHeaders,
        'Authorization': `Bearer ${newToken}`,
      };
      const retryResponse = await fetch(url, {
        ...options,
        headers: retryHeaders,
        credentials: 'include',
      });
      return handleResponse<T>(retryResponse);
    }
  }

  return handleResponse<T>(response);
}

export async function apiGet<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return fetchWithAuth<T>(url.toString(), {
    method: 'GET',
    cache: 'no-store',
  });
}

export async function apiPost<T, B = unknown>(path: string, body: B): Promise<T> {
  return fetchWithAuth<T>(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
}

export async function apiPut<T, B = unknown>(path: string, body: B): Promise<T> {
  return fetchWithAuth<T>(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
}

export async function apiDelete<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return fetchWithAuth<T>(url.toString(), {
    method: 'DELETE',
  });
}

export async function downloadFile(
  path: string,
  params?: Record<string, unknown>,
  fallbackFilename = 'export'
): Promise<void> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const reqHeaders = getAuthHeaders();
  let response = await fetch(url.toString(), {
    method: 'GET',
    headers: reqHeaders,
    credentials: 'include',
    cache: 'no-store',
  });

  if (response.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      response = await fetch(url.toString(), {
        method: 'GET',
        headers: { ...reqHeaders, 'Authorization': `Bearer ${newToken}` },
        credentials: 'include',
        cache: 'no-store',
      });
    }
  }

  if (!response.ok) {
    throw new ApiError('Failed to download file', response.status);
  }

  const blob = await response.blob();
  const contentDisposition = response.headers.get('content-disposition');
  let filename = fallbackFilename;

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }

  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(blobUrl);
}
