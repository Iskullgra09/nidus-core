import { z } from "zod";

export type ValidationTranslator = (
  key: keyof IntlMessages["Validation"],
) => string;

export const getLoginSchema = (t: ValidationTranslator) =>
  z.object({
    email: z.string().min(1, t("emailRequired")).email(t("emailInvalid")),
    password: z.string().min(8, t("passwordMin")),
  });
