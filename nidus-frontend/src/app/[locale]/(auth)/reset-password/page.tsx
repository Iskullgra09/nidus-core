import { getTranslations } from "next-intl/server";
import { redirect } from "next/navigation";
import { ResetPasswordForm } from "@/modules/identity/components/reset-password-form";
import { AuthCard } from "@/shared/components/layout/auth-card";

export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const t = await getTranslations("ResetPassword");
  const resolvedParams = await searchParams;
  const token =
    typeof resolvedParams.token === "string" ? resolvedParams.token : null;

  if (!token) {
    redirect("/login");
  }

  return (
    <AuthCard title={t("title")} description={t("description")}>
      <ResetPasswordForm token={token} />
    </AuthCard>
  );
}
