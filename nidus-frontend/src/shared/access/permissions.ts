import { NidusScope } from "@/shared/access/scopes";

type UserWithScopes = {
  scopes: string[];
  is_superuser: boolean;
};

/**
 * Mirrors backend NidusScope.get_implied_scopes().
 * write → read; invite → read.
 */
export function getImpliedScopes(scope: string): Set<string> {
  const permissions = new Set<string>([scope]);
  if (scope.includes(":write")) {
    permissions.add(scope.replace(":write", ":read"));
  }
  if (scope.includes(":invite")) {
    permissions.add(scope.replace(":invite", ":read"));
  }
  return permissions;
}

/**
 * Mirrors backend NidusScope.grants_access().
 * Single source of truth for UI + Edge proxy authorization.
 */
export function grantsAccess(
  userScopes: Iterable<string>,
  required: string,
): boolean {
  const scopeSet = new Set(userScopes);

  if (scopeSet.has(NidusScope.SUPERADMIN)) return true;
  if (scopeSet.has(required)) return true;

  for (const held of scopeSet) {
    if (getImpliedScopes(held).has(required)) return true;
  }

  return false;
}

export function hasScope(
  user: UserWithScopes | null,
  requiredScope: NidusScope | string,
): boolean {
  if (!user) return false;
  if (user.is_superuser) return true;
  return grantsAccess(user.scopes, requiredScope);
}
