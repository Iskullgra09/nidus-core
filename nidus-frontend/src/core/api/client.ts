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

  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  try {
    const response = await fetch(url.toString(), {
      ...init,
      headers,
    });

    const text = await response.text();
    const data: GenericResponse<T> = text ? JSON.parse(text) : {};

    if (data.status !== "success" || !response.ok) {
      return {
        status: "error",
        data: null,
        message: data.message || "Request failed",
        errors: data.errors || [],
      };
    }

    return data;
  } catch (error) {
    return {
      status: "error",
      data: null,
      message: "Internal Connection Error",
      errors: [{ field: "network", message: String(error) }],
    };
  }
};
