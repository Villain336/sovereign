import type { AwardRecord } from '../types.js';

const USA_SPENDING_BASE = 'https://api.usaspending.gov/api/v2';

export interface SearchAwardHistoryInput {
  naics_code: string;
  keywords?: string;
  agency_name?: string;  // e.g. "Air Force", "DARPA", "Defense Advanced Research"
  years_back?: number;   // default 3
}

/**
 * Search USASpending.gov for recent DOD contract awards.
 * Used to identify incumbents, pricing benchmarks, and spending trends.
 */
export async function searchDodAwardHistory(
  input: SearchAwardHistoryInput
): Promise<AwardRecord[]> {
  const yearsBack = input.years_back ?? 3;
  const startYear = new Date().getFullYear() - yearsBack;
  const startDate = `${startYear}-01-01`;
  const endDate = new Date().toISOString().split('T')[0];

  const filters: USASpendingFilters = {
    award_type_codes: ['A', 'B', 'C', 'D'],
    agencies: [
      {
        type: 'funding',
        tier: 'toptier',
        name: 'Department of Defense',
      },
    ],
    naics_codes: [input.naics_code],
    time_period: [{ start_date: startDate, end_date: endDate }],
  };

  if (input.agency_name) {
    filters.agencies.push({
      type: 'awarding',
      tier: 'subtier',
      name: input.agency_name,
    });
  }

  const body = {
    filters,
    fields: [
      'Award ID',
      'Recipient Name',
      'Award Amount',
      'Awarding Agency',
      'Awarding Sub Agency',
      'NAICS Code',
      'Period of Performance End Date',
      'Description',
      'Start Date',
    ],
    sort: 'Award Amount',
    order: 'desc',
    limit: 15,
    page: 1,
    subawards: false,
  };

  try {
    const res = await fetch(`${USA_SPENDING_BASE}/search/spending_by_award/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      return [{
        awardee: 'API Error',
        award_amount: 0,
        awarding_agency: 'N/A',
        description: `USASpending returned ${res.status}: ${text.slice(0, 200)}`,
      }];
    }

    const data = await res.json() as USASpendingResponse;
    const results = data.results ?? [];

    return results.map((r) => ({
      awardee: String(r['Recipient Name'] ?? 'Unknown'),
      award_amount: parseFloat(String(r['Award Amount'] ?? 0)),
      awarding_agency: [r['Awarding Agency'], r['Awarding Sub Agency']]
        .filter(Boolean)
        .join(' / '),
      award_date: r['Start Date'] as string | undefined,
      period_end: r['Period of Performance End Date'] as string | undefined,
      naics_code: r['NAICS Code'] as string | undefined,
      description: String(r['Description'] ?? '').slice(0, 300),
    }));
  } catch (err) {
    return [{
      awardee: 'Fetch Error',
      award_amount: 0,
      awarding_agency: 'N/A',
      description: String(err),
    }];
  }
}

/**
 * Format award records into a readable summary for Claude.
 */
export function formatAwardRecords(awards: AwardRecord[]): string {
  if (!awards.length) return 'No award history found.';

  return awards
    .map((a, i) => {
      const amount = a.award_amount
        ? `$${(a.award_amount / 1_000_000).toFixed(2)}M`
        : 'Amount N/A';
      const expiry = a.period_end ? ` | Expires: ${a.period_end}` : '';
      return [
        `${i + 1}. ${a.awardee} — ${amount}`,
        `   Agency: ${a.awarding_agency}${expiry}`,
        a.description ? `   Scope: ${a.description}` : '',
      ]
        .filter(Boolean)
        .join('\n');
    })
    .join('\n\n');
}

// USASpending API response shapes
interface USASpendingFilters {
  award_type_codes: string[];
  agencies: Array<{
    type: string;
    tier: string;
    name: string;
  }>;
  naics_codes: string[];
  time_period: Array<{ start_date: string; end_date: string }>;
}

interface USASpendingResponse {
  results?: Array<Record<string, unknown>>;
  page_metadata?: { total: number };
}
