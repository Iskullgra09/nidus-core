import * as React from "react";
import { LanguageSwitcher } from "@/core/i18n/components/language-switcher";
import { ThemeToggle } from "@/shared/components/layout/theme-toggle";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="absolute top-4 right-4 z-20 flex items-center gap-4">
        <LanguageSwitcher />
        <ThemeToggle />
      </div>
      <div className="absolute inset-0 z-0 opacity-30 pointer-events-none bg-[radial-gradient(circle_at_center,var(--color-primary)_0%,transparent_70%)] blur-3xl" />
      <main className="z-10 w-full max-w-md">{children}</main>
    </div>
  );
}
