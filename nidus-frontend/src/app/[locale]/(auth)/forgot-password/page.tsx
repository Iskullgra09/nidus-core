import { getTranslations } from "next-intl/server";
import { ForgotPasswordForm } from "@/modules/identity/components/forgot-password-form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/ui/card";
import { LanguageSwitcher } from "@/core/i18n/components/language-switcher";

export default async function ForgotPasswordPage() {
  const t = await getTranslations("ForgotPassword");

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="absolute top-4 right-4 z-20">
        <LanguageSwitcher />
      </div>

      <div className="absolute inset-0 z-0 opacity-30 pointer-events-none bg-[radial-gradient(circle_at_center,var(--color-primary)_0%,transparent_70%)] blur-3xl" />

      <Card className="z-10 w-full max-w-md shadow-lg border-border/50 bg-background/60 backdrop-blur supports-backdrop-filter:bg-background/60">
        <CardHeader className="space-y-1 text-center pb-6">
          <CardTitle className="text-3xl font-bold tracking-tight text-foreground">
            {t("title")}
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            {t("description")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ForgotPasswordForm />
        </CardContent>
      </Card>
    </div>
  );
}
