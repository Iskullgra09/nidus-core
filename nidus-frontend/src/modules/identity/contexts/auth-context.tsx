"use client";

import * as React from "react";
import { UserProfileResponse } from "../types/user";

interface AuthContextType {
  user: UserProfileResponse | null;
  isLoading: boolean;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({
  children,
  initialUser,
}: {
  children: React.ReactNode;
  initialUser: UserProfileResponse | null;
}) {
  const [user] = React.useState<UserProfileResponse | null>(initialUser);

  return (
    <AuthContext.Provider value={{ user, isLoading: false }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
