import { OrganizationResponse } from "../../organization/types/organization";

export interface UserProfileResponse {
  id: string;
  email: string;
  is_superuser: boolean;
  role_name: string;
  scopes: string[];
  organization: OrganizationResponse;
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
