import * as React from "react";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import { OrganizationSettingsForm } from "@/modules/organization/components/org-settings-form";

export default async function OrganizationPage() {
  const user = (await getCurrentUser())!;

  const safeOrganization = JSON.parse(JSON.stringify(user.organization));

  return (
    <div className="space-y-6">
      <OrganizationSettingsForm organization={safeOrganization} />
    </div>
  );
}
