import * as React from "react";
import { LanguageSwitcher } from "@/core/i18n/components/language-switcher";
import { UserDropdown } from "@/modules/identity/components/user-dropdown";
import { OrgSwitcher } from "@/modules/organization/components/org-switcher";
import { persistLanguageAction } from "@/modules/identity/actions/user";
import { UserOrganizationSummary } from "@/modules/identity/types/auth";
import { MainNav } from "@/shared/components/layout/main-nav";
import { UserProfileResponse } from "@/modules/identity/types/user";
import { CommandPalette } from "@/modules/shell/components/command-palette";

interface TopBarProps {
  user: UserProfileResponse;
  organizations: UserOrganizationSummary[];
}

export function TopBar({ user, organizations }: TopBarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl supports-backdrop-filter:bg-background/70">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="text-primary text-lg font-semibold tracking-tight shrink-0">
            NIDUS
          </span>
          <span
            aria-hidden
            className="hidden h-4 w-px bg-border/80 sm:block shrink-0"
          />
          <OrgSwitcher
            organizations={organizations}
            currentOrganizationId={user.organization.id}
            fallbackName={user.organization.name}
          />
          <span className="hidden sm:inline-flex rounded-md bg-muted/60 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground shrink-0">
            {user.role_name}
          </span>
        </div>

        <MainNav className="hidden md:flex ml-2" />

        <div className="flex-1" />

        <div className="flex items-center gap-2">
          <div className="hidden sm:block w-56 lg:w-64">
            <CommandPalette variant="bar" />
          </div>
          <div className="sm:hidden">
            <CommandPalette variant="icon" />
          </div>
          <LanguageSwitcher onLocaleChange={persistLanguageAction} />
          <UserDropdown user={user} />
        </div>
      </div>
    </header>
  );
}
