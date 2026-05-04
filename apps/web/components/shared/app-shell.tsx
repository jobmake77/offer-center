"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import clsx from "clsx";

import { primaryNavigation } from "@/lib/navigation";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand brand-panel">
          <span className="eyebrow">Career OS</span>
          <h1>Offer Center</h1>
          <p>Turn fragmented job hunting into a deliberate, evidence-driven operating rhythm.</p>
        </div>
        <section className="sidebar-panel workspace-panel">
          <div className="split">
            <strong>Workspace status</strong>
            <span className="pill neutral">Live</span>
          </div>
          <p className="muted">
            Keep one canonical resume, a filtered opportunity queue, and an application timeline in the same loop.
          </p>
        </section>
        <nav className="nav-list" aria-label="Primary">
          {primaryNavigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx("nav-link", { active: isActive })}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <section className="sidebar-panel sidebar-note">
          <p className="eyebrow">Operating principle</p>
          <p>Review fewer roles. Build higher-conviction applications. Close the loop from signal to action.</p>
        </section>
      </aside>
      <main className="content">
        <div className="content-inner">{children}</div>
      </main>
    </div>
  );
}
