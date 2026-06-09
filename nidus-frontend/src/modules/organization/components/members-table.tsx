"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { MoreHorizontal, UserMinus, UserCog } from "lucide-react";
import { toast } from "sonner";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";

import { MemberResponse } from "../types/members";
import { updateMemberRoleAction, removeMemberAction } from "../actions/members";
import { RoleResponse } from "@/modules/identity/types/roles";
import { CanAccess } from "@/shared/components/auth/can-access";
import { NidusScope } from "@/modules/identity/types/scopes";
import { DataTable, ColumnDef } from "@/shared/components/layout/data-table";

interface MembersTableProps {
  members: MemberResponse[];
  roles: RoleResponse[];
  currentUserId: string;
}

export function MembersTable({
  members = [],
  roles = [],
  currentUserId,
}: MembersTableProps) {
  const t = useTranslations("SettingsMembers");

  const assignableRoles = roles.filter(
    (role) => role.name.toLowerCase() !== "owner",
  );

  const getRoleLabel = (roleName: string) => {
    const normalized = roleName.toLowerCase();
    if (normalized === "owner") return t("roleOwner");
    if (normalized === "admin") return t("roleAdmin");
    if (normalized === "member") return t("roleMember");
    if (normalized === "viewer") return t("roleViewer");
    return roleName;
  };

  const handleRoleChange = async (memberId: string, roleId: string) => {
    const res = await updateMemberRoleAction(memberId, roleId);
    if (res.status === "success") {
      toast.success(res.message);
    } else {
      toast.error(res.message);
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!confirm(t("removeConfirm") || "Are you sure?")) return;
    const res = await removeMemberAction(memberId);
    if (res.status === "success") {
      toast.success(res.message);
    } else {
      toast.error(res.message);
    }
  };

  const columns: ColumnDef<MemberResponse>[] = [
    {
      header: t("tableHeaderName"),
      cell: (member) => (
        <div className="flex flex-col space-y-0.5">
          <span className="font-semibold text-foreground tracking-tight">
            {member.full_name || "---"}
          </span>
          <span className="text-xs text-muted-foreground">{member.email}</span>
        </div>
      ),
    },
    {
      header: t("tableHeaderRole"),
      cell: (member) => (
        <Badge
          variant={
            member.role_name.toLowerCase() === "owner" ? "default" : "secondary"
          }
          className="capitalize font-medium shadow-none"
        >
          {getRoleLabel(member.role_name)}
        </Badge>
      ),
    },
    {
      header: t("tableHeaderActions") || "Actions",
      className: "text-right",
      cell: (member) => (
        <CanAccess scope={NidusScope.MEMBER_WRITE}>
          {member.user_id !== currentUserId &&
            member.role_name.toLowerCase() !== "owner" && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0 rounded-md">
                    <MoreHorizontal className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuLabel>
                    {t("tableHeaderActions")}
                  </DropdownMenuLabel>
                  <DropdownMenuSub>
                    <DropdownMenuSubTrigger>
                      <UserCog className="mr-2 h-4 w-4" />
                      <span>{t("changeRole")}</span>
                    </DropdownMenuSubTrigger>
                    <DropdownMenuSubContent>
                      {assignableRoles.map((role) => (
                        <DropdownMenuItem
                          key={role.id}
                          onClick={() => handleRoleChange(member.id, role.id)}
                        >
                          <span className="capitalize">{getRoleLabel(role.name)}</span>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuSubContent>
                  </DropdownMenuSub>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer"
                    onClick={() => handleRemove(member.id)}
                  >
                    <UserMinus className="mr-2 h-4 w-4" />
                    <span className="font-medium">{t("removeMember")}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
        </CanAccess>
      ),
    },
  ];

  return (
    <DataTable
      mode="client"
      data={members}
      columns={columns}
      searchKey="email"
      searchPlaceholder={t("searchPlaceholder")}
      emptyMessage={t("noMembersFound")}
      pageSize={5}
      paginationText={(start, end, total) =>
        t("paginationInfo", { start, end, total })
      }
    />
  );
}
