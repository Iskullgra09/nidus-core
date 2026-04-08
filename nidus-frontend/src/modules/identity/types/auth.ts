import { ApiStatus } from "@/core/types/api";

export interface LoginRequest {
  email: string;
  password: string;
}

export type LoginFormData = LoginRequest;

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthActionResponse {
  status: ApiStatus;
  message: string | null;
}

export interface RegisterFormData {
  organization_name: string;
  email: string;
  password: string;
}

export interface OnboardingPayload {
  organization_name: string;
  organization_slug: string;
  admin_email: string;
  password: string;
}

export interface AuthActionResponse {
  status: ApiStatus;
  message: string | null;
}

export interface ForgotPasswordFormData {
  email: string;
}

export interface ResetPasswordFormData {
  password: string;
  confirmPassword: string;
}

export interface ResetPasswordPayload {
  token: string;
  new_password: string;
}
