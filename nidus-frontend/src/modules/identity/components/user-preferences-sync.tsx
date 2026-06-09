"use client";

import * as React from "react";
import { useLocale } from "next-intl";
import { useTheme } from "@/core/providers/theme-provider";
import { usePathname, useRouter } from "@/core/i18n/routing";
import { UserProfileResponse } from "../types/user";

interface UserPreferencesSyncProps {
  user: UserProfileResponse;
}

type AppLocale = "es" | "en";

function isAppLocale(value: string | undefined): value is AppLocale {
  return value === "es" || value === "en";
}

/** Applies DB-stored theme and language preferences after login / profile updates. */
export function UserPreferencesSync({ user }: UserPreferencesSyncProps) {
  const { setTheme } = useTheme();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const theme = user.preferences?.theme;
  const language = user.preferences?.language;

  React.useEffect(() => {
    if (!theme) return;
    setTheme(theme);
  }, [theme, setTheme]);

  React.useEffect(() => {
    if (!isAppLocale(language) || language === locale) return;
    router.replace(pathname, { locale: language });
  }, [language, locale, pathname, router]);

  return null;
}
