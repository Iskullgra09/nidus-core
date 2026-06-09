import * as React from "react";
import { getTranslations } from "next-intl/server";
import { getAvailableRoles } from "@/modules/organization/actions/members";
import { getAssignableScopes } from "@/modules/identity/actions/roles";
import { RolesTable } from "@/modules/identity/components/roles-table";

export default async function RolesPage() {
  const t = await getTranslations("SettingsRoles");
  const [roles, scopes] = await Promise.all([
    getAvailableRoles(),
    getAssignableScopes(),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{t("title")}</h3>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      <div className="rounded-md border bg-card p-4 shadow-sm">
        <RolesTable roles={roles} scopes={scopes} />
      </div>
    </div>
  );
}
