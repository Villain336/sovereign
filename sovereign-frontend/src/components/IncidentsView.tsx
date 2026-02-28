import { useState } from "react";
import { useApi } from "../hooks/useApi";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { AlertTriangle, ChevronDown, ChevronUp, Clock, Server } from "lucide-react";
import type { Incident } from "../types/api";

const severityColors: Record<string, string> = {
  critical: "bg-red-600 text-white",
  high: "bg-orange-600 text-white",
  medium: "bg-amber-600 text-white",
  low: "bg-blue-600 text-white",
  info: "bg-zinc-600 text-white",
};

const statusColors: Record<string, string> = {
  open: "border-red-500 text-red-400",
  investigating: "border-amber-500 text-amber-400",
  contained: "border-blue-500 text-blue-400",
  remediated: "border-emerald-500 text-emerald-400",
  closed: "border-zinc-500 text-zinc-400",
};

export function IncidentsView() {
  const { data, loading } = useApi<{ incidents: Incident[]; total: number }>("/api/incidents");
  const [expanded, setExpanded] = useState<string | null>(null);

  if (loading || !data) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading incidents...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-amber-400" />
        <h2 className="text-lg font-semibold text-zinc-100">Incidents</h2>
        <Badge variant="outline" className="border-zinc-700 text-zinc-400">{data.total}</Badge>
      </div>

      <div className="space-y-3">
        {data.incidents.map((incident) => (
          <Card key={incident.id} className="border-zinc-800 bg-zinc-900 hover:border-zinc-700 transition-colors">
            <CardContent className="p-4">
              <div
                className="flex items-start gap-3 cursor-pointer"
                onClick={() => setExpanded(expanded === incident.id ? null : incident.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className={severityColors[incident.severity]}>{incident.severity.toUpperCase()}</Badge>
                    <Badge variant="outline" className={statusColors[incident.status]}>{incident.status}</Badge>
                    {incident.requires_approval && (
                      <Badge variant="outline" className="border-amber-600 text-amber-400">HITL Required</Badge>
                    )}
                    <span className="text-xs text-zinc-500">
                      {new Date(incident.created_at).toLocaleString()}
                    </span>
                  </div>
                  <h3 className="text-sm font-medium text-zinc-100 mt-2">{incident.title}</h3>
                  <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{incident.description}</p>
                </div>
                <div className="text-zinc-500 pt-1">
                  {expanded === incident.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </div>
              </div>

              {expanded === incident.id && (
                <div className="mt-4 space-y-4">
                  <Separator className="bg-zinc-800" />

                  {/* Affected Assets */}
                  <div>
                    <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1">
                      <Server className="h-3 w-3" /> Affected Assets
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {incident.affected_assets.map((asset) => (
                        <Badge key={asset} variant="outline" className="border-zinc-700 text-zinc-300 text-xs">
                          {asset}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Response Actions */}
                  {incident.response_actions.length > 0 && (
                    <div>
                      <p className="text-xs text-zinc-500 mb-2">Response Actions</p>
                      <div className="space-y-2">
                        {incident.response_actions.map((action, i) => (
                          <div key={i} className="flex items-center gap-2 text-xs">
                            <Badge
                              variant="outline"
                              className={
                                action.status === "completed"
                                  ? "border-emerald-700 text-emerald-400"
                                  : action.status === "in_progress"
                                  ? "border-blue-700 text-blue-400"
                                  : "border-amber-700 text-amber-400"
                              }
                            >
                              {action.status}
                            </Badge>
                            <span className="text-zinc-300">{action.action}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Timeline */}
                  {incident.timeline.length > 0 && (
                    <div>
                      <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1">
                        <Clock className="h-3 w-3" /> Timeline
                      </p>
                      <div className="space-y-2 border-l-2 border-zinc-800 pl-4">
                        {incident.timeline.map((event, i) => (
                          <div key={i} className="text-xs">
                            <span className="text-zinc-500">{new Date(event.timestamp).toLocaleTimeString()}</span>
                            <p className="text-zinc-300 mt-0.5">{event.event}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Assigned Agent */}
                  {incident.assigned_agent && (
                    <div className="text-xs text-zinc-500">
                      Assigned: <span className="text-zinc-300 font-mono">{incident.assigned_agent}</span>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
