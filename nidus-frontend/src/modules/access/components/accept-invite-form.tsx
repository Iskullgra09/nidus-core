"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { useRouter } from "@/core/i18n/routing";
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
import { acceptInvitationAction } from "../actions/invitations";

type ValidationKeys = "passwordMin" | "passwordsDoNotMatch";

const createAcceptSchema = (t: (key: ValidationKeys) => string) =>
  z
    .object({
      password: z.string().min(8, { message: t("passwordMin") }),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t("passwordsDoNotMatch"),
      path: ["confirmPassword"],
    });

type AcceptFormValues = z.infer<ReturnType<typeof createAcceptSchema>>;

interface AcceptInviteFormProps {
  token: string;
}

export function AcceptInviteForm({ token }: AcceptInviteFormProps) {
  const t = useTranslations("InviteAccept");
  const tVal = useTranslations("Validation");
  const router = useRouter();

  const [isPending, setIsPending] = React.useState(false);

  const form = useForm<AcceptFormValues>({
    resolver: zodResolver(createAcceptSchema((key) => tVal(key))),
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (values: AcceptFormValues) => {
    setIsPending(true);
    const result = await acceptInvitationAction({
      token,
      password: values.password,
    });
    setIsPending(false);

    if (result.status === "success") {
      toast.success(t("successMessage"));
      router.push("/login");
    } else {
      toast.error(result.message);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 mt-6">
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("passwordLabel")}</FormLabel>
              <FormControl>
                <PasswordInput
                  placeholder={t("passwordPlaceholder")}
                  autoComplete="new-password"
                  {...field}
                />
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
              <FormLabel>{t("confirmPasswordLabel")}</FormLabel>
              <FormControl>
                <PasswordInput
                  placeholder={t("confirmPasswordPlaceholder")}
                  autoComplete="new-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isPending ? t("submittingButton") : t("submitButton")}
        </Button>
      </form>
    </Form>
  );
}
