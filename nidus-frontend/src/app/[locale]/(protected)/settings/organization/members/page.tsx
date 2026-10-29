import * as React from "react";
import { getTranslations } from "next-intl/server";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import { getOrganizationMembersPage } from "@/modules/organization/actions/members";
import { getAvailableRoles } from "@/modules/access/actions/roles";
import { getPendingInvitations } from "@/modules/access/actions/invitations";
import { InviteMemberButton } from "@/modules/organization/components/invite-member-button";
import { MembersWorkspace } from "@/modules/organization/components/members-workspace";

const PAGE_SIZE = 10;

type SearchParams = Promise<{
  q?: string;
  cursor?: string;
  tab?: string;
}>;

export default async function MembersPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const t = await getTranslations("SettingsMembers");
  const user = await getCurrentUser();
  const params = await searchParams;

  if (!user) return null;

  const tab = params.tab === "invitations" ? "invitations" : "members";
  const q = params.q?.trim() ?? "";
  const cursor = params.cursor ?? null;

  const [membersPage, roles, invitations] = await Promise.all([
    getOrganizationMembersPage({ q, cursor, limit: PAGE_SIZE }),
    getAvailableRoles(),
    getPendingInvitations(),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-medium">{t("title")}</h3>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>
        <InviteMemberButton roles={roles} />
      </div>

      <React.Suspense fallback={null}>
        <MembersWorkspace
          members={membersPage.items}
          pageInfo={membersPage.page_info}
          searchQuery={q}
          roles={roles}
          invitations={invitations}
          currentUserId={user.id}
          initialTab={tab}
          pageSize={PAGE_SIZE}
        />
      </React.Suspense>
    </div>
  );
}
