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
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  headers.set("Accept-Language", locale);

  try {
    const response = await fetch(url.toString(), {
      ...init,
      headers,
    });

    const text = await response.text();
    const data = text ? JSON.parse(text) : {};

    if (!response.ok || data.status === "error") {
      let errorMessage = data.message || "Request failed";

      if (!data.message && data.detail) {
        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0) {
          errorMessage = data.detail[0].msg;
        }
      }

      return {
        status: "error",
        data: null,
        message: errorMessage,
        errors: data.errors || [],
      } as GenericResponse<T>;
    }

    return {
      status: "success",
      data: data.data !== undefined ? data.data : data,
      message: data.message || "Success",
    } as GenericResponse<T>;
  } catch (error) {
    return {
      status: "error",
      data: null as unknown as T,
      message: "Internal Connection Error",
      errors: [{ field: "network", message: String(error) }],
    } as GenericResponse<T>;
  }
};
