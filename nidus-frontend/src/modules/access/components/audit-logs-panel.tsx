import { AuditLogItem } from "@/modules/access/actions/audit";

interface AuditLogsPanelProps {
  logs: AuditLogItem[];
  emptyLabel: string;
  noResourceLabel: string;
}

export function AuditLogsPanel({
  logs,
  emptyLabel,
  noResourceLabel,
}: AuditLogsPanelProps) {
  if (logs.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyLabel}</p>;
  }

  return (
    <ul className="space-y-3">
      {logs.map((event) => (
        <li
          key={event.id}
          className="flex items-center justify-between gap-4 border-b border-border/50 pb-2 last:border-0 last:pb-0"
        >
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{event.action}</p>
            <p className="text-xs text-muted-foreground truncate">
              {event.resource_type
                ? `${event.resource_type}${event.resource_id ? ` · ${event.resource_id.slice(0, 8)}` : ""}`
                : noResourceLabel}
            </p>
          </div>
          <time className="text-xs text-muted-foreground shrink-0 tabular-nums">
            {new Date(event.created_at).toLocaleString()}
          </time>
        </li>
      ))}
    </ul>
  );
}
