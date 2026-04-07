import * as React from "react";
import { Button } from "@/shared/ui/button";
import { logoutAction } from "@/modules/identity/actions/auth";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-50 flex h-14 items-center border-b border-border/50 bg-background/95 px-4 backdrop-blur supports-backdrop-filter:bg-background/60">
        <div className="flex items-center gap-4 font-bold">
          <span className="text-primary text-lg tracking-tighter">NIDUS</span>
          <span className="text-muted-foreground/50">/</span>
          <span className="text-sm font-medium">Acme Corp</span>
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">admin@nidus.com</span>

          <form action={logoutAction}>
            <Button
              variant="ghost"
              size="sm"
              className="text-muted-foreground hover:text-foreground"
            >
              Salir
            </Button>
          </form>
        </div>
      </header>

      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
