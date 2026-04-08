"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { useRouter, Link } from "@/core/i18n/routing";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { PasswordInput } from "@/shared/ui/password-input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";

import { LoginFormData } from "../types/auth";
import { getLoginSchema, ValidationTranslator } from "../model/auth.schema";
import { loginAction } from "../actions/auth";

export function LoginForm() {
  const router = useRouter();
  const tAuth = useTranslations("Auth");
  const tVal = useTranslations("Validation");

  const form = useForm<LoginFormData>({
    resolver: zodResolver(getLoginSchema(tVal as ValidationTranslator)),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: LoginFormData) {
    const result = await loginAction(values);

    if (result.status === "success") {
      toast.success(tAuth("successMessage"));
      router.push("/dashboard");
      router.refresh();
    } else {
      toast.error(result.message || tAuth("errorMessage"));
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tAuth("emailLabel")}</FormLabel>
              <FormControl>
                <Input
                  placeholder={tAuth("emailPlaceholder")}
                  type="email"
                  autoComplete="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <div className="flex items-center justify-between">
                <FormLabel>{tAuth("passwordLabel")}</FormLabel>
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  {tAuth("forgotPasswordLink")}
                </Link>
              </div>
              <FormControl>
                <PasswordInput
                  placeholder={tAuth("passwordPlaceholder")}
                  type="password"
                  autoComplete="current-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting
            ? tAuth("submittingButton")
            : tAuth("submitButton")}
        </Button>
        <div className="text-center mt-4 space-y-2">
          <p className="text-sm text-muted-foreground">
            {tAuth("noAccount")}{" "}
            <Link
              href="/register"
              className="text-primary font-medium hover:underline"
            >
              {tAuth("registerLink")}
            </Link>
          </p>
        </div>
      </form>
    </Form>
  );
}
