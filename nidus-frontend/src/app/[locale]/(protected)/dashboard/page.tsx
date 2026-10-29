import { getTranslations } from "next-intl/server";
import { Activity, Building2, HeartPulse, Users } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { getCurrentUser, getUserOrganizations } from "@/modules/identity/actions/auth";
import { getOrganizationMembersPage } from "@/modules/organization/actions/members";
import { getRecentAuditLogs } from "@/modules/access/actions/audit";
import { hasScope } from "@/shared/access/permissions";
import { NidusScope } from "@/shared/access/scopes";
import { fetchClient } from "@/core/api/client";
import { Link } from "@/core/i18n/routing";

async function getSystemHealth(): Promise<"ok" | "down"> {
  try {
    const response = await fetchClient<{ status?: string }>("/health/");
    if (response.status === "success" && response.data?.status === "ok") {
      return "ok";
    }
    return "down";
  } catch {
    return "down";
  }
}

export default async function DashboardPage() {
  const t = await getTranslations("Dashboard");
  const user = await getCurrentUser();

  const [membersPage, organizations, health] = await Promise.all([
    getOrganizationMembersPage({ limit: 100 }),
    getUserOrganizations(),
    getSystemHealth(),
  ]);

  const canReadAudit = hasScope(user, NidusScope.AUDIT_READ);
  const recentActivity = canReadAudit ? await getRecentAuditLogs(5) : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t("membersCard")}
            </CardTitle>
            <Users className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{membersPage.items.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {membersPage.page_info.has_next_page
                ? t("membersCardHintMore")
                : t("membersCardHint")}
            </p>
            <Link
              href="/settings/organization/members"
              className="text-xs text-primary hover:underline mt-2 inline-block"
            >
              {t("manageMembers")}
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t("orgsCard")}
            </CardTitle>
            <Building2 className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{organizations.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {t("orgsCardHint")}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t("healthCard")}
            </CardTitle>
            <HeartPulse className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${
                health === "ok" ? "text-primary" : "text-destructive"
              }`}
            >
              {health === "ok" ? t("healthOk") : t("healthDown")}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {t("healthCardHint")}
            </p>
          </CardContent>
        </Card>
      </div>

      {canReadAudit && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="size-4" />
                {t("activityTitle")}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {t("activityDescription")}
              </p>
            </div>
          </CardHeader>
          <CardContent>
            {recentActivity.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("activityEmpty")}</p>
            ) : (
              <ul className="space-y-3">
                {recentActivity.map((event) => (
                  <li
                    key={event.id}
                    className="flex items-center justify-between gap-4 border-b border-border/50 pb-2 last:border-0 last:pb-0"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">
                        {event.action}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {event.resource_type
                          ? `${event.resource_type}${event.resource_id ? ` · ${event.resource_id.slice(0, 8)}` : ""}`
                          : t("activityNoResource")}
                      </p>
                    </div>
                    <time className="text-xs text-muted-foreground shrink-0 tabular-nums">
                      {new Date(event.created_at).toLocaleString()}
                    </time>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
