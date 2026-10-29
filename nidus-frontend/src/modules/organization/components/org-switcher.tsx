"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/core/i18n/routing";
import { toast } from "sonner";
import { Building2, Check, ChevronsUpDown } from "lucide-react";

import { Button } from "@/shared/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { UserOrganizationSummary } from "@/modules/identity/types/auth";
import { switchOrganizationAction } from "@/modules/identity/actions/auth";

interface OrgSwitcherProps {
  organizations: UserOrganizationSummary[];
  currentOrganizationId: string;
}

export function OrgSwitcher({
  organizations,
  currentOrganizationId,
}: OrgSwitcherProps) {
  const t = useTranslations("OrganizationSwitcher");
  const router = useRouter();
  const [isPending, startTransition] = React.useTransition();

  const currentOrg = organizations.find(
    (org) => org.organization_id === currentOrganizationId,
  );

  if (organizations.length <= 1 || !currentOrg) {
    return null;
  }

  async function handleSwitch(organizationId: string) {
    if (organizationId === currentOrganizationId || isPending) return;

    startTransition(async () => {
      const result = await switchOrganizationAction(organizationId);
      if (result.status === "success") {
        toast.success(result.message);
        router.refresh();
      } else {
        toast.error(result.message);
      }
    });
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-1.5 border-border/60 bg-background/50 px-2.5 text-xs font-medium"
          disabled={isPending}
        >
          <Building2 className="size-3.5 text-muted-foreground" />
          <span className="max-w-28 truncate">{currentOrg.name}</span>
          <ChevronsUpDown className="size-3 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        <DropdownMenuLabel>{t("title")}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {organizations.map((org) => (
          <DropdownMenuItem
            key={org.organization_id}
            className="cursor-pointer"
            onClick={() => handleSwitch(org.organization_id)}
          >
            <div className="flex w-full items-center justify-between gap-2">
              <div className="flex min-w-0 flex-col">
                <span className="truncate text-sm font-medium">{org.name}</span>
                <span className="truncate text-xs capitalize text-muted-foreground">
                  {org.role_name}
                </span>
              </div>
              {org.organization_id === currentOrganizationId && (
                <Check className="size-4 shrink-0 text-primary" />
              )}
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
