/**
 * Barrel for identity auth actions.
 * Prefer importing from session / login / onboarding / password in new code.
 */
export {
  setSessionCookie,
  getCurrentUser,
  getUserOrganizations,
  logoutAction,
} from "./session";

export {
  loginAction,
  selectOrganizationAction,
  switchOrganizationAction,
} from "./login";

export { registerAction } from "./onboarding";

export { forgotPasswordAction, resetPasswordAction } from "./password";
