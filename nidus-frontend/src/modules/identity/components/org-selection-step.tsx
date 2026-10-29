"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Building2 } from "lucide-react";

import { Button } from "@/shared/ui/button";
import { UserOrganizationSummary } from "../types/auth";
import { selectOrganizationAction } from "../actions/auth";

interface OrgSelectionStepProps {
  organizations: UserOrganizationSummary[];
  preAuthToken: string;
  onComplete: () => void;
  onError: (message: string | null) => void;
}

export function OrgSelectionStep({
  organizations,
  preAuthToken,
  onComplete,
  onError,
}: OrgSelectionStepProps) {
  const t = useTranslations("OrganizationSwitcher");
  const [isPending, startTransition] = React.useTransition();

  function handleSelect(organizationId: string) {
    startTransition(async () => {
      const result = await selectOrganizationAction(
        preAuthToken,
        organizationId,
      );
      if (result.status === "success") {
        onComplete();
      } else {
        onError(result.message);
      }
    });
  }

  return (
    <div className="space-y-4">
      <div className="space-y-1 text-center">
        <h3 className="text-lg font-semibold tracking-tight">{t("pickTitle")}</h3>
        <p className="text-sm text-muted-foreground">{t("pickDescription")}</p>
      </div>
      <div className="space-y-2">
        {organizations.map((org) => (
          <Button
            key={org.organization_id}
            type="button"
            variant="outline"
            className="h-auto w-full justify-start gap-3 px-4 py-3"
            disabled={isPending}
            onClick={() => handleSelect(org.organization_id)}
          >
            <Building2 className="size-4 shrink-0 text-primary" />
            <div className="flex min-w-0 flex-col items-start text-left">
              <span className="truncate font-medium">{org.name}</span>
              <span className="truncate text-xs capitalize text-muted-foreground">
                {org.role_name}
              </span>
            </div>
          </Button>
        ))}
      </div>
    </div>
  );
}
