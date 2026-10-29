"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { ModalWrapper } from "@/shared/components/layout/modal-wrapper";
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

import { RoleResponse } from "../types/roles";
import { inviteMemberAction } from "../actions/invitations";

type ValidationKeys = "invalidEmail" | "requiredRole";

const createInviteSchema = (t: (key: ValidationKeys) => string) =>
  z.object({
    email: z.string().email({ message: t("invalidEmail") }),
    role_id: z.string().uuid({ message: t("requiredRole") }),
  });

type InviteFormValues = z.infer<ReturnType<typeof createInviteSchema>>;

interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: (open: boolean) => void;
  roles: RoleResponse[];
}

export function InviteMemberModal({
  isOpen,
  onClose,
  roles,
}: InviteMemberModalProps) {
  const t = useTranslations("Invitations");
  const tVal = useTranslations("Validation");
  const tCom = useTranslations("Common");

  const [isPending, setIsPending] = React.useState(false);

  const form = useForm<InviteFormValues>({
    resolver: zodResolver(createInviteSchema((key) => tVal(key))),
    defaultValues: {
      email: "",
      role_id: "",
    },
  });

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      form.reset();
    }
    onClose(open);
  };

  const onSubmit = async (values: InviteFormValues) => {
    setIsPending(true);
    const result = await inviteMemberAction({
      email: values.email,
      role_id: values.role_id,
    });
    setIsPending(false);

    if (result.status === "success") {
      toast.success(t("inviteSuccess", { email: values.email }));
      handleOpenChange(false);
    } else {
      toast.error(result.message);
    }
  };

  const assignableRoles = roles.filter((r) => r.name.toLowerCase() !== "owner");

  return (
    <ModalWrapper
      isOpen={isOpen}
      onClose={handleOpenChange}
      title={t("inviteMember")}
      description={t("inviteDescription")}
      size="sm"
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("emailLabel")}</FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("emailPlaceholder")}
                    autoComplete="off"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="role_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("roleLabel")}</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder={t("rolePlaceholder")} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {assignableRoles.map((role) => (
                      <SelectItem key={role.id} value={role.id}>
                        <span className="capitalize">{role.name}</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isPending}
            >
              {tCom("cancel")}
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t("sendInvite")}
            </Button>
          </div>
        </form>
      </Form>
    </ModalWrapper>
  );
}
