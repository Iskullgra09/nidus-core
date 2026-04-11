"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { PlusIcon, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/shared/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";
import { Input } from "@/shared/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select";

import {
  getInviteMemberSchema,
  InviteMemberFormData,
} from "../model/member.schema";
import { inviteMemberAction, getAvailableRoles } from "../actions/members";
import { RoleResponse } from "@/modules/identity/types/roles";

export function InviteMemberButton() {
  const t = useTranslations("SettingsMembers");
  const tVal = useTranslations("Validation");
  const [open, setOpen] = React.useState(false);
  const [roles, setRoles] = React.useState<RoleResponse[]>([]);
  const [isLoadingRoles, setIsLoadingRoles] = React.useState(false);

  const form = useForm<InviteMemberFormData>({
    resolver: zodResolver(
      getInviteMemberSchema((key: string) =>
        tVal(key as Parameters<typeof tVal>[0]),
      ),
    ),
    defaultValues: { email: "", role_id: "" },
  });

  React.useEffect(() => {
    if (open) {
      setIsLoadingRoles(true);
      getAvailableRoles().then((data) => {
        setRoles(data);
        setIsLoadingRoles(false);
      });
    }
  }, [open]);

  async function onSubmit(data: InviteMemberFormData) {
    const res = await inviteMemberAction(data);
    if (res.status === "success") {
      toast.success(res.message);
      setOpen(false);
      form.reset();
    } else {
      toast.error(res.message);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <PlusIcon className="mr-2 h-4 w-4" />
          {t("inviteButton")}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-106.25">
        <DialogHeader>
          <DialogTitle>{t("inviteButton")}</DialogTitle>
          <DialogDescription>{t("description")}</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("tableHeaderName")}</FormLabel>
                  <FormControl>
                    <Input placeholder="email@example.com" {...field} />
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
                  <FormLabel>{t("tableHeaderRole")}</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue
                          placeholder={isLoadingRoles ? "..." : "Select a role"}
                        />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {roles.map((role) => (
                        <SelectItem key={role.id} value={role.id}>
                          {role.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                {t("inviteButton")}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
