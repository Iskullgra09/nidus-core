import { NextRequest, NextResponse } from "next/server";
import { routing } from "@/core/i18n/routing";

export async function GET(request: NextRequest) {
  const localeParam = request.nextUrl.searchParams.get("locale");
  const locale =
    localeParam && routing.locales.includes(localeParam as "es" | "en")
      ? localeParam
      : routing.defaultLocale;

  const response = NextResponse.redirect(
    new URL(`/${locale}/login`, request.url),
  );

  response.cookies.set("nidus_session", "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });

  return response;
}
