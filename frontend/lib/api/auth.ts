import { apiGet, apiPost, apiPut, setAccessToken } from './client';
import {
  User,
  TokenResponse,
  LoginCredentials,
  RegisterData,
  GoogleAuthData,
  UserProfileUpdateData,
  ChangePasswordData,
  PasswordResetConfirmData,
  GenericStatusResponse,
  RegistrationResponse,
} from '../../types/auth';

export async function register(data: RegisterData): Promise<RegistrationResponse> {
  const res = await apiPost<RegistrationResponse>('/auth/register', data);
  return res;
}

export async function verifyEmail(token: string): Promise<TokenResponse> {
  const res = await apiPost<TokenResponse>('/auth/verify-email', { token });
  if (res.access_token) {
    setAccessToken(res.access_token);
  }
  return res;
}

export async function resendVerification(email: string): Promise<GenericStatusResponse> {
  return apiPost<GenericStatusResponse>('/auth/resend-verification', { email });
}

export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const res = await apiPost<TokenResponse>('/auth/login', credentials);
  if (res.access_token) {
    setAccessToken(res.access_token);
  }
  return res;
}

export async function googleLogin(data: GoogleAuthData): Promise<TokenResponse> {
  const res = await apiPost<TokenResponse>('/auth/google', data);
  if (res.access_token) {
    setAccessToken(res.access_token);
  }
  return res;
}

export async function refreshToken(): Promise<TokenResponse> {
  const res = await apiPost<TokenResponse>('/auth/refresh', {});
  if (res.access_token) {
    setAccessToken(res.access_token);
  }
  return res;
}

export async function logout(): Promise<void> {
  try {
    await apiPost<void>('/auth/logout', {});
  } finally {
    setAccessToken(null);
  }
}

export async function logoutAll(): Promise<GenericStatusResponse> {
  try {
    return await apiPost<GenericStatusResponse>('/auth/logout-all', {});
  } finally {
    setAccessToken(null);
  }
}

export async function getMe(): Promise<User> {
  return apiGet<User>('/auth/me');
}

export async function updateProfile(data: UserProfileUpdateData): Promise<User> {
  return apiPut<User>('/auth/me', data);
}

export async function changePassword(data: ChangePasswordData): Promise<GenericStatusResponse> {
  return apiPost<GenericStatusResponse>('/auth/change-password', data);
}

export async function forgotPassword(email: string): Promise<GenericStatusResponse> {
  return apiPost<GenericStatusResponse>('/auth/forgot-password', { email });
}

export async function resetPassword(data: PasswordResetConfirmData): Promise<GenericStatusResponse> {
  return apiPost<GenericStatusResponse>('/auth/reset-password', data);
}
