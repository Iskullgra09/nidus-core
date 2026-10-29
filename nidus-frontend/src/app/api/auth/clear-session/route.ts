import { NextRequest, NextResponse } from "next/server";
import { routing } from "@/core/i18n/routing";
import {
  SESSION_COOKIE_NAME,
  sessionCookieOptions,
} from "@/modules/identity/lib/session-cookie";

export async function GET(request: NextRequest) {
  const localeParam = request.nextUrl.searchParams.get("locale");
  const locale =
    localeParam && routing.locales.includes(localeParam as "es" | "en")
      ? localeParam
      : routing.defaultLocale;

  const response = NextResponse.redirect(
    new URL(`/${locale}/login`, request.url),
  );

  response.cookies.set(SESSION_COOKIE_NAME, "", sessionCookieOptions(0));

  return response;
}
