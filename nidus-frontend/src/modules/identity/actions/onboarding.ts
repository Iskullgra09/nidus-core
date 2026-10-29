"use server";

import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { ActionResponse } from "@/core/types/api";
import { OnboardingPayload, RegisterFormData } from "../types/auth";

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
): Promise<ActionResponse> {
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
