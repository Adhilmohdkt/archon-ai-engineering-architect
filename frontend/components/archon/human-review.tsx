"use client";

import { useState } from "react";
import {
  Check,
  RotateCcw,
  X,
  Loader2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { resumeArchon } from "@/lib/api";

import type {
  ArchonResponse,
  HumanResumeRequest,
} from "@/types/archon";

interface HumanReviewProps {
  run: ArchonResponse;
  onUpdated: (run: ArchonResponse) => void;
}

export default function HumanReview({
  run,
  onUpdated,
}: HumanReviewProps) {
  const [decision, setDecision] =
    useState<HumanResumeRequest["decision"]>("approve");

  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!run.thread_id || submitting) {
      return;
    }

    setSubmitting(true);
    setError("");

    /*
     * Immediately tell the dashboard that Archon is processing.
     * The backend remains the source of truth; this only improves
     * perceived responsiveness while the resume request is running.
     */
    onUpdated({
      ...run,
      status: "running",
      human_feedback: feedback.trim() || undefined,
    });

    try {
      const updatedRun = await resumeArchon(
        run.thread_id,
        {
          decision,
          feedback: feedback.trim() || undefined,
        }
      );

      onUpdated(updatedRun);
    } catch (err) {
      /*
       * Restore the previous state if the request fails.
       */
      onUpdated(run);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to submit decision"
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-violet-600">
          Human Review
        </p>

        <h2 className="mt-2 text-lg font-semibold text-slate-900">
          Review Archon&apos;s architecture
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Review the proposed architecture before Archon
          generates the final blueprint.
        </p>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <DecisionButton
          active={decision === "approve"}
          onClick={() => setDecision("approve")}
          icon={<Check className="h-4 w-4" />}
          title="Approve"
          description="Continue with the current architecture."
          disabled={submitting}
        />

        <DecisionButton
          active={decision === "revise"}
          onClick={() => setDecision("revise")}
          icon={<RotateCcw className="h-4 w-4" />}
          title="Revise"
          description="Send feedback and ask Archon to revise."
          disabled={submitting}
        />

        <DecisionButton
          active={decision === "reject"}
          onClick={() => setDecision("reject")}
          icon={<X className="h-4 w-4" />}
          title="Reject"
          description="Reject this architecture."
          disabled={submitting}
        />
      </div>

      <div className="mt-6">
        <label
          htmlFor="human-feedback"
          className="text-sm font-semibold text-slate-900"
        >
          Feedback
        </label>

        <textarea
          id="human-feedback"
          value={feedback}
          onChange={(event) =>
            setFeedback(event.target.value)
          }
          disabled={submitting}
          placeholder={
            decision === "approve"
              ? "Optional feedback..."
              : "Describe what you want Archon to change..."
          }
          className="mt-2 min-h-32 w-full resize-none rounded-lg border bg-slate-50 p-4 text-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-100 disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-sm text-red-700">
            {error}
          </p>
        </div>
      )}

      <div className="mt-5 flex items-center justify-between">
        {submitting ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin text-violet-600" />
            <span>
              Archon is processing your decision...
            </span>
          </div>
        ) : (
          <div />
        )}

        <Button
          onClick={handleSubmit}
          disabled={submitting}
          className="bg-violet-600 hover:bg-violet-500"
        >
          {submitting
            ? "Processing..."
            : "Submit Decision"}
        </Button>
      </div>
    </div>
  );
}

function DecisionButton({
  active,
  onClick,
  icon,
  title,
  description,
  disabled,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  title: string;
  description: string;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg border p-4 text-left transition ${
        active
          ? "border-violet-400 bg-violet-50 ring-2 ring-violet-100"
          : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
      } ${
        disabled
          ? "cursor-not-allowed opacity-60"
          : ""
      }`}
    >
      <div className="flex items-center gap-2">
        <span
          className={`flex h-8 w-8 items-center justify-center rounded-md ${
            active
              ? "bg-violet-600 text-white"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {icon}
        </span>

        <span className="text-sm font-semibold text-slate-900">
          {title}
        </span>
      </div>

      <p className="mt-2 text-xs leading-5 text-slate-500">
        {description}
      </p>
    </button>
  );
}