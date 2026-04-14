import * as React from "react";
import { getTranslations } from "next-intl/server";
import { AlertCircle, CheckCircle2 } from "lucide-react";

import { Link } from "@/core/i18n/routing";
import { Button } from "@/shared/ui/button";
import { AuthCard } from "@/shared/components/layout/auth-card";
import { AcceptInviteForm } from "@/modules/identity/components/accept-invite-form";
import { verifyInvitationToken } from "@/modules/identity/actions/invitations";

interface InvitePageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function InvitePage({ searchParams }: InvitePageProps) {
  const t = await getTranslations("InviteAccept");

  const resolvedParams = await searchParams;
  const token =
    typeof resolvedParams.token === "string" ? resolvedParams.token : null;

  if (!token) {
    return (
      <AuthCard
        title={t("invalidTokenTitle")}
        description={t("invalidTokenDescription")}
        icon={<AlertCircle className="h-6 w-6 text-destructive" />}
        iconBgClass="bg-destructive/10"
        borderColorClass="border-destructive/20"
      >
        <div className="flex justify-center">
          <Button asChild variant="outline">
            <Link href="/">{t("backToHome")}</Link>
          </Button>
        </div>
      </AuthCard>
    );
  }

  const verification = await verifyInvitationToken(token);

  if (verification.status === "error") {
    const safeMessage = verification.message || t("invalidTokenDescription");
    const msg = safeMessage.toLowerCase();

    if (msg.includes("accepted") || msg.includes("aceptada")) {
      return (
        <AuthCard
          title="Invitación ya aceptada"
          description="Ya eres miembro de esta organización. Por favor, inicia sesión con tu cuenta."
          icon={<CheckCircle2 className="h-6 w-6 text-primary" />}
          iconBgClass="bg-primary/10"
          borderColorClass="border-primary/20"
        >
          <div className="flex justify-center">
            <Button asChild>
              <Link href="/login">Ir a Iniciar Sesión</Link>
            </Button>
          </div>
        </AuthCard>
      );
    }

    return (
      <AuthCard
        title={t("invalidTokenTitle")}
        description={safeMessage}
        icon={<AlertCircle className="h-6 w-6 text-destructive" />}
        iconBgClass="bg-destructive/10"
        borderColorClass="border-destructive/20"
      >
        <div className="flex justify-center">
          <Button asChild variant="outline">
            <Link href="/">{t("backToHome")}</Link>
          </Button>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard title={t("title")} description={t("description")}>
      <AcceptInviteForm token={token} />
    </AuthCard>
  );
}
