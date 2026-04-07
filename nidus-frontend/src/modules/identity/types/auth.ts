import { z } from "zod";
import { ApiStatus } from "@/core/types/api";

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "El correo es requerido.")
    .email("Formato de correo inválido."),
  password: z
    .string()
    .min(8, "La contraseña debe tener al menos 8 caracteres."),
});

export type LoginRequest = z.infer<typeof loginSchema>;
export type LoginFormData = LoginRequest;

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthActionResponse {
  status: ApiStatus;
  message: string | null;
}
