"use server";

import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { redirect } from "next/navigation";
import { fetchClient } from "@/core/api/client";
import { UserProfileResponse } from "../types/user";
import {
  LoginRequest,
  TokenResponse,
  AuthActionResponse,
  RegisterFormData,
  OnboardingPayload,
} from "../types/auth";
import { FastAPIErrorResponse } from "@/core/types/api";

export async function getCurrentUser(): Promise<UserProfileResponse | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) return null;

  const response = await fetchClient<UserProfileResponse>("/organizations/me", {
    headers: { Authorization: `Bearer ${session}` },
  });

  return response.status === "success" ? response.data : null;
}

export async function loginAction(
  credentials: LoginRequest,
): Promise<AuthActionResponse> {
  const t = await getTranslations("Common");
  const tAuth = await getTranslations("Auth");

  const formData = new URLSearchParams();
  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  try {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });

    if (response.ok) {
      const data = (await response.json()) as TokenResponse;
      const cookieStore = await cookies();

      cookieStore.set("nidus_session", data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7,
        path: "/",
      });

      return { status: "success", message: tAuth("loginSuccess") };
    }

    const errorData = (await response.json()) as FastAPIErrorResponse;
    const errorMessage =
      typeof errorData.detail === "string"
        ? errorData.detail
        : t("invalidCredentials");

    return { status: "error", message: errorMessage };
  } catch (error) {
    console.error("Login Error:", error);
    return { status: "error", message: t("connectionError") };
  }
}

function slugify(text: string): string {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]+/g, "")
    .replace(/--+/g, "-");
}

export async function registerAction(
  formData: RegisterFormData,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");
  const tReg = await getTranslations("Register");

  try {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
    const payload: OnboardingPayload = {
      organization_name: formData.organization_name,
      organization_slug: slugify(formData.organization_name),
      admin_email: formData.email,
      password: formData.password,
    };

    const response = await fetch(`${baseUrl}/organizations/onboarding`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return { status: "success", message: tReg("successMessage") };
    }

    const errorData = (await response.json()) as FastAPIErrorResponse;
    return {
      status: "error",
      message:
        typeof errorData.detail === "string"
          ? errorData.detail
          : tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Register Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("nidus_session");
  redirect("/login");
}
