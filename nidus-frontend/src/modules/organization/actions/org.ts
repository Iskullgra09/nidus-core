"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { isRedirectError } from "next/dist/client/components/redirect-error";
import { getLocale, getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { redirectTo } from "@/core/i18n/routing";
import { ActionResponse } from "@/core/types/api";
import {
  SESSION_COOKIE_NAME,
  sessionCookieOptions,
} from "@/modules/identity/lib/session-cookie";
import { OrganizationUpdatePayload } from "../types";

export async function uploadOrganizationAvatarAction(
  formData: FormData,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient<{ avatar_url: string }>(
      "/organizations/me/avatar",
      {
        method: "POST",
        headers: { Authorization: `Bearer ${session}` },
        body: formData,
      },
    );

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
    console.error("Upload org avatar Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function removeOrganizationAvatarAction(): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient("/organizations/me/avatar", {
      method: "DELETE",
      headers: { Authorization: `Bearer ${session}` },
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
    console.error("Remove org avatar Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function updateOrganizationAction(
  payload: OrganizationUpdatePayload,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");
  const tOrg = await getTranslations("SettingsOrg");

  try {
    const session = (await cookies()).get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient("/organizations/me", {
      method: "PATCH",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      revalidatePath("/", "layout");
      return {
        status: "success",
        message: response.message || tOrg("successMessage"),
      };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Update Organization Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

/**
 * Soft-deletes the active organization, clears the session, and sends the user to login.
 */
export async function deleteOrganizationAction(): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");
  const tOrg = await getTranslations("SettingsOrg");

  try {
    const cookieStore = await cookies();
    const session = cookieStore.get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient("/organizations/me", {
      method: "DELETE",
      headers: { Authorization: `Bearer ${session}` },
    });

    if (response.status === "success") {
      cookieStore.set(SESSION_COOKIE_NAME, "", sessionCookieOptions(0));
      redirectTo("/login", await getLocale());
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    if (isRedirectError(error)) throw error;
    console.error("Delete Organization Error:", error);
    return { status: "error", message: tOrg("deleteError") };
  }
}
