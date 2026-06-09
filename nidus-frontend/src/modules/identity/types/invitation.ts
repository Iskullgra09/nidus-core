export interface InvitationResponse {
  id: string;
  email: string;
  role_id: string;
  role_name?: string | null;
  expires_at: string;
  is_accepted: boolean;
}

export interface InvitationAcceptedResponse {
  user_id: string;
  organization_id: string;
  role_id: string;
}

export interface InvitationPayload {
  email: string;
  role_id: string;
}
