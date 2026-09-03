export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  avatar_url?: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface GoogleAuthData {
  credential: string;
}

export interface UserProfileUpdateData {
  full_name?: string;
  avatar_url?: string;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
}

export interface PasswordResetConfirmData {
  token: string;
  new_password: string;
}

export interface GenericStatusResponse {
  status: string;
  message?: string;
  reset_token?: string | null;
}

export interface RegistrationResponse {
  status: string;
  message: string;
  email: string;
}

export interface SendRegistrationOtpResponse {
  status: string;
  email: string;
  message: string;
}

export interface VerifyRegistrationOtpResponse {
  status: string;
  email: string;
  verification_token: string;
  message: string;
}

export interface CompleteRegistrationData {
  email: string;
  verification_token: string;
  full_name: string;
  password: string;
}

export interface CompleteRegistrationResponse {
  status: string;
  message: string;
  email: string;
}


