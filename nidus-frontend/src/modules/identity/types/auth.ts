import { ApiStatus } from "@/core/types/api";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthActionResponse {
  status: ApiStatus;
  message: string | null;
}
