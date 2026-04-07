import { z } from "zod";
import { ValidationTranslator } from "./auth.schema";

export const getRegisterSchema = (t: ValidationTranslator) =>
  z.object({
    organization_name: z
      .string()
      .min(3, t("orgNameMin"))
      .max(50, t("orgNameRequired")),
    email: z.string().min(1, t("emailRequired")).email(t("emailInvalid")),
    password: z.string().min(8, t("passwordMin")),
  });
