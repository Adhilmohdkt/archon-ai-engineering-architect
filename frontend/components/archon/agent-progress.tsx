import {
  Check,
  Flag,
  UserRound,
} from "lucide-react";

import type { ArchonResponse } from "@/types/archon";

interface AgentProgressProps {
  run: ArchonResponse;
}

type AgentState = "completed" | "active" | "pending";

interface Agent {
  name: string;
  key: keyof ArchonResponse | "human";
}

export default function AgentProgress({
  run,
}: AgentProgressProps) {
  const agents: Agent[] = [
    {
      name: "Requirements Agent",
      key: "requirements",
    },
    {
      name: "Technology Agent",
      key: "technologyrecommendations",
    },
    {
      name: "Critic Agent",
      key: "critique",
    },
    {
      name: "Human Review",
      key: "human",
    },
    {
      name: "Finalizer Agent",
      key: "final_blueprint",
    },
  ];

  function getState(index: number): AgentState {
    if (run.status === "human_review_required") {
      if (index < 3) {
        return "completed";
      }

      if (index === 3) {
        return "active";
      }

      return "pending";
    }

    if (run.status === "completed") {
      return "completed";
    }

    if (index === 0 && run.requirements) {
      return "completed";
    }

    if (index === 1 && run.technologyrecommendations) {
      return "completed";
    }

    if (index === 2 && run.critique) {
      return "completed";
    }

    return "active";
  }

  return (
    <div className="rounded-xl border bg-white px-6 py-7 shadow-sm">
      <div className="flex items-start">
        {agents.map((agent, index) => {
          const state = getState(index);
          const isLast = index === agents.length - 1;

          return (
            <div
              key={agent.name}
              className="flex flex-1 items-start"
            >
              <div className="flex flex-col items-center">
                <AgentIcon state={state} />

                <p
                  className={`mt-2 max-w-[90px] text-center text-[11px] font-semibold leading-4 ${
                    state === "active"
                      ? "text-violet-600"
                      : "text-slate-700"
                  }`}
                >
                  {agent.name}
                </p>

                <p className="mt-1 text-[10px] text-slate-400">
                  {state === "completed"
                    ? "Completed"
                    : state === "active"
                      ? run.status ===
                        "human_review_required"
                        ? "Waiting for input"
                        : "In progress"
                      : "Pending"}
                </p>
              </div>

              {!isLast && (
                <div
                  className={`mt-4 h-px flex-1 ${
                    state === "completed"
                      ? "bg-emerald-400"
                      : "bg-slate-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AgentIcon({
  state,
}: {
  state: AgentState;
}) {
  if (state === "completed") {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-emerald-500 bg-emerald-50 text-emerald-600">
        <Check className="h-4 w-4" />
      </div>
    );
  }

  if (state === "active") {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-violet-400 bg-violet-50 text-violet-600">
        <UserRound className="h-4 w-4" />
      </div>
    );
  }

  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-slate-300 bg-slate-50 text-slate-500">
      <Flag className="h-4 w-4" />
    </div>
  );
}