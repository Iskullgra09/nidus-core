"use server";

import { cookies } from "next/headers";
import { fetchClient } from "@/core/api/client";
import { UserProfileResponse } from "../types/user";
import { LoginRequest, TokenResponse, AuthActionResponse } from "../types/auth";
import { redirect } from "next/navigation";
import { FastAPIErrorResponse } from "@/core/types/api";

export async function getCurrentUser(): Promise<UserProfileResponse | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get("nidus_session")?.value;

  if (!session) return null;

  const response = await fetchClient<UserProfileResponse>("/organizations/me", {
    headers: {
      Authorization: `Bearer ${session}`,
    },
  });

  if (response.status === "success" && response.data) {
    return response.data;
  }

  return null;
}

export async function loginAction(
  credentials: LoginRequest,
): Promise<AuthActionResponse> {
  const formData = new URLSearchParams();
  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  try {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

    const response = await fetch(`${baseUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (response.ok) {
      const data = (await response.json()) as TokenResponse;

      const cookieStore = await cookies();
      cookieStore.set("nidus_session", data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7,
        path: "/",
      });

      return { status: "success", message: "Autenticación exitosa" };
    }

    const errorData = (await response.json()) as FastAPIErrorResponse;
    let errorMessage = "Credenciales inválidas";

    if (typeof errorData.detail === "string") {
      errorMessage = errorData.detail;
    } else if (errorData.message) {
      errorMessage = errorData.message;
    }

    return {
      status: "error",
      message: errorMessage,
    };
  } catch (error) {
    return {
      status: "error",
      message: "Error de conexión con el servidor: " + error,
    };
  }
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete("nidus_session");
  redirect("/login");
}
