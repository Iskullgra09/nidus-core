"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { MemberResponse } from "@/modules/organization/types/members";
import { ActionResponse, CursorPage } from "@/core/types/api";

export type MembersQuery = {
  cursor?: string | null;
  q?: string | null;
  limit?: number;
};

export async function getOrganizationMembersPage(
  query: MembersQuery = {},
): Promise<CursorPage<MemberResponse>> {
  const empty: CursorPage<MemberResponse> = {
    items: [],
    page_info: { has_next_page: false, end_cursor: null },
  };

  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) return empty;

    const response = await fetchClient<CursorPage<MemberResponse>>(
      "/identity/members",
      {
        headers: { Authorization: `Bearer ${session}` },
        params: {
          limit: query.limit ?? 10,
          cursor: query.cursor || undefined,
          email__contains: query.q || undefined,
        },
      },
    );

    if (response.status === "success" && response.data) {
      return response.data;
    }
    return empty;
  } catch (error) {
    console.error("Fetch Members Error:", error);
    return empty;
  }
}

export async function getOrganizationMembers(): Promise<MemberResponse[]> {
  const page = await getOrganizationMembersPage({ limit: 100 });
  return page.items;
}

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
