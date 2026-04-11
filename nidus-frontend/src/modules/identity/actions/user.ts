"use server";

import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { ChangePasswordPayload, UpdateProfilePayload } from "../types/user";
import { AuthActionResponse } from "../types/auth";

export async function changePasswordAction(
  payload: ChangePasswordPayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");
  const tSettings = await getTranslations("Settings");

  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) {
    return { status: "error", message: tCommon("connectionError") };
  }

  try {
    const response = await fetchClient("/auth/change-password", {
      method: "POST",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      const cookieStore = await cookies();
      cookieStore.delete("nidus_session");
      return { status: "success", message: tSettings("passwordSuccess") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Change password Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function updateProfileAction(
  payload: UpdateProfilePayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");

  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) {
    return { status: "error", message: tCommon("connectionError") };
  }

  const response = await fetchClient("/users/me", {
    method: "PUT",
    headers: { Authorization: `Bearer ${session}` },
    body: JSON.stringify(payload),
  });

  return {
    status: response.status,
    message: response.message || tCommon("unknownError"),
  };
}
