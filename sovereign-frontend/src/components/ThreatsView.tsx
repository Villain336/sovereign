import { useState } from "react";
import { useApi, apiPost } from "../hooks/useApi";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { ScrollArea } from "./ui/scroll-area";
import { ShieldAlert, Target, Radio, ChevronDown, ChevronUp } from "lucide-react";
import type { Threat } from "../types/api";

const severityColors: Record<string, string> = {
  critical: "bg-red-600 text-white",
  high: "bg-orange-600 text-white",
  medium: "bg-amber-600 text-white",
  low: "bg-blue-600 text-white",
  info: "bg-zinc-600 text-white",
};

const statusColors: Record<string, string> = {
  active: "border-red-500 text-red-400",
  investigating: "border-amber-500 text-amber-400",
  contained: "border-blue-500 text-blue-400",
  remediated: "border-emerald-500 text-emerald-400",
  false_positive: "border-zinc-500 text-zinc-400",
};

export function ThreatsView() {
  const { data, loading, refetch } = useApi<{ threats: Threat[]; total: number }>("/api/threats");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [acting, setActing] = useState(false);

  if (loading || !data) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading threats...</div>;
  }

  const handleResponse = async (threatId: string, action: string) => {
    setActing(true);
    try {
      await apiPost(`/api/threats/${threatId}/respond`, { action });
      refetch();
    } catch (err) {
      console.error(err);
    } finally {
      setActing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-red-400" />
          <h2 className="text-lg font-semibold text-zinc-100">Detected Threats</h2>
          <Badge variant="outline" className="border-zinc-700 text-zinc-400">{data.total}</Badge>
        </div>
      </div>

      <ScrollArea className="h-auto">
        <div className="space-y-3">
          {data.threats.map((threat) => (
            <Card key={threat.id} className="border-zinc-800 bg-zinc-900 hover:border-zinc-700 transition-colors">
              <CardContent className="p-4">
                <div
                  className="flex items-start gap-3 cursor-pointer"
                  onClick={() => setExpanded(expanded === threat.id ? null : threat.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge className={severityColors[threat.severity]}>{threat.severity.toUpperCase()}</Badge>
                      <Badge variant="outline" className={statusColors[threat.status]}>{threat.status}</Badge>
                      <span className="text-xs text-zinc-500">
                        {new Date(threat.detected_at).toLocaleString()}
                      </span>
                    </div>
                    <h3 className="text-sm font-medium text-zinc-100 mt-2">{threat.title}</h3>
                    <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{threat.description}</p>
                  </div>
                  <div className="text-zinc-500 pt-1">
                    {expanded === threat.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </div>
                </div>

                {expanded === threat.id && (
                  <div className="mt-4 space-y-4">
                    <Separator className="bg-zinc-800" />

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div>
                        <span className="text-zinc-500">Source IP:</span>
                        <span className="text-zinc-300 ml-2 font-mono">{threat.source_ip || "N/A"}</span>
                      </div>
                      <div>
                        <span className="text-zinc-500">Target:</span>
                        <span className="text-zinc-300 ml-2">{threat.target_asset || "N/A"}</span>
                      </div>
                      <div>
                        <span className="text-zinc-500">Confidence:</span>
                        <span className="text-zinc-300 ml-2">{(threat.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div>
                        <span className="text-zinc-500">Detected by:</span>
                        <span className="text-zinc-300 ml-2 font-mono">{threat.detected_by}</span>
                      </div>
                    </div>

                    {/* MITRE ATT&CK */}
                    {threat.mitre_techniques.length > 0 && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1">
                          <Target className="h-3 w-3" /> MITRE ATT&CK Mapping
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {threat.mitre_techniques.map((t) => (
                            <Badge key={t.technique_id} variant="outline" className="border-zinc-700 text-zinc-300 text-xs">
                              {t.technique_id}: {t.name}
                              <span className="text-zinc-500 ml-1">({t.tactic})</span>
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Indicators */}
                    {threat.indicators.length > 0 && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1">
                          <Radio className="h-3 w-3" /> Indicators of Compromise
                        </p>
                        <div className="space-y-1">
                          {threat.indicators.map((ind, i) => (
                            <div key={i} className="flex items-center gap-2 text-xs">
                              <Badge variant="outline" className="border-zinc-700 text-zinc-400 text-xs w-14 justify-center">
                                {ind.indicator_type}
                              </Badge>
                              <span className="text-zinc-300 font-mono text-xs truncate">{ind.value}</span>
                              <span className="text-zinc-500 ml-auto">{(ind.confidence * 100).toFixed(0)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Response Actions */}
                    {threat.status === "active" || threat.status === "investigating" ? (
                      <div className="flex gap-2 pt-2">
                        <button
                          className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50"
                          onClick={(e) => { e.stopPropagation(); handleResponse(threat.id, "contain"); }}
                          disabled={acting}
                        >
                          Contain
                        </button>
                        <button
                          className="px-3 py-1.5 text-xs bg-amber-600 hover:bg-amber-700 text-white rounded transition-colors disabled:opacity-50"
                          onClick={(e) => { e.stopPropagation(); handleResponse(threat.id, "investigate"); }}
                          disabled={acting}
                        >
                          Investigate
                        </button>
                        <button
                          className="px-3 py-1.5 text-xs bg-emerald-600 hover:bg-emerald-700 text-white rounded transition-colors disabled:opacity-50"
                          onClick={(e) => { e.stopPropagation(); handleResponse(threat.id, "remediate"); }}
                          disabled={acting}
                        >
                          Remediate
                        </button>
                        <button
                          className="px-3 py-1.5 text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded transition-colors disabled:opacity-50"
                          onClick={(e) => { e.stopPropagation(); handleResponse(threat.id, "false_positive"); }}
                          disabled={acting}
                        >
                          False Positive
                        </button>
                      </div>
                    ) : null}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
