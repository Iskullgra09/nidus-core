"use server";

import { cookies } from "next/headers";
import { fetchClient } from "@/core/api/client";
import { CursorPage } from "@/core/types/api";

export interface AuditLogItem {
  id: string;
  organization_id: string;
  actor_user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  metadata: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
}

export async function getRecentAuditLogs(
  limit = 5,
): Promise<AuditLogItem[]> {
  try {
    const session = (await cookies()).get("nidus_session")?.value;
    if (!session) return [];

    const response = await fetchClient<CursorPage<AuditLogItem>>(
      "/audit-logs",
      {
        headers: { Authorization: `Bearer ${session}` },
        params: { limit },
      },
    );

    if (response.status === "success" && response.data?.items) {
      return response.data.items;
    }
    return [];
  } catch (error) {
    console.error("Fetch Audit Logs Error:", error);
    return [];
  }
}
