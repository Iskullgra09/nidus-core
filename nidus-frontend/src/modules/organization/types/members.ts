export type MemberRole = "owner" | "admin" | "member" | "viewer";

export interface MemberResponse {
  id: string;
  user_id: string;
  full_name: string | null;
  email: string;
  role_name: string;
  joined_at: string;
}

export interface InviteMemberPayload {
  email: string;
  role_id: string;
}
