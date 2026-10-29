"use client";

import * as React from "react";
import { useRouter } from "@/core/i18n/routing";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";

type UploadResult = { status: "success" | "error"; message: string | null };

interface AvatarUploadProps {
  imageUrl: string | null | undefined;
  fallback: string;
  labels: {
    title: string;
    hint: string;
    upload: string;
    remove: string;
    uploading: string;
  };
  onUpload: (file: File) => Promise<UploadResult>;
  onRemove: () => Promise<UploadResult>;
}

export function AvatarUpload({
  imageUrl,
  fallback,
  labels,
  onUpload,
  onRemove,
}: AvatarUploadProps) {
  const router = useRouter();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [busy, setBusy] = React.useState(false);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    try {
      const result = await onUpload(file);
      if (result.status === "success") {
        toast.success(result.message || labels.upload);
        router.refresh();
      } else {
        toast.error(result.message);
      }
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function handleRemove() {
    setBusy(true);
    try {
      const result = await onRemove();
      if (result.status === "success") {
        toast.success(result.message || labels.remove);
        router.refresh();
      } else {
        toast.error(result.message);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center gap-4">
      <Avatar className="size-16 border border-border/50">
        {imageUrl ? <AvatarImage src={imageUrl} alt="" /> : null}
        <AvatarFallback className="bg-primary/10 text-primary text-lg font-medium">
          {fallback}
        </AvatarFallback>
      </Avatar>
      <div className="space-y-2">
        <div>
          <p className="text-sm font-medium">{labels.title}</p>
          <p className="text-xs text-muted-foreground">{labels.hint}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={busy}
            onClick={() => inputRef.current?.click()}
          >
            {busy ? labels.uploading : labels.upload}
          </Button>
          {imageUrl ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={busy}
              onClick={handleRemove}
            >
              {labels.remove}
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
