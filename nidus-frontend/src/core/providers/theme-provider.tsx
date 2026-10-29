"use client";

import * as React from "react";
import {
  THEME_STORAGE_KEY,
  persistThemePreference,
  type ResolvedTheme,
  type Theme,
} from "@/core/providers/theme-config";

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: ResolvedTheme;
  systemTheme: ResolvedTheme | undefined;
  themes: Theme[];
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(
  undefined,
);

const defaultContext: ThemeContextValue = {
  theme: "system",
  setTheme: () => {},
  resolvedTheme: "light",
  systemTheme: undefined,
  themes: [],
};

function getSystemTheme(): ResolvedTheme {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function readStoredTheme(): Theme {
  if (typeof window === "undefined") return "system";

  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark" || stored === "system") {
      return stored;
    }
  } catch {
    // localStorage may be unavailable
  }

  return "system";
}

function resolveTheme(theme: Theme, systemTheme: ResolvedTheme): ResolvedTheme {
  return theme === "system" ? systemTheme : theme;
}

function applyTheme(
  resolved: ResolvedTheme,
  disableTransitionOnChange: boolean,
) {
  const root = document.documentElement;

  const update = () => {
    root.classList.remove("light", "dark");
    root.classList.add(resolved);
    root.style.colorScheme = resolved;
  };

  if (!disableTransitionOnChange) {
    update();
    return;
  }

  const style = document.createElement("style");
  style.appendChild(
    document.createTextNode(
      "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}",
    ),
  );
  document.head.appendChild(style);
  update();
  window.setTimeout(() => {
    document.head.removeChild(style);
  }, 1);
}

interface ThemeProviderProps {
  children: React.ReactNode;
  disableTransitionOnChange?: boolean;
}

export function ThemeProvider({
  children,
  disableTransitionOnChange = false,
}: ThemeProviderProps) {
  const [theme, setThemeState] = React.useState<Theme>("system");
  const [systemTheme, setSystemTheme] =
    React.useState<ResolvedTheme>("light");
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setThemeState(readStoredTheme());
    setSystemTheme(getSystemTheme());
    setMounted(true);
  }, []);

  const resolvedTheme = resolveTheme(theme, systemTheme);

  React.useEffect(() => {
    if (!mounted) return;
    applyTheme(resolvedTheme, disableTransitionOnChange);
  }, [resolvedTheme, mounted, disableTransitionOnChange]);

  React.useEffect(() => {
    if (!mounted || theme !== "system") return;

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setSystemTheme(getSystemTheme());

    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, [theme, mounted]);

  const setTheme = React.useCallback((next: Theme) => {
    setThemeState(next);
    persistThemePreference(next);
  }, []);

  const value = React.useMemo(
    () => ({
      theme,
      setTheme,
      resolvedTheme,
      systemTheme: theme === "system" ? systemTheme : undefined,
      themes: ["light", "dark", "system"] as Theme[],
    }),
    [theme, setTheme, resolvedTheme, systemTheme],
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  return React.useContext(ThemeContext) ?? defaultContext;
}
