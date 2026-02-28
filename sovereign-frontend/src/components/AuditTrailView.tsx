import { useApi } from "../hooks/useApi";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollText, ShieldCheck, Link2 } from "lucide-react";
import type { AuditEntry } from "../types/api";

export function AuditTrailView() {
  const { data, loading } = useApi<{ entries: AuditEntry[]; total: number }>("/api/audit/trail?limit=100");
  const { data: integrity } = useApi<{ verified: boolean; entries_checked: number; message: string }>("/api/audit/integrity");

  if (loading || !data) {
    return <div className="text-zinc-400 animate-pulse p-8">Loading audit trail...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ScrollText className="h-5 w-5 text-purple-400" />
          <h2 className="text-lg font-semibold text-zinc-100">Cryptographic Audit Trail</h2>
          <Badge variant="outline" className="border-zinc-700 text-zinc-400">{data.total} entries</Badge>
        </div>
        {integrity && (
          <Badge
            variant="outline"
            className={integrity.verified ? "border-emerald-600 text-emerald-400" : "border-red-600 text-red-400"}
          >
            <ShieldCheck className="h-3 w-3 mr-1" />
            {integrity.verified ? "Chain Verified" : "Integrity Error"}
          </Badge>
        )}
      </div>

      {/* Chain Info */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="p-3">
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <Link2 className="h-3 w-3" />
            <span>SHA-256 hash chain | Each entry linked to previous via cryptographic hash | Tamper-evident design for CMMC AU family compliance</span>
          </div>
        </CardContent>
      </Card>

      {/* Entries */}
      <div className="space-y-2">
        {data.entries.map((entry) => (
          <Card key={entry.id} className="border-zinc-800 bg-zinc-900">
            <CardContent className="p-3">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-zinc-500">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                    <Badge variant="outline" className="border-zinc-700 text-zinc-300 text-xs">
                      {entry.action}
                    </Badge>
                    <span className="text-xs text-zinc-500">by</span>
                    <span className="text-xs text-zinc-300 font-mono">{entry.actor}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs">
                    {entry.resource_type && (
                      <span className="text-zinc-500">
                        {entry.resource_type}/{entry.resource_id}
                      </span>
                    )}
                  </div>
                  <div className="mt-1 text-xs font-mono text-zinc-600 truncate" title={entry.hash}>
                    Hash: {entry.hash.substring(0, 24)}...
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
