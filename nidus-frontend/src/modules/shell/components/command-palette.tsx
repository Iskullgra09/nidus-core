"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import {
  LayoutDashboard,
  LogOut,
  Shield,
  Users,
  Building2,
  UserRound,
  KeyRound,
  Search,
  ScrollText,
} from "lucide-react";

import { useRouter } from "@/core/i18n/routing";
import { useAuth } from "@/modules/identity/contexts/auth-context";
import { logoutAction } from "@/modules/identity/actions/auth";
import { hasScope } from "@/shared/access/permissions";
import { NidusScope } from "@/shared/access/scopes";
import { Button } from "@/shared/ui/button";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/shared/ui/command";
import { cn } from "@/core/lib/utils";

type CommandPaletteVariant = "bar" | "icon";

interface CommandPaletteProps {
  variant?: CommandPaletteVariant;
}

export function CommandPalette({ variant = "bar" }: CommandPaletteProps) {
  const [open, setOpen] = React.useState(false);
  const router = useRouter();
  const { user } = useAuth();
  const t = useTranslations("CommandPalette");

  React.useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === "k" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const run = React.useCallback(
    (href: string) => {
      setOpen(false);
      router.push(href);
    },
    [router],
  );

  const canManageMembers = hasScope(user, NidusScope.MEMBER_READ);
  const canManageRoles = hasScope(user, NidusScope.ROLE_READ);
  const canReadAudit = hasScope(user, NidusScope.AUDIT_READ);

  return (
    <>
      {variant === "bar" ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className={cn(
            "group flex h-9 w-full items-center gap-2 rounded-lg border border-border/50",
            "bg-muted/30 px-3 text-left text-sm text-muted-foreground",
            "shadow-none transition-colors",
            "hover:border-border hover:bg-muted/50 hover:text-foreground/80",
            "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
          )}
        >
          <Search className="size-4 shrink-0 opacity-70" />
          <span className="flex-1 truncate">{t("trigger")}</span>
          <kbd className="pointer-events-none hidden h-5 select-none items-center gap-0.5 rounded border border-border/60 bg-background/80 px-1.5 font-mono text-[10px] font-medium text-muted-foreground sm:inline-flex">
            ⌘K
          </kbd>
        </button>
      ) : (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={() => setOpen(true)}
          aria-label={t("trigger")}
        >
          <Search className="size-4" />
        </Button>
      )}

      <CommandDialog
        open={open}
        onOpenChange={setOpen}
        title={t("title")}
        description={t("description")}
      >
        <CommandInput placeholder={t("placeholder")} />
        <CommandList>
          <CommandEmpty>{t("empty")}</CommandEmpty>
          <CommandGroup heading={t("groupNavigate")}>
            <CommandItem
              value="dashboard control centro /dashboard"
              onSelect={() => run("/dashboard")}
            >
              <LayoutDashboard />
              {t("dashboard")}
            </CommandItem>
            <CommandItem
              value="profile perfil settings /settings/profile"
              onSelect={() => run("/settings/profile")}
            >
              <UserRound />
              {t("profile")}
            </CommandItem>
            <CommandItem
              value="security seguridad password /settings/security"
              onSelect={() => run("/settings/security")}
            >
              <KeyRound />
              {t("security")}
            </CommandItem>
            <CommandItem
              value="organization organizacion workspace /settings/organization"
              onSelect={() => run("/settings/organization")}
            >
              <Building2 />
              {t("organization")}
            </CommandItem>
            {canManageMembers && (
              <CommandItem
                value="members miembros team invite /settings/organization/members"
                onSelect={() => run("/settings/organization/members")}
              >
                <Users />
                {t("members")}
              </CommandItem>
            )}
            {canManageRoles && (
              <CommandItem
                value="roles permisos permissions scopes /settings/organization/roles"
                onSelect={() => run("/settings/organization/roles")}
              >
                <Shield />
                {t("roles")}
              </CommandItem>
            )}
            {canReadAudit && (
              <CommandItem
                value="audit auditoria logs activity /settings/organization/audit"
                onSelect={() => run("/settings/organization/audit")}
              >
                <ScrollText />
                {t("audit")}
              </CommandItem>
            )}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading={t("groupAccount")}>
            <CommandItem
              value="logout cerrar sesion sign out"
              onSelect={() => {
                setOpen(false);
                void logoutAction();
              }}
            >
              <LogOut />
              {t("logout")}
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}
