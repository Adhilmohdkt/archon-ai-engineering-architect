import { Copy } from "lucide-react";

import type { ArchonResponse } from "@/types/archon";
import { Button } from "@/components/ui/button";

interface RunHeaderProps {
  run: ArchonResponse;
}

export default function RunHeader({ run }: RunHeaderProps) {
  function copyThreadId() {
    navigator.clipboard.writeText(run.thread_id);
  }

  const statusLabel = run.status.replaceAll("_", " ").toUpperCase();

  return (
    <div className="rounded-xl border bg-white shadow-sm">
      <div className="border-b px-5 py-5">
        <h1 className="text-xl font-semibold tracking-tight">
          {run.user_goal}
        </h1>
      </div>

      <div className="grid grid-cols-1 divide-y md:grid-cols-4 md:divide-x md:divide-y-0">
        {/* Run ID */}
        <div className="px-5 py-4">
          <p className="text-[11px] font-medium text-slate-500">
            Run ID
          </p>

          <div className="mt-2 flex items-center gap-2">
            <p className="truncate text-xs font-medium">
              {run.thread_id}
            </p>

            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0"
              onClick={copyThreadId}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {/* Status */}
        <div className="px-5 py-4">
          <p className="text-[11px] font-medium text-slate-500">
            Status
          </p>

          <div className="mt-2">
            <span
              className={`inline-flex rounded-md px-2.5 py-1 text-[10px] font-semibold ${
                run.status === "human_review_required"
                  ? "bg-amber-100 text-amber-700"
                  : run.status === "completed"
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-blue-100 text-blue-700"
              }`}
            >
              {statusLabel}
            </span>
          </div>
        </div>

        {/* Started */}
        <div className="px-5 py-4">
          <p className="text-[11px] font-medium text-slate-500">
            Started At
          </p>

          <p className="mt-2 text-xs text-slate-700">
            —
          </p>
        </div>

        {/* Updated */}
        <div className="px-5 py-4">
          <p className="text-[11px] font-medium text-slate-500">
            Updated At
          </p>

          <p className="mt-2 text-xs text-slate-700">
            —
          </p>
        </div>
      </div>
    </div>
  );
}