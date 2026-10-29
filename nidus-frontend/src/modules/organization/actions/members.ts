"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { MemberResponse } from "@/modules/organization/types/members";
import { ActionResponse, CursorPage } from "@/core/types/api";

/**
 * Fetch members - Matches: GET /members
 */
export async function getOrganizationMembers(): Promise<MemberResponse[]> {
  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) return [];

    const response = await fetchClient<CursorPage<MemberResponse>>(
      "/identity/members",
      {
        headers: { Authorization: `Bearer ${session}` },
      },
    );

    if (response.status === "success" && response.data?.items) {
      return response.data.items;
    }
    return [];
  } catch (error) {
    console.error("Fetch Members Error:", error);
    return [];
  }
}

/**
 * Update Role - Matches: PATCH /members/{member_id}/role
 */
export async function updateMemberRoleAction(
  memberId: string,
  roleId: string,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get("nidus_session")?.value;
    const response = await fetchClient(`/identity/members/${memberId}/role`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify({ role_id: roleId }),
    });

    if (response.status === "success") {
      revalidatePath("/settings/organization/members");
      return { status: "success", message: response.message || "OK" };
    }
    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Update Members Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

/**
 * Remove Member - Matches: DELETE /members/{member_id}
 */
export async function removeMemberAction(
  memberId: string,
): Promise<ActionResponse> {
  const tCommon = await getTranslations("Common");
  try {
    const session = (await cookies()).get("nidus_session")?.value;
    const response = await fetchClient(`/identity/members/${memberId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${session}` },
    });

    if (response.status === "success") {
      revalidatePath("/settings/organization/members");
      return { status: "success", message: response.message || "OK" };
    }
    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Remove Members Error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}
