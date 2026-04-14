"use client";

import * as React from "react";
import { PlusIcon } from "lucide-react";
import { useTranslations } from "next-intl";

import { Button } from "@/shared/ui/button";
import { CanAccess } from "@/shared/components/auth/can-access";
import { NidusScope } from "@/modules/identity/types/scopes";
import { RoleResponse } from "@/modules/identity/types/roles";

import { InviteMemberModal } from "../../identity/components/invite-member-modal";

interface InviteMemberButtonProps {
  roles: RoleResponse[];
}

export function InviteMemberButton({ roles }: InviteMemberButtonProps) {
  const t = useTranslations("SettingsMembers");
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <>
      <CanAccess scope={NidusScope.MEMBER_INVITE}>
        <Button size="sm" onClick={() => setIsOpen(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          {t("inviteButton") || "Invite Member"}
        </Button>
      </CanAccess>
      <InviteMemberModal isOpen={isOpen} onClose={setIsOpen} roles={roles} />
    </>
  );
}
