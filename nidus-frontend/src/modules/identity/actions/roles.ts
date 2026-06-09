"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { AuthActionResponse } from "../types/auth";
import { RolePayload, RoleResponse } from "../types/roles";
import { ScopeResponse } from "../types/scopes-catalog";

const ROLES_PATH = "/settings/organization/roles";

export async function getAssignableScopes(): Promise<ScopeResponse[]> {
  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) return [];

    const response = await fetchClient<ScopeResponse[]>("/identity/scopes", {
      headers: { Authorization: `Bearer ${session}` },
    });

    return response.status === "success" && response.data ? response.data : [];
  } catch (error) {
    console.error("Fetch scopes error:", error);
    return [];
  }
}

export async function createRoleAction(
  payload: RolePayload,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient<RoleResponse>("/identity/roles", {
      method: "POST",
      headers: { Authorization: `Bearer ${session}` },
      body: JSON.stringify(payload),
    });

    if (response.status === "success") {
      revalidatePath(ROLES_PATH);
      revalidatePath("/settings/organization/members");
      return { status: "success", message: response.message || tCommon("success") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Create role error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function updateRoleAction(
  roleId: string,
  payload: Partial<RolePayload>,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient<RoleResponse>(
      `/identity/roles/${roleId}`,
      {
        method: "PATCH",
        headers: { Authorization: `Bearer ${session}` },
        body: JSON.stringify(payload),
      },
    );

    if (response.status === "success") {
      revalidatePath(ROLES_PATH);
      revalidatePath("/settings/organization/members");
      return { status: "success", message: response.message || tCommon("success") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Update role error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}

export async function deleteRoleAction(
  roleId: string,
): Promise<AuthActionResponse> {
  const tCommon = await getTranslations("Common");

  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) {
      return { status: "error", message: tCommon("connectionError") };
    }

    const response = await fetchClient(`/identity/roles/${roleId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${session}` },
    });

    if (response.status === "success") {
      revalidatePath(ROLES_PATH);
      revalidatePath("/settings/organization/members");
      return { status: "success", message: response.message || tCommon("success") };
    }

    return {
      status: "error",
      message: response.message || tCommon("unknownError"),
    };
  } catch (error) {
    console.error("Delete role error:", error);
    return { status: "error", message: tCommon("connectionError") };
  }
}
