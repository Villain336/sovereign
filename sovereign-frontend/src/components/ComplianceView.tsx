import { useState } from "react";
import { useApi, apiPost } from "../hooks/useApi";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { FileCheck, CheckCircle, XCircle, AlertCircle, HelpCircle, RefreshCw } from "lucide-react";
import type { ComplianceStatus, ComplianceControl } from "../types/api";

const statusConfig: Record<string, { icon: typeof CheckCircle; color: string; bg: string }> = {
  compliant: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-600" },
  partially_compliant: { icon: AlertCircle, color: "text-amber-400", bg: "bg-amber-600" },
  non_compliant: { icon: XCircle, color: "text-red-400", bg: "bg-red-600" },
  not_assessed: { icon: HelpCircle, color: "text-zinc-400", bg: "bg-zinc-600" },
};

export function ComplianceView() {
  const { data: status, loading: statusLoading, refetch: refetchStatus } = useApi<ComplianceStatus>("/api/compliance/status");
  const { data: controlsData, loading: controlsLoading, refetch: refetchControls } = useApi<{ controls: ComplianceControl[]; total: number }>("/api/compliance/controls");
  const [selectedFamily, setSelectedFamily] = useState<string | null>(null);
  const [assessing, setAssessing] = useState(false);

  if (statusLoading || controlsLoading || !status || !controlsData) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading compliance data...</div>;
  }

  const filteredControls = selectedFamily
    ? controlsData.controls.filter((c) => c.family_id === selectedFamily)
    : controlsData.controls;

  const handleAssess = async () => {
    setAssessing(true);
    try {
      await apiPost("/api/compliance/assess", {});
      refetchStatus();
      refetchControls();
    } finally {
      setAssessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCheck className="h-5 w-5 text-emerald-400" />
          <h2 className="text-lg font-semibold text-zinc-100">CMMC Level 2 Compliance</h2>
          <Badge variant="outline" className="border-zinc-700 text-zinc-400">NIST 800-171 Rev 2</Badge>
        </div>
        <button
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded transition-colors disabled:opacity-50"
          onClick={handleAssess}
          disabled={assessing}
        >
          <RefreshCw className={`h-3 w-3 ${assessing ? "animate-spin" : ""}`} />
          Run Assessment
        </button>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-3 text-center">
            <p className="text-3xl font-bold text-emerald-400">{status.overall_score}%</p>
            <p className="text-xs text-zinc-500 mt-1">Overall Score</p>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-emerald-400">{status.compliant}</p>
            <p className="text-xs text-zinc-500 mt-1">Compliant</p>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-amber-400">{status.partially_compliant}</p>
            <p className="text-xs text-zinc-500 mt-1">Partial</p>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-red-400">{status.non_compliant}</p>
            <p className="text-xs text-zinc-500 mt-1">Non-Compliant</p>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-zinc-400">{status.not_assessed}</p>
            <p className="text-xs text-zinc-500 mt-1">Not Assessed</p>
          </CardContent>
        </Card>
      </div>

      {/* Family Filter */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400">Control Families</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <button
              className={`px-3 py-1 text-xs rounded transition-colors ${!selectedFamily ? "bg-zinc-700 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
              onClick={() => setSelectedFamily(null)}
            >
              All ({status.total_controls})
            </button>
            {status.families.map((fam) => (
              <button
                key={fam.family_id}
                className={`px-3 py-1 text-xs rounded transition-colors ${selectedFamily === fam.family_id ? "bg-zinc-700 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
                onClick={() => setSelectedFamily(fam.family_id)}
              >
                {fam.family_id} ({fam.total})
                <span className="ml-1 text-zinc-500">{fam.score}%</span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Controls List */}
      <div className="space-y-2">
        {filteredControls.map((control) => {
          const config = statusConfig[control.status];
          const Icon = config.icon;
          return (
            <Card key={control.control_id} className="border-zinc-800 bg-zinc-900">
              <CardContent className="p-3">
                <div className="flex items-start gap-3">
                  <Icon className={`h-4 w-4 mt-0.5 ${config.color}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-zinc-500">{control.control_id}</span>
                      <Badge className={`${config.bg} text-white text-xs`}>
                        {control.status.replace("_", " ")}
                      </Badge>
                      <span className="text-xs text-zinc-600 ml-auto">{control.family_id}: {control.family}</span>
                    </div>
                    <p className="text-xs text-zinc-300 mt-1 line-clamp-2">{control.title}</p>
                    {control.findings.length > 0 && (
                      <p className="text-xs text-amber-400 mt-1">Finding: {control.findings[0]}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
