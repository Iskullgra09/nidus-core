"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { DataTable, ColumnDef } from "@/shared/components/layout/data-table";
import { CanAccess } from "@/shared/components/auth/can-access";
import { NidusScope } from "@/modules/identity/types/scopes";

import { RoleResponse } from "../types/roles";
import { ScopeResponse } from "../types/scopes-catalog";
import { deleteRoleAction } from "../actions/roles";
import { RoleFormDialog } from "./role-form-dialog";

interface RolesTableProps {
  roles: RoleResponse[];
  scopes: ScopeResponse[];
}

export function RolesTable({ roles, scopes }: RolesTableProps) {
  const t = useTranslations("SettingsRoles");
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [selectedRole, setSelectedRole] = React.useState<RoleResponse | null>(
    null,
  );

  const openCreate = () => {
    setSelectedRole(null);
    setDialogOpen(true);
  };

  const openEdit = (role: RoleResponse) => {
    setSelectedRole(role);
    setDialogOpen(true);
  };

  const handleDelete = async (role: RoleResponse) => {
    if (!confirm(t("deleteConfirm", { name: role.name }))) return;

    const result = await deleteRoleAction(role.id);
    if (result.status === "success") {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const columns: ColumnDef<RoleResponse>[] = [
    {
      header: t("tableName"),
      cell: (role) => (
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{role.name}</span>
            {role.is_system && (
              <Badge variant="outline" className="text-[10px] uppercase">
                {t("systemBadge")}
              </Badge>
            )}
          </div>
          {role.description && (
            <p className="text-xs text-muted-foreground">{role.description}</p>
          )}
        </div>
      ),
    },
    {
      header: t("tablePermissions"),
      cell: (role) => (
        <div className="flex flex-wrap gap-1">
          {role.scopes.slice(0, 3).map((scope) => (
            <Badge key={scope} variant="secondary" className="font-mono text-[10px]">
              {scope}
            </Badge>
          ))}
          {role.scopes.length > 3 && (
            <Badge variant="secondary" className="text-[10px]">
              +{role.scopes.length - 3}
            </Badge>
          )}
        </div>
      ),
    },
    {
      header: t("tableActions"),
      className: "text-right",
      cell: (role) => (
        <CanAccess scope={NidusScope.ROLE_WRITE}>
          {!role.is_system && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => openEdit(role)}>
                  <Pencil className="mr-2 h-4 w-4" />
                  {t("editRole")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="text-destructive focus:text-destructive"
                  onClick={() => handleDelete(role)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t("deleteRole")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </CanAccess>
      ),
    },
  ];

  return (
    <>
      <div className="mb-4 flex justify-end">
        <CanAccess scope={NidusScope.ROLE_WRITE}>
          <Button size="sm" onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            {t("createRoleButton")}
          </Button>
        </CanAccess>
      </div>

      <DataTable
        mode="client"
        data={roles}
        columns={columns}
        searchKey="name"
        searchPlaceholder={t("searchPlaceholder")}
        emptyMessage={t("noRolesFound")}
        pageSize={8}
      />

      <RoleFormDialog
        isOpen={dialogOpen}
        onClose={setDialogOpen}
        scopes={scopes}
        role={selectedRole}
      />
    </>
  );
}
