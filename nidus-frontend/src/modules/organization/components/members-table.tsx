"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { MoreHorizontal, ShieldCheck, UserMinus, UserCog } from "lucide-react";
import { toast } from "sonner";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/table";
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

import { OrganizationMember } from "../types/members";
import { updateMemberRoleAction, removeMemberAction } from "../actions/members";
import { RoleResponse } from "@/modules/identity/types/roles";

interface MembersTableProps {
  members: OrganizationMember[];
  roles: RoleResponse[];
  currentUserId: string;
}

export function MembersTable({
  members = [],
  roles = [],
  currentUserId,
}: MembersTableProps) {
  const t = useTranslations("SettingsMembers");

  const getRoleIdByName = (name: string) => {
    if (!Array.isArray(roles)) return undefined;
    return roles.find((r) => r.name.toLowerCase() === name.toLowerCase())?.id;
  };

  if (!Array.isArray(members) || members.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground italic">
        {t("noMembersFound") || "No members found in this organization."}
      </div>
    );
  }

  const handleRoleChange = async (memberId: string, roleName: string) => {
    const roleId = getRoleIdByName(roleName);

    if (!roleId) {
      toast.error("Role UUID not found");
      return;
    }

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

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{t("tableHeaderName")}</TableHead>
          <TableHead>{t("tableHeaderRole")}</TableHead>
          <TableHead className="text-right">
            {t("tableHeaderActions") || "Actions"}
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {members.map((member) => (
          <TableRow key={member.id}>
            <TableCell>
              <div className="flex flex-col">
                <span className="font-medium">{member.full_name || "---"}</span>
                <span className="text-xs text-muted-foreground">
                  {member.email}
                </span>
              </div>
            </TableCell>
            <TableCell>
              <Badge
                variant={member.role_name === "owner" ? "default" : "secondary"}
                className="capitalize"
              >
                {t(
                  `role${member.role_name.charAt(0).toUpperCase() + member.role_name.slice(1)}`,
                )}
              </Badge>
            </TableCell>
            <TableCell className="text-right">
              {member.user_id !== currentUserId &&
                member.role_name !== "owner" && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>
                        {t("tableHeaderActions") || "Actions"}
                      </DropdownMenuLabel>

                      <DropdownMenuSub>
                        <DropdownMenuSubTrigger>
                          <UserCog className="mr-2 h-4 w-4" />
                          <span>{t("changeRole") || "Change Role"}</span>
                        </DropdownMenuSubTrigger>
                        <DropdownMenuSubContent>
                          <DropdownMenuItem
                            onClick={() => handleRoleChange(member.id, "admin")}
                          >
                            <ShieldCheck className="mr-2 h-4 w-4" />
                            <span>{t("roleAdmin")}</span>
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() =>
                              handleRoleChange(member.id, "member")
                            }
                          >
                            <span>{t("roleMember")}</span>
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() =>
                              handleRoleChange(member.id, "viewer")
                            }
                          >
                            <span>{t("roleViewer")}</span>
                          </DropdownMenuItem>
                        </DropdownMenuSubContent>
                      </DropdownMenuSub>

                      <DropdownMenuSeparator />

                      <DropdownMenuItem
                        className="text-destructive focus:text-destructive"
                        onClick={() => handleRemove(member.id)}
                      >
                        <UserMinus className="mr-2 h-4 w-4" />
                        <span>{t("removeMember") || "Remove"}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
