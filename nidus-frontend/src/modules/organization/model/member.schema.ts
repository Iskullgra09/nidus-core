import { z } from "zod";

export type ValidationTranslator = (key: string) => string;

export const getInviteMemberSchema = (t: ValidationTranslator) =>
  z.object({
    email: z.string().email(t("emailInvalid")),
    role_id: z.string().uuid("Invalid Role ID"),
  });

export type InviteMemberFormData = z.infer<
  ReturnType<typeof getInviteMemberSchema>
>;
