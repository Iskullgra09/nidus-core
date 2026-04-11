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
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/form";

import { OrganizationFormData } from "../types";
import { getOrganizationUpdateSchema } from "../model/org.schema";
import { ValidationTranslator } from "@/modules/identity/model/auth.schema";
import { updateOrganizationAction } from "../actions/org";
import { OrganizationResponse } from "@/modules/organization/types/organization";

interface OrgSettingsFormProps {
  organization: OrganizationResponse;
}

export function OrganizationSettingsForm({
  organization,
}: OrgSettingsFormProps) {
  const router = useRouter();
  const tOrg = useTranslations("OrgSettings");
  const tVal = useTranslations("Validation");

  const form = useForm<OrganizationFormData>({
    resolver: zodResolver(
      getOrganizationUpdateSchema(tVal as ValidationTranslator),
    ),
    defaultValues: {
      name: organization.name,
      slug: organization.slug,
    },
  });

  async function onSubmit(values: OrganizationFormData) {
    const payload: Partial<OrganizationFormData> = {};
    if (values.name !== organization.name) payload.name = values.name;
    if (values.slug !== organization.slug) payload.slug = values.slug;

    if (Object.keys(payload).length === 0) {
      toast.info(tOrg("noChangesDetected"));
      return;
    }

    const result = await updateOrganizationAction(organization.id, payload);

    if (result.status === "success") {
      toast.success(result.message || tOrg("successMessage"));
      router.refresh();
    } else {
      toast.error(result.message);
    }
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-5 max-w-md"
      >
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tOrg("orgNameLabel")}</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="slug"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{tOrg("orgSlugLabel")}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  onChange={(e) => {
                    const formatted = e.target.value
                      .toLowerCase()
                      .replace(/\s+/g, "-");
                    field.onChange(formatted);
                  }}
                />
              </FormControl>
              <FormDescription>{tOrg("orgSlugDescription")}</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting
            ? tOrg("savingChanges")
            : tOrg("saveChanges")}
        </Button>
      </form>
    </Form>
  );
}
