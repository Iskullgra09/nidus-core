import { getTranslations } from "next-intl/server";
import { RegisterForm } from "@/modules/identity/components/register-form";
import { AuthCard } from "@/shared/components/layout/auth-card";

export default async function RegisterPage() {
  const t = await getTranslations("Register");

  return (
    <AuthCard title={t("title")} description={t("description")}>
      <RegisterForm />
    </AuthCard>
  );
}
