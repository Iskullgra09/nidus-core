"use server";

import { cookies } from "next/headers";
import { fetchClient } from "@/core/api/client";
import { OrganizationUpdatePayload } from "../types";
import { getTranslations } from "next-intl/server";

export interface ActionResponse {
  status: "success" | "error";
  message: string;
}

/**
 * Updates the current organization settings.
 * Relies on the backend matching the org_id with the JWT context.
 */
export async function updateOrganizationAction(
  orgId: string,
  payload: OrganizationUpdatePayload,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");

  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) {
    return { status: "error", message: tCommon("connectionError") };
  }

  const response = await fetchClient(`/organizations/${orgId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${session}` },
    body: JSON.stringify(payload),
  });

  return {
    status: response.status,
    message: response.message || tCommon("unknownError"),
  };
}
