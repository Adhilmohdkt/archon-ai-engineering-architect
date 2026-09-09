import type {
  ArchonRequest,
  ArchonResponse,
  HumanResumeRequest,
} from "@/types/archon";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function startArchon(
  request: ArchonRequest
): Promise<ArchonResponse> {
  const response = await fetch(`${API_URL}/api/v1/archon`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error("Failed to start Archon");
  }

  return response.json();
}

export async function getArchonRun(
  threadId: string
): Promise<ArchonResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/archon/${threadId}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch Archon run");
  }

  return response.json();
}

export async function resumeArchon(
  threadId: string,
  request: HumanResumeRequest
): Promise<ArchonResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/archon/${threadId}/resume`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to resume Archon");
  }

  return response.json();
}