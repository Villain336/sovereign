import { useApi, apiPost } from "../hooks/useApi";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Bot, Play, Square, Activity, Shield, FileCheck, Cpu } from "lucide-react";
import type { AgentState } from "../types/api";

const typeIcons: Record<string, typeof Bot> = {
  sentinel: Shield,
  vanguard: Activity,
  compliance: FileCheck,
  orchestrator: Cpu,
};

const typeColors: Record<string, string> = {
  sentinel: "text-blue-400",
  vanguard: "text-red-400",
  compliance: "text-emerald-400",
  orchestrator: "text-purple-400",
};

const statusConfig: Record<string, { color: string; bg: string }> = {
  running: { color: "text-emerald-400", bg: "bg-emerald-600" },
  idle: { color: "text-zinc-400", bg: "bg-zinc-600" },
  stopped: { color: "text-red-400", bg: "bg-red-600" },
  error: { color: "text-red-400", bg: "bg-red-600" },
  awaiting_approval: { color: "text-amber-400", bg: "bg-amber-600" },
};

export function AgentsView() {
  const { data, loading, refetch } = useApi<{ agents: AgentState[]; total: number; running: number }>("/api/agents");

  if (loading || !data) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading agents...</div>;
  }

  const handleAction = async (agentId: string, action: string) => {
    try {
      await apiPost(`/api/agents/${agentId}/action`, { action });
      refetch();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Bot className="h-5 w-5 text-blue-400" />
        <h2 className="text-lg font-semibold text-zinc-100">Agent Pool</h2>
        <Badge variant="outline" className="border-zinc-700 text-zinc-400">
          {data.running}/{data.total} running
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.agents.map((agent) => {
          const Icon = typeIcons[agent.agent_type] || Bot;
          const typeColor = typeColors[agent.agent_type] || "text-zinc-400";
          const config = statusConfig[agent.status] || statusConfig.stopped;

          return (
            <Card key={agent.agent_id} className="border-zinc-800 bg-zinc-900">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-zinc-800 ${typeColor}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-zinc-100">{agent.name}</h3>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge variant="outline" className={`text-xs ${typeColor} border-zinc-700`}>
                          {agent.agent_type}
                        </Badge>
                        <Badge className={`${config.bg} text-white text-xs`}>
                          {agent.status}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div>
                    {agent.status === "running" ? (
                      <button
                        className="p-1.5 rounded bg-zinc-800 hover:bg-red-900 text-zinc-400 hover:text-red-400 transition-colors"
                        onClick={() => handleAction(agent.agent_id, "stop")}
                        title="Stop agent"
                      >
                        <Square className="h-3.5 w-3.5" />
                      </button>
                    ) : (
                      <button
                        className="p-1.5 rounded bg-zinc-800 hover:bg-emerald-900 text-zinc-400 hover:text-emerald-400 transition-colors"
                        onClick={() => handleAction(agent.agent_id, "start")}
                        title="Start agent"
                      >
                        <Play className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-xs text-zinc-500 mt-3">{agent.description}</p>

                <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                  <div className="bg-zinc-800 rounded px-2 py-1.5">
                    <span className="text-zinc-500">Actions:</span>
                    <span className="text-zinc-200 ml-1 font-mono">{agent.actions_taken.toLocaleString()}</span>
                  </div>
                  <div className="bg-zinc-800 rounded px-2 py-1.5">
                    <span className="text-zinc-500">Last active:</span>
                    <span className="text-zinc-200 ml-1">
                      {agent.last_action_at
                        ? new Date(agent.last_action_at).toLocaleTimeString()
                        : "N/A"}
                    </span>
                  </div>
                </div>

                {agent.current_task && (
                  <div className="mt-2 text-xs text-zinc-500 bg-zinc-800 rounded px-2 py-1.5">
                    <span className="text-zinc-600">Task:</span>{" "}
                    <span className="text-zinc-300">{agent.current_task}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
