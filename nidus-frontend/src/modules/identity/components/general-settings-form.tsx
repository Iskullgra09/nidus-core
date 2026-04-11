"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select";

import { UpdateProfileFormData, UserProfileResponse } from "../types/user";
import { getUpdateProfileSchema } from "../model/settings.schema";
import { ValidationTranslator } from "../model/auth.schema";
import { updateProfileAction } from "../actions/user";

interface GeneralSettingsFormProps {
  user: UserProfileResponse;
}

export function GeneralSettingsForm({ user }: GeneralSettingsFormProps) {
  const router = useRouter();
  const tSet = useTranslations("Settings");
  const tVal = useTranslations("Validation");

  const form = useForm<UpdateProfileFormData>({
    resolver: zodResolver(getUpdateProfileSchema(tVal as ValidationTranslator)),
    defaultValues: {
      fullName: user.full_name || "",
      language: user.preferences?.language || "en",
      theme: user.preferences?.theme || "system",
    },
  });

  async function onSubmit(values: UpdateProfileFormData) {
    const result = await updateProfileAction({
      full_name: values.fullName,
      preferences: {
        language: values.language,
        theme: values.theme,
      },
    });

    if (result.status === "success") {
      toast.success(result.message || tSet("profileSuccess"));
      router.refresh();
    } else {
      toast.error(result.message);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{tSet("generalTitle")}</h3>
        <p className="text-sm text-muted-foreground">
          {tSet("generalDescription")}
        </p>
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-5 max-w-md"
        >
          <FormItem>
            <FormLabel>{tSet("emailAddress")}</FormLabel>
            <FormControl>
              <Input
                type="email"
                value={user.email}
                disabled
                className="bg-muted/50 cursor-not-allowed"
              />
            </FormControl>
          </FormItem>

          <FormField
            control={form.control}
            name="fullName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{tSet("fullName")}</FormLabel>
                <FormControl>
                  <Input placeholder={tSet("fullNamePlaceholder")} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="language"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{tSet("language")}</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="theme"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{tSet("theme")}</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="light">
                        {tSet("themeLight")}
                      </SelectItem>
                      <SelectItem value="dark">{tSet("themeDark")}</SelectItem>
                      <SelectItem value="system">
                        {tSet("themeSystem")}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <Button type="submit" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting
              ? tSet("savingChanges")
              : tSet("saveChanges")}
          </Button>
        </form>
      </Form>
    </div>
  );
}
