"use client";

import {
  Bot,
  Clock3,
  FolderKanban,
  KeyRound,
  LayoutDashboard,
  Plus,
  Settings,
} from "lucide-react";

import { Button } from "@/components/ui/button";

interface SidebarProps {
  onNewRun?: () => void;
}

export default function Sidebar({ onNewRun }: SidebarProps) {
  return (
    <aside className="flex min-h-screen w-[220px] shrink-0 flex-col bg-[#0b1220] text-white">
      {/* Branding */}
      <div className="px-5 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/20 bg-white/10">
            <Bot className="h-5 w-5" />
          </div>

          <div>
            <div className="text-[17px] font-bold tracking-wide">
              ARCHON
            </div>

            <div className="text-[10px] text-slate-300">
              AI Architect
            </div>
          </div>
        </div>
      </div>

      {/* New architecture */}
      <div className="px-3">
        <Button
          onClick={onNewRun}
          className="w-full justify-start gap-3 bg-violet-600 text-white hover:bg-violet-500"
        >
          <Plus className="h-4 w-4" />
          New Architecture
        </Button>
      </div>

      {/* Navigation */}
      <nav className="mt-6 space-y-1 px-3">
        <SidebarItem
          icon={<LayoutDashboard className="h-4 w-4" />}
          label="Dashboard"
        />

        <SidebarItem
          icon={<FolderKanban className="h-4 w-4" />}
          label="Runs"
          active
        />

        <SidebarItem
          icon={<Clock3 className="h-4 w-4" />}
          label="History"
        />

        <SidebarItem
          icon={<Settings className="h-4 w-4" />}
          label="Settings"
        />

        <SidebarItem
          icon={<KeyRound className="h-4 w-4" />}
          label="API Keys"
        />
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* About */}
      <div className="mx-3 mb-4 rounded-lg border border-white/10 bg-white/5 p-4">
        <p className="text-xs font-semibold text-white">
          About Archon
        </p>

        <p className="mt-2 text-[11px] leading-5 text-slate-400">
          Archon is an AI architecture designer with human-in-the-loop
          review to produce robust software architectures.
        </p>
      </div>

      {/* User */}
      <div className="border-t border-white/10 p-3">
        <div className="flex items-center gap-3 rounded-lg bg-white/5 p-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold">
            AS
          </div>

          <div className="min-w-0">
            <p className="truncate text-xs font-semibold">
              Adhil Muhammed
            </p>

            <p className="truncate text-[10px] text-slate-400">
              admin@example.com
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

function SidebarItem({
  icon,
  label,
  active = false,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
}) {
  return (
    <button
      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
        active
          ? "bg-white/10 text-white"
          : "text-slate-300 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}