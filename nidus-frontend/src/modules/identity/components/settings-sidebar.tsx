"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { Link } from "@/core/i18n/routing";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/lib/utils";
import { buttonVariants } from "@/shared/ui/button";

type SidebarNavProps = React.HTMLAttributes<HTMLElement>;

type SettingsPath =
  | "/settings/profile"
  | "/settings/security"
  | "/settings/organization"
  | "/settings/organization/members";

interface NavItem {
  title: string;
  href: SettingsPath;
}

const SidebarNavItem = ({
  item,
  isActive,
}: {
  item: NavItem;
  isActive: boolean;
}) => (
  <Link
    href={item.href}
    className={cn(
      buttonVariants({ variant: "ghost" }),
      isActive
        ? "bg-primary/10 text-primary font-bold hover:bg-primary/20"
        : "text-muted-foreground hover:bg-muted hover:text-foreground",
      "justify-start w-full transition-all duration-200",
    )}
  >
    {item.title}
  </Link>
);

export function SettingsSidebar({ className, ...props }: SidebarNavProps) {
  const pathname = usePathname();
  const t = useTranslations("SettingsLayout");

  const sidebarGroups = [
    {
      label: "Personal",
      items: [
        { title: t("navProfile"), href: "/settings/profile" },
        { title: t("navSecurity"), href: "/settings/security" },
      ] as NavItem[],
    },
    {
      label: "Workspace",
      items: [
        { title: t("navOrganization"), href: "/settings/organization" },
        { title: t("navMembers"), href: "/settings/organization/members" },
      ] as NavItem[],
    },
  ];

  return (
    <nav className={cn("flex flex-col space-y-8", className)} {...props}>
      {sidebarGroups.map((group) => (
        <div key={group.label} className="flex flex-col space-y-2">
          <h4 className="px-4 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground/50">
            {group.label}
          </h4>
          <div className="flex flex-col space-y-1">
            {group.items.map((item) => (
              <SidebarNavItem
                key={item.href}
                item={item}
                isActive={pathname === item.href}
              />
            ))}
          </div>
        </div>
      ))}
    </nav>
  );
}
