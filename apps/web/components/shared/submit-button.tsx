"use client";

import { ReactNode } from "react";
import { useFormStatus } from "react-dom";

type SubmitButtonProps = {
  label: string;
  pendingLabel: string;
  variant?: "primary" | "secondary" | "ghost";
  pendingHint?: string;
  className?: string;
  children?: ReactNode;
};

export function SubmitButton({
  label,
  pendingLabel,
  variant = "primary",
  pendingHint,
  className = "",
  children
}: SubmitButtonProps) {
  const { pending } = useFormStatus();
  const variantClass = variant === "primary" ? "" : variant;

  return (
    <div className="submit-control">
      <button
        className={`button ${variantClass} ${pending ? "is-pending" : ""} ${className}`.trim()}
        type="submit"
        disabled={pending}
        aria-disabled={pending}
      >
        <span>{pending ? pendingLabel : label}</span>
      </button>
      {pending && pendingHint ? <p className="submit-hint">{pendingHint}</p> : null}
      {!pending && children ? <>{children}</> : null}
    </div>
  );
}
