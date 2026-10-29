import { z } from "zod";
import type { ValidationTranslator } from "@/shared/validation/types";

export type { ValidationTranslator };

export const getLoginSchema = (t: ValidationTranslator) =>
  z.object({
    email: z.string().min(1, t("emailRequired")).email(t("emailInvalid")),
    password: z.string().min(8, t("passwordMin")),
  });
