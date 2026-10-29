"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog";
import { CanAccess } from "@/modules/access/components/can-access";
import { NidusScope } from "@/shared/access/scopes";
import { deleteOrganizationAction } from "../actions/org";

interface OrgDangerZoneProps {
  organizationName: string;
  organizationSlug: string;
}

export function OrgDangerZone({
  organizationName,
  organizationSlug,
}: OrgDangerZoneProps) {
  const t = useTranslations("SettingsOrg");
  const [open, setOpen] = React.useState(false);
  const [confirmSlug, setConfirmSlug] = React.useState("");
  const [isDeleting, setIsDeleting] = React.useState(false);

  const canDelete = confirmSlug === organizationSlug;

  async function handleDelete() {
    if (!canDelete || isDeleting) return;

    setIsDeleting(true);
    const result = await deleteOrganizationAction();

    // On success the action redirects; only surface failures here.
    if (result.status === "error") {
      toast.error(result.message || t("deleteError"));
      setIsDeleting(false);
    }
  }

  return (
    <CanAccess scope={NidusScope.ORG_DELETE}>
      <div className="max-w-md space-y-4 rounded-md border border-destructive/40 bg-destructive/5 p-5">
        <div className="space-y-1">
          <h4 className="text-sm font-semibold text-destructive">
            {t("dangerZoneTitle")}
          </h4>
          <p className="text-sm text-muted-foreground">
            {t("dangerZoneDescription")}
          </p>
        </div>

        <Button
          type="button"
          variant="destructive"
          size="sm"
          onClick={() => {
            setConfirmSlug("");
            setOpen(true);
          }}
        >
          {t("deleteButton")}
        </Button>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("deleteDialogTitle")}</DialogTitle>
              <DialogDescription>
                {t("deleteDialogDescription", { name: organizationName })}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                {t("deleteConfirmHint", { slug: organizationSlug })}
              </p>
              <Input
                value={confirmSlug}
                onChange={(e) => setConfirmSlug(e.target.value)}
                placeholder={organizationSlug}
                autoComplete="off"
                disabled={isDeleting}
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={isDeleting}
              >
                {t("deleteCancel")}
              </Button>
              <Button
                type="button"
                variant="destructive"
                disabled={!canDelete || isDeleting}
                onClick={handleDelete}
              >
                {isDeleting ? t("deleting") : t("deleteConfirm")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </CanAccess>
  );
}
