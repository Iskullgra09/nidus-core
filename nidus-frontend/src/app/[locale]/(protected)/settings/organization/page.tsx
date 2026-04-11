import { getTranslations } from "next-intl/server";
import { OrganizationSettingsForm } from "@/modules/organization/components/org-settings-form";
import { getCurrentUser } from "@/modules/identity/actions/auth";

export default async function OrgSettingsPage() {
  const t = await getTranslations("OrgSettings");

  const rawUser = await getCurrentUser();
  const organizationData = JSON.parse(JSON.stringify(rawUser!.organization));

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      <div className="p-6 border rounded-md bg-card text-card-foreground shadow-sm">
        <OrganizationSettingsForm organization={organizationData} />
      </div>
    </div>
  );
}
