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

import { RegisterFormData } from "../types/auth";
import { getRegisterSchema } from "../model/register.schema";
import { ValidationTranslator } from "../model/auth.schema";
import { registerAction } from "../actions/auth";

export function RegisterForm() {
  const router = useRouter();
  const tReg = useTranslations("Register");
  const tAuth = useTranslations("Auth");
  const tVal = useTranslations("Validation");

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(getRegisterSchema(tVal as ValidationTranslator)),
    defaultValues: { organization_name: "", email: "", password: "" },
  });

  async function onSubmit(values: RegisterFormData) {
    const result = await registerAction(values);

    if (result.status === "success") {
      toast.success(result.message);
      router.push("/login");
    } else {
      toast.error(result.message);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="organization_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tReg("orgNameLabel")}</FormLabel>
              <FormControl>
                <Input placeholder={tReg("orgNamePlaceholder")} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

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
              <FormLabel>{tAuth("passwordLabel")}</FormLabel>
              <FormControl>
                <PasswordInput
                  placeholder={tAuth("passwordPlaceholder")}
                  type="password"
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
            ? tReg("submittingButton")
            : tReg("submitButton")}
        </Button>

        <div className="text-center mt-4">
          <Link href="/login" className="text-sm text-primary hover:underline">
            {tReg("loginLink")}
          </Link>
        </div>
      </form>
    </Form>
  );
}
