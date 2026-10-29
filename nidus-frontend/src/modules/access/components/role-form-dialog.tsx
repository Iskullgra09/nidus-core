"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { ModalWrapper } from "@/shared/components/layout/modal-wrapper";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Checkbox } from "@/shared/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";

import { RoleResponse } from "../types/roles";
import { ScopeResponse } from "../types/scopes-catalog";
import { createRoleAction, updateRoleAction } from "../actions/roles";

const roleSchema = z.object({
  name: z.string().min(2),
  description: z.string().optional(),
  scopes: z.array(z.string()).min(1),
});

type RoleFormValues = z.infer<typeof roleSchema>;

interface RoleFormDialogProps {
  isOpen: boolean;
  onClose: (open: boolean) => void;
  scopes: ScopeResponse[];
  role?: RoleResponse | null;
}

export function RoleFormDialog({
  isOpen,
  onClose,
  scopes,
  role,
}: RoleFormDialogProps) {
  const t = useTranslations("SettingsRoles");
  const tCom = useTranslations("Common");
  const [isPending, setIsPending] = React.useState(false);

  const form = useForm<RoleFormValues>({
    resolver: zodResolver(roleSchema),
    defaultValues: {
      name: role?.name ?? "",
      description: role?.description ?? "",
      scopes: role?.scopes ?? [],
    },
  });

  React.useEffect(() => {
    form.reset({
      name: role?.name ?? "",
      description: role?.description ?? "",
      scopes: role?.scopes ?? [],
    });
  }, [role, form, isOpen]);

  const selectedScopes = useWatch({ control: form.control, name: "scopes" }) ?? [];

  const groupedScopes = React.useMemo(() => {
    return scopes.reduce<Record<string, ScopeResponse[]>>((acc, scope) => {
      acc[scope.group] = acc[scope.group] ? [...acc[scope.group], scope] : [scope];
      return acc;
    }, {});
  }, [scopes]);

  const handleOpenChange = (open: boolean) => {
    if (!open) form.reset();
    onClose(open);
  };

  const onSubmit = async (values: RoleFormValues) => {
    setIsPending(true);
    const payload = {
      name: values.name,
      description: values.description || null,
      scopes: values.scopes,
    };

    const result = role
      ? await updateRoleAction(role.id, payload)
      : await createRoleAction(payload);

    setIsPending(false);

    if (result.status === "success") {
      toast.success(result.message);
      handleOpenChange(false);
    } else {
      toast.error(result.message);
    }
  };

  const toggleScope = (scopeValue: string, checked: boolean) => {
    const current = form.getValues("scopes");
    form.setValue(
      "scopes",
      checked
        ? [...current, scopeValue]
        : current.filter((value) => value !== scopeValue),
      { shouldValidate: true },
    );
  };

  return (
    <ModalWrapper
      isOpen={isOpen}
      onClose={handleOpenChange}
      title={role ? t("editRole") : t("createRole")}
      description={t("formDescription")}
      size="md"
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("nameLabel")}</FormLabel>
                <FormControl>
                  <Input placeholder={t("namePlaceholder")} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("descriptionLabel")}</FormLabel>
                <FormControl>
                  <Input placeholder={t("descriptionPlaceholder")} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="scopes"
            render={() => (
              <FormItem>
                <FormLabel>{t("permissionsLabel")}</FormLabel>
                <div className="max-h-56 space-y-4 overflow-y-auto rounded-md border p-3">
                  {Object.entries(groupedScopes).map(([group, groupScopes]) => (
                    <div key={group} className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                        {group}
                      </p>
                      {groupScopes.map((scope) => (
                        <label
                          key={scope.value}
                          className="flex items-center gap-2 text-sm"
                        >
                          <Checkbox
                            checked={selectedScopes.includes(scope.value)}
                            onCheckedChange={(checked) =>
                              toggleScope(scope.value, checked === true)
                            }
                          />
                          <span className="font-mono text-xs">{scope.value}</span>
                        </label>
                      ))}
                    </div>
                  ))}
                </div>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex justify-end gap-2 pt-2">
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
              {role ? t("saveRole") : t("createRoleButton")}
            </Button>
          </div>
        </form>
      </Form>
    </ModalWrapper>
  );
}
