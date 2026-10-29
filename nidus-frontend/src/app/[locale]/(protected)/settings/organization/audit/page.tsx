import { getTranslations } from "next-intl/server";
import { getRecentAuditLogs } from "@/modules/access/actions/audit";
import { AuditLogsPanel } from "@/modules/access/components/audit-logs-panel";

export default async function AuditSettingsPage() {
  const t = await getTranslations("SettingsAudit");
  const logs = await getRecentAuditLogs(50);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{t("title")}</h3>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      <div className="rounded-md border bg-card p-4 shadow-sm">
        <AuditLogsPanel
          logs={logs}
          emptyLabel={t("empty")}
          noResourceLabel={t("noResource")}
        />
      </div>
    </div>
  );
}
