import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PATHS = ["/dashboard", "/settings", "/org"];
const AUTH_PATHS = ["/login", "/register", "/forgot-password"];

export default function proxy(request: NextRequest) {
  const token = request.cookies.get("nidus_session")?.value;
  const { pathname } = request.nextUrl;

  const isProtectedRoute = PROTECTED_PATHS.some((path) =>
    pathname.startsWith(path),
  );
  const isAuthRoute = AUTH_PATHS.some((path) => pathname.startsWith(path));

  if (isProtectedRoute && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
