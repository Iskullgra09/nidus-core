"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
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

import { ChangePasswordFormData } from "../types/user";
import { getChangePasswordSchema } from "../model/settings.schema";
import { ValidationTranslator } from "../model/auth.schema";
import { changePasswordAction } from "../actions/user";

export function SecuritySettingsForm() {
  const tSet = useTranslations("SettingsSecurity");
  const tVal = useTranslations("Validation");

  const form = useForm<ChangePasswordFormData>({
    resolver: zodResolver(
      getChangePasswordSchema(tVal as ValidationTranslator),
    ),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmNewPassword: "",
    },
  });

  async function onSubmit(values: ChangePasswordFormData) {
    const result = await changePasswordAction({
      current_password: values.currentPassword,
      new_password: values.newPassword,
    });

    if (result.status === "success") {
      toast.success(result.message);
      form.reset();
    } else {
      form.setError("currentPassword", {
        type: "server",
        message: result.message || undefined,
      });
      toast.error(result.message);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{tSet("title")}</h3>
        <p className="text-sm text-muted-foreground">{tSet("description")}</p>
      </div>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-4 max-w-md"
        >
          <FormField
            control={form.control}
            name="currentPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{tSet("currentPassword")}</FormLabel>
                <FormControl>
                  <PasswordInput type="password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="newPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{tSet("newPassword")}</FormLabel>
                <FormControl>
                  <PasswordInput type="password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="confirmNewPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{tSet("confirmNewPassword")}</FormLabel>
                <FormControl>
                  <PasswordInput type="password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting
              ? tSet("submittingPassword")
              : tSet("submitPassword")}
          </Button>
        </form>
      </Form>
    </div>
  );
}
