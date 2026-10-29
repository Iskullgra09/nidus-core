import { defineRouting } from "next-intl/routing";
import { createNavigation } from "next-intl/navigation";

export const routing = defineRouting({
  locales: ["es", "en"],
  defaultLocale: "es",
});

export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);

/** Locale-aware redirect typed as `never` for correct TS control-flow narrowing. */
export function redirectTo(href: string, locale: string): never {
  redirect({ href, locale });
  throw new Error("Unreachable: redirect did not terminate");
}
