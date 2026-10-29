"use server";

import { cookies } from "next/headers";
import { getLocale } from "next-intl/server";
import { redirectTo } from "@/core/i18n/routing";
import { fetchClient } from "@/core/api/client";
import { UserProfileResponse } from "../types/user";
import { UserOrganizationSummary } from "../types/auth";
import {
  SESSION_COOKIE_NAME,
  sessionCookieOptions,
} from "../lib/session-cookie";

export async function setSessionCookie(token: string) {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE_NAME, token, sessionCookieOptions());
}

export async function getCurrentUser(): Promise<UserProfileResponse | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get(SESSION_COOKIE_NAME)?.value;

  if (!session) return null;

  const response = await fetchClient<UserProfileResponse>("/users/me", {
    headers: { Authorization: `Bearer ${session}` },
  });

  return response.status === "success" && response.data ? response.data : null;
}

export async function hasSessionCookie(): Promise<boolean> {
  return Boolean((await cookies()).get(SESSION_COOKIE_NAME)?.value);
}

export async function getUserOrganizations(): Promise<UserOrganizationSummary[]> {
  const cookieStore = await cookies();
  const session = cookieStore.get(SESSION_COOKIE_NAME)?.value;

  if (!session) return [];

  const response = await fetchClient<UserOrganizationSummary[]>(
    "/users/me/organizations",
    { headers: { Authorization: `Bearer ${session}` } },
  );

  return response.status === "success" && response.data ? response.data : [];
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE_NAME, "", sessionCookieOptions(0));
  redirectTo("/login", await getLocale());
}
