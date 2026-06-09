import { z } from "zod";
import { ValidationTranslator } from "./auth.schema";

export const getForgotPasswordSchema = (t: ValidationTranslator) =>
  z.object({
    email: z.string().min(1, t("emailRequired")).email(t("emailInvalid")),
  });
