"use client";

import { Link } from "@/core/i18n/routing";
import { usePathname } from "next/navigation";
import { cn } from "@/shared/lib/utils";
import { useTranslations } from "next-intl";

export function MainNav({ className }: React.HTMLAttributes<HTMLElement>) {
  const pathname = usePathname();
  const t = useTranslations("MainNav");

  return (
    <nav className={cn("flex items-center space-x-4 lg:space-x-6", className)}>
      <Link
        href="/dashboard"
        className={cn(
          "text-sm font-medium transition-colors hover:text-primary",
          pathname.includes("/dashboard")
            ? "text-primary"
            : "text-muted-foreground",
        )}
      >
        {t("dashboard")}
      </Link>
    </nav>
  );
}
