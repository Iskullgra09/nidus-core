"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { Link } from "@/core/i18n/routing";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";

import { ForgotPasswordFormData } from "../types/auth";
import { getForgotPasswordSchema } from "../model/password.schema";
import { ValidationTranslator } from "../model/auth.schema";
import { forgotPasswordAction } from "../actions/auth";

export function ForgotPasswordForm() {
  const tForgot = useTranslations("ForgotPassword");
  const tAuth = useTranslations("Auth");
  const tVal = useTranslations("Validation");

  const form = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(
      getForgotPasswordSchema(tVal as ValidationTranslator),
    ),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: ForgotPasswordFormData) {
    const result = await forgotPasswordAction(values);

    if (result.status === "success") {
      toast.success(result.message);
      form.reset();
    } else {
      toast.error(result.message);
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
            ? tForgot("submittingButton")
            : tForgot("submitButton")}
        </Button>
        <div className="text-center mt-4">
          <Link href="/login" className="text-sm text-primary hover:underline">
            {tForgot("backToLogin")}
          </Link>
        </div>
      </form>
    </Form>
  );
}
