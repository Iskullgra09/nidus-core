export enum NidusScope {
  SUPERADMIN = "*",
  ORG_READ = "org:read",
  ORG_UPDATE = "org:update",
  MEMBER_READ = "identity:member:read",
  MEMBER_WRITE = "identity:member:write",
  MEMBER_INVITE = "identity:member:invite",
  ROLE_READ = "identity:role:read",
  ROLE_WRITE = "identity:role:write",
}
