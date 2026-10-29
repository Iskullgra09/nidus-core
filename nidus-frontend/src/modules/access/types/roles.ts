export interface RoleResponse {
  id: string;
  name: string;
  description: string | null;
  scopes: string[];
  is_system: boolean;
}

export interface RolePayload {
  name: string;
  description?: string | null;
  scopes: string[];
}
