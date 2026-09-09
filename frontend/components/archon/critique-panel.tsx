"use client";

import { AlertTriangle, CheckCircle2 } from "lucide-react";

import type { Critique } from "@/types/archon";

interface CritiquePanelProps {
  critique?: Critique;
}

export default function CritiquePanel({
  critique,
}: CritiquePanelProps) {
  if (!critique) {
    return null;
  }

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-violet-600">
            Critic Agent
          </p>

          <h2 className="mt-2 text-lg font-semibold text-slate-900">
            Architecture Review
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Review the issues identified by Archon&apos;s critic before making
            your decision.
          </p>
        </div>

        {critique.approved ? (
          <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
            <CheckCircle2 className="h-4 w-4" />
            Approved
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700">
            <AlertTriangle className="h-4 w-4" />
            Revision Required
          </div>
        )}
      </div>

      {critique.issues.length > 0 ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-slate-900">
            Issues identified
          </h3>

          <div className="mt-3 space-y-3">
            {critique.issues.map((issue, index) => (
              <div
                key={index}
                className="flex gap-3 rounded-lg border border-amber-100 bg-amber-50/50 p-4"
              >
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />

                <p className="text-sm leading-6 text-slate-700">
                  {issue}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-lg border border-emerald-100 bg-emerald-50 p-4">
          <p className="text-sm text-emerald-700">
            The critic did not identify any issues with the proposed
            architecture.
          </p>
        </div>
      )}

      {critique.target_agent && (
        <div className="mt-5 rounded-lg border bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Revision Target
          </p>

          <p className="mt-1 text-sm font-semibold capitalize text-slate-800">
            {critique.target_agent} Agent
          </p>
        </div>
      )}

      <div className="mt-5 flex items-center gap-2 text-xs text-slate-500">
        <span className="font-medium">
          Revision required:
        </span>

        <span
          className={
            critique.revision_required
              ? "font-semibold text-amber-600"
              : "font-semibold text-emerald-600"
          }
        >
          {critique.revision_required
            ? "Yes"
            : "No"}
        </span>
      </div>
    </div>
  );
}