export enum NidusScope {
  SUPERADMIN = "*",
  ORG_READ = "org:read",
  ORG_UPDATE = "org:update",
  ORG_DELETE = "org:delete",
  MEMBER_READ = "identity:member:read",
  MEMBER_WRITE = "identity:member:write",
  MEMBER_INVITE = "identity:member:invite",
  ROLE_READ = "identity:role:read",
  ROLE_WRITE = "identity:role:write",
}

/** Assignable scopes mirrored from backend NidusScope (excluding SUPERADMIN). */
export const ASSIGNABLE_SCOPES = Object.values(NidusScope).filter(
  (scope) => scope !== NidusScope.SUPERADMIN,
);
