export interface RoleResponse {
  id: string;
  name: string;
  description: string | null;
  scopes: string[];
}
