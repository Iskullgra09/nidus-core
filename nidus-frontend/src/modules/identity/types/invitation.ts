export interface InvitationResponse {
  id: string;
  email: string;
  role_id: string;
  token: string;
  expires_at: string;
  is_accepted: boolean;
}

export interface InvitationAcceptedResponse {
  user_id: string;
  organization_id: string;
  role_id: string;
}

export interface InvitationCreate {
  email: string;
  role_id: string;
}
