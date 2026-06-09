"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { OrganizationUpdatePayload } from "../types";
import { AuthActionResponse } from "@/modules/identity/types/auth";

/**
 * Updates the current organization settings.
 */
export async function updateOrganizationAction(
  orgId: string,
  payload: OrganizationUpdatePayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");
  const tOrg = await getTranslations("SettingsOrg");

  try {
    const session = (await cookies()).get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient(`/organizations/${orgId}`, {
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
