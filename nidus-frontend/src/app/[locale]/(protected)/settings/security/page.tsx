import * as React from "react";
import { SecuritySettingsForm } from "@/modules/identity/components/security-settings-form";

export default function SecurityPage() {
  return (
    <div className="space-y-6">
      <SecuritySettingsForm />
    </div>
  );
}
