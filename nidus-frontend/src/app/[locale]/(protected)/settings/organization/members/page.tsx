import * as React from "react";
import { getTranslations } from "next-intl/server";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import {
  getOrganizationMembers,
  getAvailableRoles,
} from "@/modules/organization/actions/members";
import { Button } from "@/shared/ui/button";
import { PlusIcon } from "lucide-react";
import { MembersTable } from "@/modules/organization/components/members-table";

export default async function MembersPage() {
  const t = await getTranslations("SettingsMembers");
  const user = (await getCurrentUser())!;

  const [membersData, rolesData] = await Promise.all([
    getOrganizationMembers(),
    getAvailableRoles(),
  ]);

  const members = JSON.parse(JSON.stringify(membersData ?? []));
  const roles = JSON.parse(JSON.stringify(rolesData ?? []));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">{t("title")}</h3>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>
        <Button size="sm">
          <PlusIcon className="mr-2 h-4 w-4" />
          {t("inviteButton")}
        </Button>
      </div>

      <div className="border rounded-md bg-card shadow-sm">
        <MembersTable members={members} roles={roles} currentUserId={user.id} />
      </div>
    </div>
  );
}
