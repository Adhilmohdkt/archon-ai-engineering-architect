"use client";

import { useEffect, useState } from "react";
import { ChevronRight, Moon } from "lucide-react";

import {
  getArchonRun,
  startArchon,
} from "@/lib/api";

import type { ArchonResponse } from "@/types/archon";

import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/sidebar";
import RunHeader from "@/components/archon/run-header";
import AgentProgress from "@/components/archon/agent-progress";
import ArchitectureDiagramView from "@/components/archon/architecture-diagram";
import HumanReview from "@/components/archon/human-review";
import CritiquePanel from "@/components/archon/critique-panel";
import FinalBlueprint from "@/components/archon/final-blueprint";

export default function ArchonDashboard() {
  const [goal, setGoal] = useState("");
  const [run, setRun] =
    useState<ArchonResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleStart() {
    if (!goal.trim()) return;

    setLoading(true);
    setError("");

    try {
      const result = await startArchon({
        user_goal: goal,
      });

      setRun(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  function handleNewRun() {
    setRun(null);
    setGoal("");
    setError("");
  }

  useEffect(() => {
    if (!run?.thread_id) {
      return;
    }

    if (run.status !== "running") {
      return;
    }

    const interval = setInterval(
      async () => {
        try {
          const updatedRun =
            await getArchonRun(
              run.thread_id
            );

          setRun(updatedRun);

          if (
            updatedRun.status !==
            "running"
          ) {
            clearInterval(interval);
          }
        } catch (err) {
          console.error(
            "Polling failed:",
            err
          );
        }
      },
      1000
    );

    return () => {
      clearInterval(interval);
    };
  }, [
    run?.thread_id,
    run?.status,
  ]);

  return (
    <div className="flex min-h-screen bg-[#f8f9fc]">
      <Sidebar
        onNewRun={handleNewRun}
      />

      <main className="min-w-0 flex-1">
        {/* Top bar */}
        <header className="flex h-14 items-center justify-between border-b bg-white px-6">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span>Runs</span>

            <ChevronRight className="h-3.5 w-3.5" />

            <span className="font-medium text-slate-800">
              {run?.thread_id ??
                "New Architecture"}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full"
            >
              <Moon className="h-4 w-4" />
            </Button>

            <Button
              onClick={handleNewRun}
              className="bg-violet-600 hover:bg-violet-500"
            >
              + New Run
            </Button>
          </div>
        </header>

        <div className="mx-auto max-w-[1100px] px-6 py-7">
          {!run ? (
            <NewArchitecture
              goal={goal}
              setGoal={setGoal}
              loading={loading}
              error={error}
              onStart={handleStart}
            />
          ) : (
            <div className="space-y-5">

              {/* Run information */}
              <RunHeader run={run} />

              {/* Agent progress */}
              <AgentProgress run={run} />

              {/* Critic findings */}
              {run.critique && (
                <CritiquePanel
                  critique={run.critique}
                />
              )}

              {/* Human Review */}
              {run.status ===
                "human_review_required" && (
                <HumanReview
                  run={run}
                  onUpdated={setRun}
                />
              )}

              {/* Final Blueprint */}
              {run.status ===
                "completed" &&
                run.final_blueprint && (
                <FinalBlueprint
                  content={run.final_blueprint}
                />
              )}

              {/* Final Architecture Diagram */}
              {run.status ===
                "completed" &&
                run.diagram && (
                <div className="rounded-xl border bg-white p-6 shadow-sm">
                  <div className="mb-5">
                    <h2 className="text-lg font-semibold text-slate-900">
                      Architecture Diagram
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Visual representation of
                      the final architecture
                      generated by Archon.
                    </p>
                  </div>

                  <ArchitectureDiagramView
                    diagram={run.diagram}
                  />
                </div>
              )}

            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function NewArchitecture({
  goal,
  setGoal,
  loading,
  error,
  onStart,
}: {
  goal: string;
  setGoal: (value: string) => void;
  loading: boolean;
  error: string;
  onStart: () => void;
}) {
  return (
    <div className="mx-auto max-w-3xl pt-12">
      <p className="text-xs font-semibold tracking-wide text-violet-600">
        ARCHON AI ENGINEERING ARCHITECT
      </p>

      <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
        Design your system
      </h1>

      <p className="mt-2 text-sm text-slate-500">
        Describe what you want to build
        and Archon will design, critique,
        and refine the architecture.
      </p>

      <div className="mt-8 rounded-xl border bg-white p-6 shadow-sm">
        <label
          htmlFor="goal"
          className="text-sm font-semibold"
        >
          What do you want to build?
        </label>

        <textarea
          id="goal"
          value={goal}
          onChange={(e) =>
            setGoal(e.target.value)
          }
          placeholder="Example: Build a RAG-based customer support system for a SaaS company..."
          className="mt-3 min-h-44 w-full resize-none rounded-lg border bg-slate-50 p-4 text-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
        />

        <div className="mt-4 flex justify-end">
          <Button
            onClick={onStart}
            disabled={
              !goal.trim() ||
              loading
            }
            className="bg-violet-600 hover:bg-violet-500"
          >
            {loading
              ? "Starting..."
              : "Create Architecture"}
          </Button>
        </div>

        {error && (
          <p className="mt-4 text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}