import * as React from "react";
import { redirect } from "next/navigation";

import { getCurrentUser } from "@/modules/identity/actions/auth";
import { UserDropdown } from "@/modules/identity/components/user-dropdown";
import { LanguageSwitcher } from "@/core/i18n/components/language-switcher";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const userContext = await getCurrentUser();

  if (!userContext) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-50 flex h-14 items-center border-b border-border/50 bg-background/95 px-4 backdrop-blur supports-backdrop-filter:bg-background/60">
        <div className="flex items-center gap-4 font-bold">
          <span className="text-primary text-lg tracking-tighter">NIDUS</span>
          <span className="text-muted-foreground/50">/</span>
          <span className="text-sm font-medium">
            {userContext.organization.name}
          </span>

          <span className="ml-2 rounded-full bg-secondary px-2 py-0.5 text-[10px] uppercase text-secondary-foreground">
            {userContext.role_name}
          </span>
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-4">
          <LanguageSwitcher />
          <UserDropdown user={userContext} />
        </div>
      </header>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
