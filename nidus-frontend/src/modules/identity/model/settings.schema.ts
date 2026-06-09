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

export const getUpdateProfileSchema = (t: ValidationTranslator) =>
  z.object({
    fullName: z
      .string()
      .min(2, t("stringMin"))
      .max(100)
      .optional()
      .or(z.literal("")),
    language: z.enum(["es", "en"]),
    theme: z.enum(["light", "dark", "system"]),
  });
