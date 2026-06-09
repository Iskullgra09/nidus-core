"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog";
import { cn } from "@/shared/lib/utils";

type ModalSize = "sm" | "md" | "lg" | "xl" | "full";

interface ModalWrapperProps {
  isOpen: boolean;
  onClose: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  size?: ModalSize;
  className?: string;
}

const sizeClasses: Record<ModalSize, string> = {
  sm: "sm:max-w-[425px]",
  md: "sm:max-w-[600px]",
  lg: "sm:max-w-[800px]",
  xl: "sm:max-w-[1024px]",
  full: "sm:max-w-[95vw] sm:h-[95vh]",
};

export function ModalWrapper({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = "md",
  className,
}: ModalWrapperProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={cn(sizeClasses[size], className)}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <div className="mt-4">{children}</div>
      </DialogContent>
    </Dialog>
  );
}
