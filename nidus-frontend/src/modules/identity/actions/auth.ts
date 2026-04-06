"use server";

import { cookies } from "next/headers";
import { fetchClient } from "@/core/api/client";
import { UserProfileResponse } from "../types/user";
import { LoginRequest, TokenResponse, AuthActionResponse } from "../types/auth";

export async function getCurrentUser(): Promise<UserProfileResponse | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) return null;

  const response = await fetchClient<UserProfileResponse>("/identity/me", {
    headers: {
      Authorization: `Bearer ${session}`,
    },
  });

  if (response.status === "success" && response.data) {
    return response.data;
  }

  return null;
}

export async function loginAction(
  credentials: LoginRequest,
): Promise<AuthActionResponse> {
  const response = await fetchClient<TokenResponse>("/identity/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  if (response.status === "success" && response.data?.access_token) {
    const cookieStore = await cookies();
    cookieStore.set("nidus_session", response.data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7,
      path: "/",
    });
    return { status: "success", message: "Authenticated successfully" };
  }

  return {
    status: "error",
    message: response.message || "Invalid credentials",
  };
}
