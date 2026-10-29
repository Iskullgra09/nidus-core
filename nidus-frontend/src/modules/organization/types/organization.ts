export interface OrganizationResponse {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
}

export interface OnboardingResponse {
  organization_id: string;
  user_id: string;
}
