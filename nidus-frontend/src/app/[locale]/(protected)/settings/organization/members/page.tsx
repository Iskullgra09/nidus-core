import * as React from "react";
import { getTranslations } from "next-intl/server";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import {
  getOrganizationMembers,
  getAvailableRoles,
} from "@/modules/organization/actions/members";
import { getPendingInvitations } from "@/modules/identity/actions/invitations";
import { MembersTable } from "@/modules/organization/components/members-table";
import { PendingInvitationsTable } from "@/modules/organization/components/pending-invitations-table";
import { InviteMemberButton } from "@/modules/organization/components/invite-member-button";

export default async function MembersPage() {
  const t = await getTranslations("SettingsMembers");
  const user = await getCurrentUser();

  if (!user) return null;

  const [members, roles, invitations] = await Promise.all([
    getOrganizationMembers(),
    getAvailableRoles(),
    getPendingInvitations(),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">{t("title")}</h3>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>

        <InviteMemberButton roles={roles} />
      </div>

      <div className="space-y-8">
        <PendingInvitationsTable invitations={invitations} />

        <div className="border rounded-md bg-card shadow-sm">
          <MembersTable members={members} roles={roles} currentUserId={user.id} />
        </div>
      </div>
    </div>
  );
}
