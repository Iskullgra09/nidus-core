import { z } from "zod";
import { ValidationTranslator } from "@/modules/identity/model/auth.schema";

export const getOrganizationUpdateSchema = (t: ValidationTranslator) =>
  z.object({
    name: z.string().min(3, t("orgNameMin")).max(100),
    slug: z
      .string()
      .min(3, t("orgNameMin"))
      .regex(/^[a-z0-9-]+$/, t("invalidSlug")),
  });
