"use client";

import * as React from "react";
import { Eye, EyeOff } from "lucide-react";
import { useTranslations } from "next-intl";
import { Input } from "@/shared/ui/input";
import { Button } from "@/shared/ui/button";
import { cn } from "@/core/lib/utils";

const PasswordInput = React.forwardRef<
  HTMLInputElement,
  React.ComponentProps<"input">
>(({ className, ...props }, ref) => {
  const [showPassword, setShowPassword] = React.useState(false);

  const t = useTranslations("Common");

  return (
    <div className="relative">
      <Input
        className={cn("pr-10", className)}
        ref={ref}
        {...props}
        type={showPassword ? "text" : "password"}
      />
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
        onClick={() => setShowPassword(!showPassword)}
        tabIndex={-1}
      >
        {showPassword ? (
          <EyeOff className="size-4 text-muted-foreground" aria-hidden="true" />
        ) : (
          <Eye className="size-4 text-muted-foreground" aria-hidden="true" />
        )}
        <span className="sr-only">
          {showPassword ? t("hidePassword") : t("showPassword")}
        </span>
      </Button>
    </div>
  );
});
PasswordInput.displayName = "PasswordInput";

export { PasswordInput };
