"use server";

import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { ActionResponse } from "@/core/types/api";
import { ForgotPasswordFormData, ResetPasswordPayload } from "../types/auth";

export async function forgotPasswordAction(
  formData: ForgotPasswordFormData,
): Promise<ActionResponse> {
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
): Promise<ActionResponse> {
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
