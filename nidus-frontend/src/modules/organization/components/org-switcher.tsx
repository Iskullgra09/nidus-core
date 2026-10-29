"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/core/i18n/routing";
import { toast } from "sonner";
import { Check, ChevronDown } from "lucide-react";

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
import { cn } from "@/core/lib/utils";

interface OrgSwitcherProps {
  organizations: UserOrganizationSummary[];
  currentOrganizationId: string;
  fallbackName?: string;
}

export function OrgSwitcher({
  organizations,
  currentOrganizationId,
  fallbackName,
}: OrgSwitcherProps) {
  const t = useTranslations("OrganizationSwitcher");
  const router = useRouter();
  const [isPending, startTransition] = React.useTransition();

  const currentOrg = organizations.find(
    (org) => org.organization_id === currentOrganizationId,
  );
  const displayName = currentOrg?.name ?? fallbackName;

  if (!displayName) {
    return null;
  }

  if (organizations.length <= 1) {
    return (
      <span className="truncate text-sm font-medium text-foreground/90 max-w-40">
        {displayName}
      </span>
    );
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
          variant="ghost"
          size="sm"
          className={cn(
            "h-8 max-w-48 gap-1 px-2 text-sm font-medium text-foreground/90",
            "hover:bg-muted/50 hover:text-foreground",
            "focus-visible:ring-1",
          )}
          disabled={isPending}
        >
          <span className="truncate">{currentOrg!.name}</span>
          <ChevronDown className="size-3.5 shrink-0 text-muted-foreground" />
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
