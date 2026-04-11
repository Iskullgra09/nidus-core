import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import createIntlMiddleware from "next-intl/middleware";
import { routing } from "@/core/i18n/routing";
import { NidusScope } from "@/modules/identity/types/scopes";
import { decodeJwt } from "jose";

const intlMiddleware = createIntlMiddleware(routing);

const ROUTE_PERMISSIONS: Record<string, NidusScope[]> = {
  "/settings/organization/members": [NidusScope.MEMBER_READ],
  "/settings/organization": [NidusScope.ORG_UPDATE],
  "/org": [NidusScope.ORG_READ],
  "/dashboard": [],
};

const AUTH_PATHS = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
];

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("nidus_session")?.value;

  let currentLocale = routing.defaultLocale;
  let cleanPathname = pathname;

  for (const loc of routing.locales) {
    if (pathname.startsWith(`/${loc}/`) || pathname === `/${loc}`) {
      currentLocale = loc;
      cleanPathname = pathname.replace(`/${loc}`, "") || "/";
      break;
    }
  }

  const isAuthRoute = AUTH_PATHS.some((path) => cleanPathname.startsWith(path));
  if (isAuthRoute && token) {
    return NextResponse.redirect(
      new URL(`/${currentLocale}/dashboard`, request.url),
    );
  }

  const requiredScopes = Object.entries(ROUTE_PERMISSIONS).find(([path]) =>
    cleanPathname.startsWith(path),
  )?.[1];

  if (requiredScopes !== undefined) {
    if (!token) {
      const loginUrl = new URL(`/${currentLocale}/login`, request.url);
      loginUrl.searchParams.set("from", cleanPathname);
      return NextResponse.redirect(loginUrl);
    }

    try {
      const payload = decodeJwt(token) as { scopes?: string[] };
      const userScopes = payload.scopes || [];
      const hasAccess = checkUserAccess(userScopes, requiredScopes);
      if (!hasAccess) {
        console.warn(
          `[AUTH] Acceso denegado a ${cleanPathname}. Scopes requeridos: ${requiredScopes}`,
        );
        return NextResponse.redirect(
          new URL(
            `/${currentLocale}/dashboard?error=unauthorized`,
            request.url,
          ),
        );
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      return NextResponse.redirect(
        new URL(`/${currentLocale}/login`, request.url),
      );
    }
  }

  return intlMiddleware(request);
}

function checkUserAccess(
  userScopes: string[],
  requiredScopes: NidusScope[],
): boolean {
  if (userScopes.includes(NidusScope.SUPERADMIN)) return true;
  if (requiredScopes.length === 0) return true;
  return requiredScopes.every((required) => {
    if (userScopes.includes(required)) return true;
    const baseResource = required.split(":").slice(0, -1).join(":");
    return userScopes.some(
      (s) => s.startsWith(baseResource) && s.endsWith(":write"),
    );
  });
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
