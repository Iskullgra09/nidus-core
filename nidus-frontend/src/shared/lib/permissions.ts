import { UserProfileResponse } from "@/modules/identity/types/user";
import { NidusScope } from "@/modules/identity/types/scopes";

type UserWithScopes = Pick<UserProfileResponse, "scopes" | "is_superuser">;

export function hasScope(
  user: UserWithScopes | null,
  requiredScope: NidusScope | string,
): boolean {
  if (!user) return false;

  if (user.is_superuser || user.scopes.includes(NidusScope.SUPERADMIN))
    return true;

  if (user.scopes.includes(requiredScope)) return true;
  if (typeof requiredScope === "string" && requiredScope.endsWith(":read")) {
    const resource = requiredScope.replace(":read", "");
    return user.scopes.includes(`${resource}:write`);
  }

  return false;
}
