import { OrganizationResponse } from "../../organization/types/organization";

export interface UserPreferences {
  language: "es" | "en";
  theme: "light" | "dark" | "system";
}

export interface UserProfileResponse {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  preferences: UserPreferences;
  is_superuser: boolean;
  role_name: string;
  scopes: string[];
  organization: OrganizationResponse;
}

export interface UpdateProfilePayload {
  full_name?: string | null;
  preferences?: Partial<UserPreferences>;
}

export interface UpdateProfileFormData {
  fullName?: string;
  language: "es" | "en";
  theme: "light" | "dark" | "system";
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
