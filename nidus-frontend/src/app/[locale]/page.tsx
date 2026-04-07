import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <Card className="w-87.5">
        <CardHeader>
          <CardTitle className="text-primary">Nidus Core v4</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            Si ves esto en azul eléctrico y con bordes suaves, la
            infraestructura está lista.
          </p>
          <Button>Probar Motor</Button>
        </CardContent>
      </Card>
    </main>
  );
}
