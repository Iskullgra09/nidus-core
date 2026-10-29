export const THEME_STORAGE_KEY = "nidus-theme";

export type ResolvedTheme = "light" | "dark";
export type Theme = ResolvedTheme | "system";

export function isTheme(value: string | undefined): value is Theme {
  return value === "light" || value === "dark" || value === "system";
}

/** Only explicit light/dark can be applied during SSR; "system" resolves on the client. */
export function getServerThemeClass(
  stored: string | undefined,
): ResolvedTheme | undefined {
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return undefined;
}

export function persistThemePreference(theme: Theme) {
  if (typeof document === "undefined") return;

  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // localStorage may be unavailable
  }

  document.cookie = `${THEME_STORAGE_KEY}=${theme};path=/;max-age=31536000;SameSite=Lax`;
}
