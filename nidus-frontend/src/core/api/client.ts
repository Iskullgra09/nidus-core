import { getLocale } from "next-intl/server";
import { GenericResponse } from "@/core/types/api";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export type FetchOptions = RequestInit & {
  params?: Record<string, string | number | boolean | null | undefined>;
};

export const fetchClient = async <T>(
  endpoint: string,
  options: FetchOptions = {},
): Promise<GenericResponse<T>> => {
  const { params, ...init } = options;

  const url = new URL(`${BASE_URL}${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const locale = await getLocale();
  const headers = new Headers(init.headers);
  const isFormData =
    typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (isFormData) {
    headers.delete("Content-Type");
  }
  headers.set("Accept-Language", locale);

  try {
    const response = await fetch(url.toString(), {
      ...init,
      headers,
    });

    const text = await response.text();
    let payload: Record<string, unknown> = {};
    if (text) {
      try {
        payload = JSON.parse(text) as Record<string, unknown>;
      } catch {
        return {
          status: "error",
          data: null,
          message: "Invalid JSON response from API",
          errors: [{ field: "parse", message: text.slice(0, 200) }],
        };
      }
    }

    const status = payload.status as string | undefined;
    const message =
      typeof payload.message === "string" ? payload.message : null;

    if (!response.ok || status === "error") {
      let errorMessage = message || "Request failed";

      if (!message && payload.detail !== undefined) {
        const detail = payload.detail;
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          const first = detail[0] as { msg?: string };
          errorMessage = first.msg || errorMessage;
        }
      }

      return {
        status: "error",
        data: null,
        message: errorMessage,
        errors: (payload.errors as GenericResponse<T>["errors"]) || [],
      };
    }

    return {
      status: "success",
      data: (payload.data as T | null | undefined) ?? null,
      message: message || "Success",
    };
  } catch (error) {
    return {
      status: "error",
      data: null,
      message: "Internal Connection Error",
      errors: [{ field: "network", message: String(error) }],
    };
  }
};
