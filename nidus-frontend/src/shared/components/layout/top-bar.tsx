import * as React from "react";
import { LanguageSwitcher } from "@/core/i18n/components/language-switcher";
import { UserDropdown } from "@/modules/identity/components/user-dropdown";
import { OrgSwitcher } from "@/modules/organization/components/org-switcher";
import { UserOrganizationSummary } from "@/modules/identity/types/auth";
import { MainNav } from "./main-nav";
import { UserProfileResponse } from "@/modules/identity/types/user";

interface TopBarProps {
  user: UserProfileResponse;
  organizations: UserOrganizationSummary[];
}

export function TopBar({ user, organizations }: TopBarProps) {
  return (
    <header className="sticky top-0 z-50 flex h-16 items-center border-b border-border/50 bg-background/95 px-6 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="flex items-center gap-3 font-bold mr-8 min-w-0">
        <span className="text-primary text-xl tracking-tighter shrink-0">
          NIDUS
        </span>
        <span className="text-muted-foreground/50 shrink-0">/</span>
        <OrgSwitcher
          organizations={organizations}
          currentOrganizationId={user.organization.id}
        />
        {organizations.length <= 1 && (
          <span className="text-sm font-medium truncate max-w-30">
            {user.organization.name}
          </span>
        )}
        <span className="ml-1 rounded-full bg-secondary px-2 py-0.5 text-[10px] uppercase text-secondary-foreground shrink-0">
          {user.role_name}
        </span>
      </div>
      <MainNav className="hidden md:flex" />
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        <LanguageSwitcher />
        <UserDropdown user={user} />
      </div>
    </header>
  );
}
