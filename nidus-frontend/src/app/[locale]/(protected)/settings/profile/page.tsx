import * as React from "react";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import { GeneralSettingsForm } from "@/modules/identity/components/general-settings-form";

export default async function ProfilePage() {
  const user = (await getCurrentUser())!;

  return (
    <div className="space-y-6">
      <GeneralSettingsForm user={user} />
    </div>
  );
}
