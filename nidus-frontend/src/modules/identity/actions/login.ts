"use server";

import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { fetchClient } from "@/core/api/client";
import { ActionResponse } from "@/core/types/api";
import {
  LoginRequest,
  TokenResponse,
  LoginActionResult,
  OrgSelectionActionResponse,
  LoginOrgSelectionPayload,
} from "../types/auth";
import { setSessionCookie } from "./session";

export async function loginAction(
  credentials: LoginRequest,
): Promise<LoginActionResult> {
  const t = await getTranslations("Common");
  const tAuth = await getTranslations("Auth");

  const formData = new URLSearchParams();
  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  try {
    const response = await fetchClient<
      TokenResponse | LoginOrgSelectionPayload
    >("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });

    if (response.status !== "success" || !response.data) {
      return {
        status: "error",
        message: response.message || t("invalidCredentials"),
      };
    }

    const data = response.data;

    if (
      "org_selection_required" in data &&
      data.org_selection_required === true &&
      Array.isArray(data.organizations) &&
      data.organizations.length > 1
    ) {
      return {
        status: "org_selection",
        organizations: data.organizations,
        preAuthToken: data.pre_auth_token,
      } satisfies OrgSelectionActionResponse;
    }

    if ("access_token" in data) {
      await setSessionCookie(data.access_token);
      return { status: "success", message: tAuth("loginSuccess") };
    }

    return { status: "error", message: t("unknownError") };
  } catch (error) {
    console.error("Login Error:", error);
    return { status: "error", message: t("connectionError") };
  }
}

export async function selectOrganizationAction(
  preAuthToken: string,
  organizationId: string,
): Promise<ActionResponse> {
  const t = await getTranslations("Common");
  const tAuth = await getTranslations("Auth");

  try {
    const response = await fetchClient<TokenResponse>("/auth/select-org", {
      method: "POST",
      body: JSON.stringify({
        pre_auth_token: preAuthToken,
        organization_id: organizationId,
      }),
    });

    if (response.status === "success" && response.data?.access_token) {
      await setSessionCookie(response.data.access_token);
      return { status: "success", message: tAuth("loginSuccess") };
    }

    return {
      status: "error",
      message: response.message || t("unknownError"),
    };
  } catch (error) {
    console.error("Select Org Error:", error);
    return { status: "error", message: t("connectionError") };
  }
}

export async function switchOrganizationAction(
  organizationId: string,
): Promise<ActionResponse> {
  const t = await getTranslations("Common");
  const tOrg = await getTranslations("OrganizationSwitcher");
  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) {
    return { status: "error", message: t("unknownError") };
  }

  try {
    const response = await fetchClient<TokenResponse>("/auth/switch-org", {
      method: "POST",
      body: JSON.stringify({ organization_id: organizationId }),
      headers: { Authorization: `Bearer ${session}` },
    });

    if (response.status === "success" && response.data?.access_token) {
      await setSessionCookie(response.data.access_token);
      return { status: "success", message: tOrg("switchSuccess") };
    }

    return {
      status: "error",
      message: response.message || t("unknownError"),
    };
  } catch (error) {
    console.error("Switch Org Error:", error);
    return { status: "error", message: t("connectionError") };
  }
}
