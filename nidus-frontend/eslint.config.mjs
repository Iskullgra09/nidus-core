import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

/**
 * Nidus Core module boundaries (foundation template).
 * core → shared/modules: forbidden
 * shared → modules: forbidden (platform primitives only)
 * organization → identity/components: forbidden (use access for IAM UI)
 */
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
  {
    files: ["src/core/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/modules/*", "@/modules/**"],
              message:
                "core/ is platform infrastructure and must not import feature modules.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["src/shared/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/modules/*", "@/modules/**"],
              message:
                "shared/ must stay feature-agnostic. Put feature UI in modules/; scopes/permissions live in shared/access.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["src/modules/organization/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: [
                "@/modules/identity/components/*",
                "@/modules/identity/components/**",
              ],
              message:
                "organization must not import identity UI. Use @/modules/access for IAM components.",
            },
          ],
        },
      ],
    },
  },
]);

export default eslintConfig;
