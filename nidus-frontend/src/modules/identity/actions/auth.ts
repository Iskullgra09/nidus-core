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
  ForgotPasswordFormData,
  ResetPasswordPayload,
} from "../types/auth";

export async function getCurrentUser(): Promise<UserProfileResponse | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) return null;

  const response = await fetchClient<UserProfileResponse>("/users/me", {
    headers: { Authorization: `Bearer ${session}` },
  });

  return response.status === "success" && response.data ? response.data : null;
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
    const response = await fetchClient<TokenResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });

    if (response.status === "success" && response.data) {
      const cookieStore = await cookies();
      cookieStore.set("nidus_session", response.data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7,
        path: "/",
      });
      return { status: "success", message: tAuth("loginSuccess") };
    }

    return {
      status: "error",
      message: response.message || t("invalidCredentials"),
    };
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
    const payload: OnboardingPayload = {
      organization_name: formData.organization_name,
      organization_slug: slugify(formData.organization_name),
      admin_email: formData.email,
      password: formData.password,
    };

    const response = await fetchClient("/organizations/onboarding", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      return { status: "success", message: tReg("successMessage") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Onboarding Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("nidus_session");
  redirect("/login");
}

export async function forgotPasswordAction(
  formData: ForgotPasswordFormData,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");
  const tForgot = await getTranslations("ForgotPassword");

  try {
    const response = await fetchClient("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email: formData.email }),
    });

    if (response.status === "success") {
      return { status: "success", message: tForgot("successMessage") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Forgot Password Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function resetPasswordAction(
  payload: ResetPasswordPayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");
  const tReset = await getTranslations("ResetPassword");

  try {
    const response = await fetchClient("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      const cookieStore = await cookies();
      cookieStore.delete("nidus_session");
      return { status: "success", message: tReset("successMessage") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Reset Password Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}
