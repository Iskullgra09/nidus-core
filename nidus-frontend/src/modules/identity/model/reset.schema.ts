import { z } from "zod";
import { ValidationTranslator } from "./auth.schema";

export const getResetPasswordSchema = (t: ValidationTranslator) =>
  z
    .object({
      password: z.string().min(8, t("passwordMin")),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t("passwordsDoNotMatch"),
      path: ["confirmPassword"],
    });
