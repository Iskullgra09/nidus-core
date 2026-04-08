import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import createIntlMiddleware from "next-intl/middleware";
import { routing } from "@/core/i18n/routing";

const intlMiddleware = createIntlMiddleware(routing);

const PROTECTED_PATHS = ["/dashboard", "/settings", "/org"];
const AUTH_PATHS = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
];

export default function proxy(request: NextRequest) {
  const token = request.cookies.get("nidus_session")?.value;
  const { pathname } = request.nextUrl;

  let currentLocale = "";
  let cleanPathname = pathname;

  for (const loc of routing.locales) {
    if (pathname.startsWith(`/${loc}/`) || pathname === `/${loc}`) {
      currentLocale = loc;
      cleanPathname = pathname.replace(`/${loc}`, "") || "/";
      break;
    }
  }

  const isProtectedRoute = PROTECTED_PATHS.some((path) =>
    cleanPathname.startsWith(path),
  );
  const isAuthRoute = AUTH_PATHS.some((path) => cleanPathname.startsWith(path));

  if (isProtectedRoute && !token) {
    const targetPath = currentLocale ? `/${currentLocale}/login` : "/login";
    const loginUrl = new URL(targetPath, request.url);
    loginUrl.searchParams.set("from", cleanPathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthRoute && token) {
    const targetPath = currentLocale
      ? `/${currentLocale}/dashboard`
      : "/dashboard";
    return NextResponse.redirect(new URL(targetPath, request.url));
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
