import { getTranslations } from "next-intl/server";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { SecuritySettingsForm } from "@/modules/identity/components/security-settings-form";

export default async function SettingsPage() {
  const t = await getTranslations("Settings");

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="general">{t("tabGeneral")}</TabsTrigger>
          <TabsTrigger value="security">{t("tabSecurity")}</TabsTrigger>
        </TabsList>

        <TabsContent
          value="general"
          className="p-4 border rounded-md bg-card text-card-foreground shadow-sm"
        >
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Perfil General</h3>
            <p className="text-sm text-muted-foreground">
              Opciones de perfil en construcción...
            </p>
          </div>
        </TabsContent>

        <TabsContent
          value="security"
          className="p-6 border rounded-md bg-card text-card-foreground shadow-sm"
        >
          <SecuritySettingsForm />
        </TabsContent>
      </Tabs>
    </div>
  );
}
