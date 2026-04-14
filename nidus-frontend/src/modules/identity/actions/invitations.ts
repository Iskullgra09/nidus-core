"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { InvitationPayload, InvitationResponse } from "../types/invitation";
import { AuthActionResponse } from "../types/auth";

export async function inviteMemberAction(
  payload: InvitationPayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const cookieStore = await cookies();
    const session = cookieStore.get("nidus_session")?.value;

    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient<InvitationResponse>(
      "/identity/invitations",
      {
        method: "POST",
        headers: { Authorization: `Bearer ${session}` },
        body: JSON.stringify(payload),
      },
    );

    if (response.status === "success") {
      revalidatePath("/settings/organization/members");
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
    console.error("Invite member error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function acceptInvitationAction(payload: {
  token: string;
  password: string;
}) {
  const t = await getTranslations("Common");

  try {
    const response = await fetchClient("/identity/invitations/accept", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      return { status: "success", message: response.message };
    }

    return { status: "error", message: response.message || t("unknownError") };
  } catch (error) {
    console.error("Accept invite error:", error);
    return { status: "error", message: t("connectionError") };
  }
}

export interface VerificationResult {
  status: "success" | "error";
  message: string;
  code?: string;
}

export async function verifyInvitationToken(
  token: string,
): Promise<VerificationResult> {
  const t = await getTranslations("Common");

  try {
    const response = await fetchClient<Record<string, boolean>>(
      `/identity/invitations/verify/${token}`,
    );

    if (response.status === "success") {
      return {
        status: "success",
        message: response.message || t("success"),
      };
    }

    return {
      status: "error",
      message: response.message || t("unknownError"),
      code: "API_ERROR",
    };
  } catch (error) {
    console.error("Verify token error:", error);
    return {
      status: "error",
      message: t("connectionError"),
      code: "CONNECTION_ERROR",
    };
  }
}
