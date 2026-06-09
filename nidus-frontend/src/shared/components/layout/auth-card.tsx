import * as React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/ui/card";

interface AuthCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
  iconBgClass?: string;
  borderColorClass?: string;
}

export function AuthCard({
  title,
  description,
  children,
  icon,
  iconBgClass,
  borderColorClass = "border-border/50",
}: AuthCardProps) {
  return (
    <Card
      className={`w-full shadow-lg bg-background/60 backdrop-blur supports-backdrop-filter:bg-background/60 ${borderColorClass}`}
    >
      <CardHeader className="space-y-1 text-center pb-6">
        {icon && iconBgClass && (
          <div
            className={`mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full ${iconBgClass}`}
          >
            {icon}
          </div>
        )}
        <CardTitle className="text-3xl font-bold tracking-tight text-foreground">
          {title}
        </CardTitle>
        {description && (
          <CardDescription className="text-muted-foreground">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
