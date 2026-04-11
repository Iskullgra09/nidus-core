"use client";

import * as React from "react";
import { useAuth } from "@/modules/identity/contexts/auth-context";
import { hasScope } from "@/shared/lib/permissions";
import { NidusScope } from "@/modules/identity/types/scopes";

interface CanAccessProps {
  scope: NidusScope | string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function CanAccess({
  scope,
  children,
  fallback = null,
}: CanAccessProps) {
  const { user } = useAuth();

  if (!hasScope(user, scope)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
