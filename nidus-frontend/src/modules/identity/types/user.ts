import { OrganizationResponse } from "../../organization/types/organization";

export interface UserPreferences {
  language: "es" | "en";
  theme: "light" | "dark" | "system";
}

export interface UserProfileResponse {
  id: string;
  email: string;
  full_name: string | null;
  preferences: UserPreferences;
  is_superuser: boolean;
  role_name: string;
  scopes: string[];
  organization: OrganizationResponse;
}

export interface UpdateProfilePayload {
  full_name?: string | null;
  preferences?: UserPreferences;
}

export interface UpdateProfileFormData {
  fullName: string;
  language: "es" | "en";
  theme: "light" | "dark" | "system";
}

export interface MemberResponse {
  id: string;
  email: string;
  role_name: string;
  joined_at: string;
}

/**
 * Mirroring the Pydantic MemberFilter exactly.
 * Use 'role' as the alias for 'role_name' as defined in the backend.
 */
export interface MemberFilter {
  role?: string;
  email__contains?: string;
  is_active?: boolean;
  limit?: number;
  cursor?: string;
}

export interface ChangePasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}
