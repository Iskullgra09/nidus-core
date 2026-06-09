"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { MailX } from "lucide-react";

import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import { DataTable, ColumnDef } from "@/shared/components/layout/data-table";
import { CanAccess } from "@/shared/components/auth/can-access";
import { NidusScope } from "@/modules/identity/types/scopes";

import { InvitationResponse } from "@/modules/identity/types/invitation";
import { revokeInvitationAction } from "@/modules/identity/actions/invitations";

interface PendingInvitationsTableProps {
  invitations: InvitationResponse[];
}

export function PendingInvitationsTable({
  invitations,
}: PendingInvitationsTableProps) {
  const t = useTranslations("SettingsMembers");

  const handleRevoke = async (invitationId: string) => {
    if (!confirm(t("revokeConfirm"))) return;

    const result = await revokeInvitationAction(invitationId);
    if (result.status === "success") {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const columns: ColumnDef<InvitationResponse>[] = [
    {
      header: t("tableHeaderName"),
      cell: (invitation) => (
        <div className="flex flex-col space-y-0.5">
          <span className="font-semibold">{invitation.email}</span>
          <span className="text-xs text-muted-foreground">
            {new Date(invitation.expires_at).toLocaleDateString()}
          </span>
        </div>
      ),
    },
    {
      header: t("tableHeaderRole"),
      cell: (invitation) => (
        <Badge variant="secondary" className="capitalize">
          {invitation.role_name || "—"}
        </Badge>
      ),
    },
    {
      header: t("tableHeaderStatus"),
      cell: () => (
        <Badge variant="outline" className="text-amber-600 border-amber-600/30">
          {t("statusPending")}
        </Badge>
      ),
    },
    {
      header: t("tableHeaderActions"),
      className: "text-right",
      cell: (invitation) => (
        <CanAccess scope={NidusScope.MEMBER_INVITE}>
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive hover:text-destructive"
            onClick={() => handleRevoke(invitation.id)}
          >
            <MailX className="mr-2 h-4 w-4" />
            {t("revokeInvite")}
          </Button>
        </CanAccess>
      ),
    },
  ];

  if (invitations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div>
        <h4 className="text-sm font-medium">{t("pendingTitle")}</h4>
        <p className="text-xs text-muted-foreground">{t("pendingDescription")}</p>
      </div>
      <DataTable
        mode="client"
        data={invitations}
        columns={columns}
        searchKey="email"
        searchPlaceholder={t("searchPlaceholder")}
        emptyMessage={t("noPendingInvites")}
        pageSize={5}
      />
    </div>
  );
}
