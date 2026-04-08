"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { useRouter } from "@/core/i18n/routing";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { PasswordInput } from "@/shared/ui/password-input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";

import { ResetPasswordFormData } from "../types/auth";
import { getResetPasswordSchema } from "../model/reset.schema";
import { ValidationTranslator } from "../model/auth.schema";
import { resetPasswordAction } from "../actions/auth";

export function ResetPasswordForm({ token }: { token: string }) {
  const router = useRouter();
  const tReset = useTranslations("ResetPassword");
  const tVal = useTranslations("Validation");

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(getResetPasswordSchema(tVal as ValidationTranslator)),
    defaultValues: { password: "", confirmPassword: "" },
  });

  async function onSubmit(values: ResetPasswordFormData) {
    const result = await resetPasswordAction({
      token,
      new_password: values.password,
    });

    if (result.status === "success") {
      toast.success(result.message);
      router.push("/login");
      router.refresh();
    } else {
      toast.error(result.message);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tReset("newPasswordLabel")}</FormLabel>
              <FormControl>
                <PasswordInput type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tReset("confirmPasswordLabel")}</FormLabel>
              <FormControl>
                <PasswordInput type="password" {...field} />
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
            ? tReset("submittingButton")
            : tReset("submitButton")}
        </Button>
      </form>
    </Form>
  );
}
