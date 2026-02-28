import { useApi } from "../hooks/useApi";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import {
  Shield,
  AlertTriangle,
  ShieldAlert,
  Activity,
  CheckCircle,
  Clock,
  Bot,
  FileCheck,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import type { DashboardSummary } from "../types/api";

const COLORS = ["#22c55e", "#f59e0b", "#ef4444", "#6b7280"];

export function DashboardOverview() {
  const { data, loading } = useApi<DashboardSummary>("/api/dashboard/summary");

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-zinc-400">Loading dashboard...</div>
      </div>
    );
  }

  const compliancePieData = [
    { name: "Compliant", value: data.controls_compliant },
    {
      name: "Partial",
      value: data.controls_total - data.controls_compliant - Math.round(data.controls_total * 0.13),
    },
    {
      name: "Non-Compliant",
      value: Math.round(data.controls_total * 0.10),
    },
    {
      name: "Not Assessed",
      value: Math.round(data.controls_total * 0.13),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-zinc-500 uppercase tracking-wider">Active Threats</p>
                <p className="text-3xl font-bold text-red-400 mt-1">{data.active_threats}</p>
                <p className="text-xs text-zinc-500 mt-1">{data.critical_threats} critical</p>
              </div>
              <ShieldAlert className="h-8 w-8 text-red-500 opacity-60" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-zinc-500 uppercase tracking-wider">Open Incidents</p>
                <p className="text-3xl font-bold text-amber-400 mt-1">{data.open_incidents}</p>
                <p className="text-xs text-zinc-500 mt-1">{data.total_incidents} total</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-amber-500 opacity-60" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-zinc-500 uppercase tracking-wider">CMMC L2 Score</p>
                <p className="text-3xl font-bold text-emerald-400 mt-1">{data.compliance_score}%</p>
                <p className="text-xs text-zinc-500 mt-1">{data.controls_compliant}/{data.controls_total} controls</p>
              </div>
              <CheckCircle className="h-8 w-8 text-emerald-500 opacity-60" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-zinc-500 uppercase tracking-wider">Agents Online</p>
                <p className="text-3xl font-bold text-blue-400 mt-1">{data.agents_running}</p>
                <p className="text-xs text-zinc-500 mt-1">{data.agents_total} deployed</p>
              </div>
              <Bot className="h-8 w-8 text-blue-500 opacity-60" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Approvals Banner */}
      {data.pending_approvals > 0 && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="p-4 flex items-center gap-3">
            <Clock className="h-5 w-5 text-amber-400" />
            <span className="text-amber-200 font-medium">
              {data.pending_approvals} action{data.pending_approvals > 1 ? "s" : ""} awaiting human approval
            </span>
            <Badge variant="outline" className="ml-auto border-amber-600 text-amber-400">
              HITL Required
            </Badge>
          </CardContent>
        </Card>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Trend */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Threat Activity (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={data.threat_trend}>
                <XAxis
                  dataKey="hour"
                  tick={{ fill: "#71717a", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  interval={3}
                />
                <YAxis
                  tick={{ fill: "#71717a", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={20}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "1px solid #3f3f46",
                    borderRadius: "6px",
                    color: "#fafafa",
                  }}
                />
                <Bar dataKey="threats" fill="#ef4444" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Compliance Pie */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
              <FileCheck className="h-4 w-4" />
              NIST 800-171 Compliance
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-center">
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie
                  data={compliancePieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {compliancePieData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "1px solid #3f3f46",
                    borderRadius: "6px",
                    color: "#fafafa",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 text-sm">
              {compliancePieData.map((entry, i) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[i] }}
                  />
                  <span className="text-zinc-400">{entry.name}</span>
                  <span className="text-zinc-200 font-medium ml-auto">{entry.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Compliance by Family */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Compliance by Control Family
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.compliance_by_family.map((family) => (
              <div key={family.family_id} className="flex items-center gap-3">
                <span className="text-xs font-mono text-zinc-500 w-6">{family.family_id}</span>
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-zinc-400 truncate">{family.family}</span>
                    <span className="text-zinc-300">{family.score}%</span>
                  </div>
                  <Progress
                    value={family.score}
                    className="h-1.5"
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
