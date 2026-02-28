import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { DashboardOverview } from "./components/DashboardOverview";
import { ThreatsView } from "./components/ThreatsView";
import { IncidentsView } from "./components/IncidentsView";
import { ComplianceView } from "./components/ComplianceView";
import { AgentsView } from "./components/AgentsView";
import { AuditTrailView } from "./components/AuditTrailView";
import { PendingActions } from "./components/PendingActions";
import {
  Shield,
  LayoutDashboard,
  ShieldAlert,
  AlertTriangle,
  FileCheck,
  Bot,
  ScrollText,
  Clock,
} from "lucide-react";

function App() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-screen-2xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-600 to-emerald-600 p-2 rounded-lg">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-zinc-100 tracking-tight">SOVEREIGN</h1>
              <p className="text-xs text-zinc-500 -mt-0.5">Agentic Cyber Defense & Compliance</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-zinc-500">All Systems Operational</span>
            </div>
            <div className="text-xs text-zinc-600 font-mono">
              CMMC L2 | NIST 800-171
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-screen-2xl mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-zinc-900 border border-zinc-800 mb-6 flex-wrap h-auto gap-1 p-1">
            <TabsTrigger
              value="overview"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <LayoutDashboard className="h-3.5 w-3.5" />
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="threats"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <ShieldAlert className="h-3.5 w-3.5" />
              Threats
            </TabsTrigger>
            <TabsTrigger
              value="incidents"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              Incidents
            </TabsTrigger>
            <TabsTrigger
              value="compliance"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <FileCheck className="h-3.5 w-3.5" />
              Compliance
            </TabsTrigger>
            <TabsTrigger
              value="agents"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <Bot className="h-3.5 w-3.5" />
              Agents
            </TabsTrigger>
            <TabsTrigger
              value="approvals"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <Clock className="h-3.5 w-3.5" />
              Approvals
            </TabsTrigger>
            <TabsTrigger
              value="audit"
              className="data-[state=active]:bg-zinc-700 data-[state=active]:text-zinc-100 text-zinc-400 gap-1.5 text-xs"
            >
              <ScrollText className="h-3.5 w-3.5" />
              Audit Trail
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <DashboardOverview />
          </TabsContent>
          <TabsContent value="threats">
            <ThreatsView />
          </TabsContent>
          <TabsContent value="incidents">
            <IncidentsView />
          </TabsContent>
          <TabsContent value="compliance">
            <ComplianceView />
          </TabsContent>
          <TabsContent value="agents">
            <AgentsView />
          </TabsContent>
          <TabsContent value="approvals">
            <PendingActions />
          </TabsContent>
          <TabsContent value="audit">
            <AuditTrailView />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 mt-12">
        <div className="max-w-screen-2xl mx-auto px-4 py-4 flex items-center justify-between text-xs text-zinc-600">
          <span>Sovereign v0.1.0 | Agentic Cyber Defense Platform</span>
          <span>NIST 800-171 Rev 2 | 110 Controls | CMMC Level 2</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
