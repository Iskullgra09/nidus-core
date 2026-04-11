import { OrganizationMember } from "./members";

export interface OrganizationResponse {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
  members: OrganizationMember[];
}

export interface OnboardingResponse {
  organization_id: string;
  user_id: string;
}

export interface OrganizationCreate {
  organization_name: string;
  organization_slug: string;
  admin_email: string;
  password: string;
}
