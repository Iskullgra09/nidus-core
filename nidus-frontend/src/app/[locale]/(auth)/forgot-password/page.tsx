import { getTranslations } from "next-intl/server";
import { ForgotPasswordForm } from "@/modules/identity/components/forgot-password-form";
import { AuthCard } from "@/shared/components/layout/auth-card";

export default async function ForgotPasswordPage() {
  const t = await getTranslations("ForgotPassword");

  return (
    <AuthCard title={t("title")} description={t("description")}>
      <ForgotPasswordForm />
    </AuthCard>
  );
}
