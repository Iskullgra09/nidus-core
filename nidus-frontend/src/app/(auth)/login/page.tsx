import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/ui/card";
import { LoginForm } from "@/modules/identity/components/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="absolute inset-0 z-[-1] opacity-30 pointer-events-none bg-[radial-gradient(circle_at_center,var(--color-primary)_0%,transparent_70%)] blur-3xl" />

      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-black tracking-tighter text-primary">
            NIDUS
          </h1>
          <p className="text-muted-foreground">Ecosistema Empresarial</p>
        </div>

        <Card className="border-border/50 shadow-xl backdrop-blur-sm bg-background/80">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Iniciar Sesión</CardTitle>
            <CardDescription>
              Ingresa tus credenciales para acceder a tu entorno.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
