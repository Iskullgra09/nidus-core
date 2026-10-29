import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/core/i18n/routing";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/core/providers/theme-provider";
import {
  THEME_STORAGE_KEY,
  getServerThemeClass,
} from "@/core/providers/theme-config";

import "@/app/globals.css";

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Nidus Core",
  description: "Enterprise SaaS Architecture",
};

export default async function RootLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {
  const { locale } = await params;

  if (!routing.locales.includes(locale as (typeof routing.locales)[number])) {
    notFound();
  }

  const messages = await getMessages();
  const cookieStore = await cookies();
  const themeClass = getServerThemeClass(
    cookieStore.get(THEME_STORAGE_KEY)?.value,
  );

  return (
    <html
      lang={locale}
      className={themeClass}
      suppressHydrationWarning
    >
      <body
        className={`${geistMono.variable} antialiased bg-background text-foreground`}
        suppressHydrationWarning
      >
        <ThemeProvider disableTransitionOnChange>
          <NextIntlClientProvider messages={messages}>
            {children}
          </NextIntlClientProvider>
        </ThemeProvider>

        <Toaster
          position="top-right"
          richColors
          closeButton
          expand={false}
          duration={4000}
        />
      </body>
    </html>
  );
}
