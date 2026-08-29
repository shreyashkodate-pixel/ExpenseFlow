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

export async function apiGet<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
    cache: 'no-store',
  });

  return handleResponse<T>(response);
}

export async function apiPost<T, B = unknown>(path: string, body: B): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(body),
  });

  return handleResponse<T>(response);
}

export async function apiPut<T, B = unknown>(path: string, body: B): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(body),
  });

  return handleResponse<T>(response);
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

  const response = await fetch(url.toString(), {
    method: 'DELETE',
    headers: {
      'Accept': 'application/json',
    },
  });

  return handleResponse<T>(response);
}

export async function downloadFile(path: string, params?: Record<string, unknown>, fallbackFilename = 'export'): Promise<void> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    cache: 'no-store',
  });

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
