"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { ActionResponse } from "@/core/types/api";
import {
  SESSION_COOKIE_NAME,
  sessionCookieOptions,
} from "../lib/session-cookie";
import { ChangePasswordPayload, UpdateProfilePayload } from "../types/user";

export async function changePasswordAction(
  payload: ChangePasswordPayload,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");
  const tSettings = await getTranslations("Settings");

  try {
    const cookieStore = await cookies();
    const session = cookieStore.get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient("/auth/change-password", {
      method: "POST",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      cookieStore.set(SESSION_COOKIE_NAME, "", sessionCookieOptions(0));
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

export async function persistLanguageAction(
  language: "es" | "en",
): Promise<ActionResponse> {
  return updateProfileAction({ preferences: { language } });
}

export async function updateProfileAction(
  payload: UpdateProfilePayload,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const cookieStore = await cookies();
    const session = cookieStore.get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const body: UpdateProfilePayload = {};

    if (payload.full_name !== undefined) {
      body.full_name = payload.full_name === "" ? null : payload.full_name;
    }

    if (payload.preferences !== undefined) {
      body.preferences = payload.preferences;
    }

    const response = await fetchClient("/users/me", {
      method: "PUT",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify(body),
    });

    if (response.status === "success") {
      revalidatePath("/", "layout");

      return {
        status: "success",
        message: response.message || tCommon("success"),
      };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Update profile Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}
