import { z } from "zod";
import { ValidationTranslator } from "./auth.schema";

export const getChangePasswordSchema = (t: ValidationTranslator) =>
  z
    .object({
      currentPassword: z.string().min(1, t("passwordMin")),
      newPassword: z.string().min(8, t("passwordMin")),
      confirmNewPassword: z.string(),
    })
    .refine((data) => data.newPassword === data.confirmNewPassword, {
      message: t("passwordsDoNotMatch"),
      path: ["confirmNewPassword"],
    });
