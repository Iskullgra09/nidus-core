"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/core/i18n/routing";
import { useSearchParams } from "next/navigation";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { MembersTable } from "@/modules/organization/components/members-table";
import { PendingInvitationsTable } from "@/modules/organization/components/pending-invitations-table";
import { MemberResponse } from "@/modules/organization/types/members";
import { RoleResponse } from "@/modules/access/types/roles";
import { InvitationResponse } from "@/modules/access/types/invitation";
import { PageInfo } from "@/core/types/api";

type MembersTab = "members" | "invitations";

interface MembersWorkspaceProps {
  members: MemberResponse[];
  pageInfo: PageInfo;
  searchQuery: string;
  roles: RoleResponse[];
  invitations: InvitationResponse[];
  currentUserId: string;
  initialTab: MembersTab;
  pageSize: number;
}

export function MembersWorkspace({
  members,
  pageInfo,
  searchQuery,
  roles,
  invitations,
  currentUserId,
  initialTab,
  pageSize,
}: MembersWorkspaceProps) {
  const t = useTranslations("SettingsMembers");
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const tab = (searchParams.get("tab") as MembersTab) || initialTab;

  const onTabChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", value);
    if (value !== "members") {
      params.delete("cursor");
      params.delete("q");
    }
    router.replace(`${pathname}?${params.toString()}`);
  };

  return (
    <Tabs value={tab} onValueChange={onTabChange} className="space-y-4">
      <TabsList variant="line">
        <TabsTrigger value="members">{t("tabMembers")}</TabsTrigger>
        <TabsTrigger value="invitations">{t("tabInvitations")}</TabsTrigger>
      </TabsList>

      <TabsContent value="members" className="space-y-4">
        <div className="rounded-md border bg-card shadow-sm p-4">
          <MembersTable
            members={members}
            roles={roles}
            currentUserId={currentUserId}
            pageInfo={pageInfo}
            searchQuery={searchQuery}
            pageSize={pageSize}
          />
        </div>
      </TabsContent>

      <TabsContent value="invitations" className="space-y-4">
        <PendingInvitationsTable invitations={invitations} />
      </TabsContent>
    </Tabs>
  );
}
