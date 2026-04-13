import type { SamOpportunity } from '../types.js';

const SAM_BASE = 'https://api.sam.gov/opportunities/v2/search';
const SAM_API_KEY = process.env.SAM_API_KEY ?? '';

// DOD department codes/names as SAM.gov uses them
const DOD_DEPARTMENT = 'DEPT OF DEFENSE';

export interface SearchOpportunitiesInput {
  naics_codes: string[];
  keywords: string;
  set_aside_types?: string[];
  posted_after?: string;
  opportunity_type?: string; // "SBIR", "STTR", "OTA", or undefined for all
}

/**
 * Search SAM.gov for open DOD contract opportunities.
 * Filters to DOD agencies only and returns the top 20 results.
 */
export async function searchDodOpportunities(
  input: SearchOpportunitiesInput
): Promise<SamOpportunity[]> {
  const params = new URLSearchParams({
    ptype: 'o',
    deptname: DOD_DEPARTMENT,
    status: 'active',
    limit: '20',
    offset: '0',
    naics: input.naics_codes.join(','),
  });

  if (input.keywords) params.set('q', input.keywords);
  if (input.posted_after) params.set('postedFrom', input.posted_after);
  if (SAM_API_KEY) params.set('api_key', SAM_API_KEY);

  // Filter by set-aside type if specified
  if (input.set_aside_types?.length) {
    params.set('typeOfSetAside', input.set_aside_types.join(','));
  }

  const url = `${SAM_BASE}?${params.toString()}`;

  let data: SAMSearchResponse;
  try {
    const res = await fetch(url, {
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) {
      const text = await res.text();
      return [{
        notice_id: 'error',
        title: 'SAM.gov API Error',
        agency: 'N/A',
        opportunity_type: 'Error',
        description: `SAM.gov returned ${res.status}: ${text.slice(0, 200)}`,
      }];
    }
    data = await res.json() as SAMSearchResponse;
  } catch (err) {
    return [{
      notice_id: 'error',
      title: 'SAM.gov fetch failed',
      agency: 'N/A',
      opportunity_type: 'Error',
      description: String(err),
    }];
  }

  const opps = data.opportunitiesData ?? [];
  return opps.map((o) => ({
    notice_id: o.noticeId ?? '',
    title: o.title ?? 'Untitled',
    agency: o.fullParentPathName ?? o.organizationHierarchy?.split('.')?.[1] ?? DOD_DEPARTMENT,
    sub_agency: o.organizationHierarchy?.split('.')?.[2],
    naics_code: o.naicsCode,
    set_aside_type: o.typeOfSetAside,
    opportunity_type: classifyOpportunityType(o.type ?? '', o.title ?? '', o.description ?? ''),
    response_deadline: o.responseDeadLine,
    posted_date: o.postedDate,
    description: (o.description ?? '').slice(0, 800),
    place_of_performance: o.placeOfPerformance?.state?.name,
    contact_email: o.pointOfContact?.[0]?.email,
  }));
}

/**
 * Get full solicitation text for a specific SAM.gov notice.
 */
export async function getOpportunityDetail(noticeId: string): Promise<string> {
  const params = new URLSearchParams({
    ptype: 'o',
    noticeid: noticeId,
    limit: '1',
  });
  if (SAM_API_KEY) params.set('api_key', SAM_API_KEY);

  try {
    const res = await fetch(`${SAM_BASE}?${params.toString()}`, {
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) return `Could not retrieve detail for notice ${noticeId}`;

    const data = await res.json() as SAMSearchResponse;
    const opp = data.opportunitiesData?.[0];
    if (!opp) return `Notice ${noticeId} not found`;

    return [
      `TITLE: ${opp.title}`,
      `AGENCY: ${opp.fullParentPathName ?? 'N/A'}`,
      `TYPE: ${opp.type}`,
      `NAICS: ${opp.naicsCode ?? 'N/A'}`,
      `SET ASIDE: ${opp.typeOfSetAside ?? 'None'}`,
      `RESPONSE DEADLINE: ${opp.responseDeadLine ?? 'N/A'}`,
      `POSTED: ${opp.postedDate ?? 'N/A'}`,
      `PLACE OF PERFORMANCE: ${opp.placeOfPerformance?.state?.name ?? 'N/A'}`,
      `CONTACT: ${opp.pointOfContact?.[0]?.email ?? 'N/A'}`,
      '',
      'DESCRIPTION:',
      opp.description ?? 'No description available.',
    ].join('\n');
  } catch (err) {
    return `Error fetching notice ${noticeId}: ${String(err)}`;
  }
}

function classifyOpportunityType(type: string, title: string, desc: string): string {
  const combined = `${type} ${title} ${desc}`.toLowerCase();
  if (combined.includes('sbir')) return 'SBIR';
  if (combined.includes('sttr')) return 'STTR';
  if (combined.includes('other transaction') || combined.includes(' ota ')) return 'OTA';
  if (combined.includes('broad agency announcement') || combined.includes(' baa ')) return 'BAA';
  if (type === 'p') return 'Pre-Solicitation';
  if (type === 'o') return 'Solicitation';
  if (type === 'k') return 'Combined Synopsis/Solicitation';
  return type ?? 'Opportunity';
}

// SAM.gov API response shapes (partial — only fields we use)
interface SAMSearchResponse {
  opportunitiesData?: SAMOpportunityRaw[];
  totalRecords?: number;
}

interface SAMOpportunityRaw {
  noticeId?: string;
  title?: string;
  type?: string;
  fullParentPathName?: string;
  organizationHierarchy?: string;
  naicsCode?: string;
  typeOfSetAside?: string;
  responseDeadLine?: string;
  postedDate?: string;
  description?: string;
  placeOfPerformance?: {
    state?: { name?: string };
  };
  pointOfContact?: Array<{ email?: string; name?: string }>;
}
