"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useTheme } from "next-themes";
import { Link } from "@/core/i18n/routing";
import { toast } from "sonner";
import { Moon, Sun, Monitor, LogOut, Settings, Building } from "lucide-react";

import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";

import { UserProfileResponse } from "../types/user";
import { logoutAction } from "../actions/auth";
import { updateProfileAction } from "../actions/user";

interface UserDropdownProps {
  user: UserProfileResponse;
}

export function UserDropdown({ user }: UserDropdownProps) {
  const tTop = useTranslations("TopBar");
  const tSet = useTranslations("SettingsProfile");
  const { setTheme } = useTheme();

  const initials = user.full_name
    ? user.full_name.substring(0, 2).toUpperCase()
    : user.email.substring(0, 2).toUpperCase();

  const handleThemeChange = async (newTheme: "light" | "dark" | "system") => {
    setTheme(newTheme);

    const result = await updateProfileAction({
      preferences: {
        theme: newTheme,
        language: user.preferences?.language || "en",
      },
    });

    if (result.status === "error") {
      toast.error(result.message);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative size-8 rounded-full">
          <Avatar className="size-8 border border-border/50">
            <AvatarFallback className="bg-primary/10 text-primary font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {user.full_name || tTop("profile")}
            </p>
            <p className="text-xs leading-none text-muted-foreground truncate">
              {user.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem asChild className="cursor-pointer">
            <Link href="/settings/profile" className="w-full flex items-center">
              <Settings className="mr-2 size-4 text-muted-foreground" />
              {tTop("settings")}
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem
            asChild
            className="cursor-pointer flex items-center"
          >
            <Link
              href="/settings/organization"
              className="w-full flex items-center"
            >
              <Building className="mr-2 size-4 text-muted-foreground" />
              {tTop("orgSettings")}
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuSub>
            <DropdownMenuSubTrigger className="cursor-pointer">
              <Sun className="mr-2 h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-muted-foreground" />
              <Moon className="absolute mr-2 h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-muted-foreground" />
              <span>{tSet("theme")}</span>
            </DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              <DropdownMenuSubContent>
                <DropdownMenuItem
                  onClick={() => handleThemeChange("light")}
                  className="cursor-pointer"
                >
                  <Sun className="mr-2 size-4 text-muted-foreground" />
                  <span>{tSet("themeLight")}</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => handleThemeChange("dark")}
                  className="cursor-pointer"
                >
                  <Moon className="mr-2 size-4 text-muted-foreground" />
                  <span>{tSet("themeDark")}</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => handleThemeChange("system")}
                  className="cursor-pointer"
                >
                  <Monitor className="mr-2 size-4 text-muted-foreground" />
                  <span>{tSet("themeSystem")}</span>
                </DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <form action={logoutAction} className="w-full">
            <button
              type="submit"
              className="w-full text-left text-destructive cursor-pointer flex items-center"
            >
              <LogOut className="mr-2 size-4" />
              {tTop("logout")}
            </button>
          </form>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
