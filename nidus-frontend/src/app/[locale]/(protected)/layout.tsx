import * as React from "react";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/modules/identity/actions/auth";
import { TopBar } from "@/shared/components/layout/top-bar";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <TopBar user={user} />
      <main className="flex-1 p-6 lg:p-8">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
