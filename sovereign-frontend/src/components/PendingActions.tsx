import { useApi, apiPost } from "../hooks/useApi";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Clock, CheckCircle, XCircle } from "lucide-react";
import type { ResponseAction } from "../types/api";

const riskColors: Record<string, string> = {
  low: "bg-blue-600 text-white",
  medium: "bg-amber-600 text-white",
  high: "bg-orange-600 text-white",
  critical: "bg-red-600 text-white",
};

export function PendingActions() {
  const { data, loading, refetch } = useApi<{ actions: ResponseAction[]; total: number }>("/api/actions/pending");

  if (loading || !data) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading pending actions...</div>;
  }

  const handleDecision = async (actionId: string, decision: string) => {
    try {
      await apiPost(`/api/actions/${actionId}/decide`, { decision, decided_by: "operator" });
      refetch();
    } catch (err) {
      console.error(err);
    }
  };

  if (data.actions.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-amber-400" />
          <h2 className="text-lg font-semibold text-zinc-100">Pending Approvals</h2>
        </div>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
            <p className="text-zinc-400">No actions pending approval</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Clock className="h-5 w-5 text-amber-400" />
        <h2 className="text-lg font-semibold text-zinc-100">Pending Approvals</h2>
        <Badge variant="outline" className="border-amber-600 text-amber-400">{data.total} pending</Badge>
      </div>

      <div className="space-y-3">
        {data.actions.map((action) => (
          <Card key={action.id} className="border-amber-900/50 bg-zinc-900">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className={riskColors[action.risk_level]}>
                      {action.risk_level.toUpperCase()} RISK
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700 text-zinc-300">
                      {action.action_type}
                    </Badge>
                  </div>
                  <p className="text-sm text-zinc-200 mt-2">{action.description}</p>
                  <div className="mt-2 text-xs text-zinc-500">
                    Target: <span className="text-zinc-300 font-mono">{action.target}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  className="flex items-center gap-1.5 px-4 py-2 text-sm bg-emerald-600 hover:bg-emerald-700 text-white rounded transition-colors"
                  onClick={() => handleDecision(action.id, "approve")}
                >
                  <CheckCircle className="h-4 w-4" />
                  Approve
                </button>
                <button
                  className="flex items-center gap-1.5 px-4 py-2 text-sm bg-zinc-700 hover:bg-red-900 text-zinc-300 hover:text-red-300 rounded transition-colors"
                  onClick={() => handleDecision(action.id, "reject")}
                >
                  <XCircle className="h-4 w-4" />
                  Reject
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
