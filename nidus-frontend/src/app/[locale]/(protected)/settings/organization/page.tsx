import * as React from "react";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import { OrganizationSettingsForm } from "@/modules/organization/components/org-settings-form";
import { OrgDangerZone } from "@/modules/organization/components/org-danger-zone";

export default async function OrganizationPage() {
  const user = (await getCurrentUser())!;

  const safeOrganization = JSON.parse(JSON.stringify(user.organization));

  return (
    <div className="space-y-8">
      <OrganizationSettingsForm organization={safeOrganization} />
      <OrgDangerZone
        organizationName={safeOrganization.name}
        organizationSlug={safeOrganization.slug}
      />
    </div>
  );
}
