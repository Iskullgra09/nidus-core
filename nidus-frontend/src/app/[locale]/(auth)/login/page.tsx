import { getTranslations } from "next-intl/server";
import { LoginForm } from "@/modules/identity/components/login-form";
import { AuthCard } from "@/shared/components/layout/auth-card";

export default async function LoginPage() {
  const t = await getTranslations("Auth");

  return (
    <AuthCard title={t("loginTitle")} description={t("loginDescription")}>
      <LoginForm />
    </AuthCard>
  );
}
