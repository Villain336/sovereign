import Anthropic from '@anthropic-ai/sdk';
import type { CompanyProfile, PipelineResult, Opportunity } from './types.js';
import { searchDodOpportunities, getOpportunityDetail } from './tools/sam.js';
import { searchDodAwardHistory, formatAwardRecords } from './tools/usaspending.js';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const MODEL = 'claude-sonnet-4-6';

const SYSTEM_PROMPT = `You are an expert defense business development analyst specializing in DOD technology contracts. You have deep knowledge of:

ACQUISITION PATHWAYS:
- SBIR/STTR: Phase I ($250K, 6mo), Phase II ($1.75M, 2yr), Phase III (unlimited, no set-aside — sole-source path to production)
- OTA (Other Transaction Authority): DIU, SOCOM, AFWERX, NavalX — rapid acquisition, no FAR requirements, ideal for non-traditional defense contractors
- IDIQ vehicles: CIO-SP4, SEWP V, OASIS+, STARS III, STARHQ — task-order vehicles that require separate on-ramping
- Broad Agency Announcements (BAA): open R&D solicitations from DARPA, AFRL, ARL, ONR — best for deep tech
- GSA Schedules: IT Schedule 70, now IT Schedule under MAS — commercial item acquisition

KEY PROGRAM OFFICES (by technology area):
- AI/ML: CDAO (Chief Digital and AI Office), JAIC (Joint AI Center), AFRL/RY, Army Futures Command AFC
- Autonomous Systems: AFWERX, NavalX, SOCOM, ARL (Army Research Lab), DARPA TTO
- Cyber: CYBERCOM, NSA/CSS, DISA, each service CIO, AFRL/RI
- Semiconductors/Microelectronics: DARPA MTO, ONR, Army C5ISR, JASON
- Space/SATCOM: USSF SpaceWERX, SMC (Space and Missile Center), NRO, DARPA TTO
- Advanced Manufacturing: DLA, OSD MIBP, Army AMCOM, Navy NAVSEA
- Quantum Computing: DARPA DSO, NSA/CSS, ARL, IARPA

EVALUATION CRITERIA for DOD tech solicitations:
- Technical approach and innovation (often 50%+ of evaluation weight)
- Past performance — defense-specific contracts weighted heavily; no past performance is acceptable for SBIR
- Cost realism (not just low price — unrealistically low bids raise red flags)
- Clearance requirements: Secret, Top Secret (TS), TS/SCI, SAP/SAR — each requires separate adjudication
- CMMC compliance: Level 1 (basic cyber hygiene), Level 2 (CUI handling, NIST 800-171), Level 3 (advanced APT defense)
- Small business certifications: 8(a) (SBA program), SDVOSB (service-disabled veteran), HUBZone, WOSB

SET-ASIDE TYPE CODES on SAM.gov:
- "SBA" or "8AN" = 8(a) set-aside
- "SBP" = Small Business set-aside
- "SDVOSBC" = Service-Disabled Veteran-Owned Small Business
- "HZC" = HUBZone
- "WOSB" = Women-Owned Small Business
- "EDWOSB" = Economically Disadvantaged WOSB
- No code = full and open competition (primes eligible)

COMPETITIVE LANDSCAPE:
- Traditional primes (Lockheed, Raytheon, Northrop, Boeing, L3Harris, SAIC, Leidos, Booz Allen) dominate large contracts
- Non-traditional defense contractors (commercial tech companies) gain advantage via OTA and SBIR
- SBIR Phase I/II are explicitly set aside for small businesses — primes are excluded
- "Recompete" opportunities (existing contracts expiring) carry incumbent risk but also transition opportunity

INSTRUCTIONS:
1. Search for open DOD opportunities using the provided NAICS codes and capability keywords
2. For the most promising opportunities, retrieve full solicitation details
3. Search award history to identify incumbents and pricing benchmarks
4. Analyze each opportunity with full DOD domain knowledge
5. Return ONLY valid JSON — a PipelineResult object — as your final response

FINAL OUTPUT FORMAT:
Return a single JSON object with this exact structure:
{
  "company": "<company name>",
  "generated_at": "<ISO timestamp>",
  "summary": "<2-3 sentence executive summary of findings>",
  "pipeline": [
    {
      "title": "<opportunity title>",
      "agency": "<awarding agency>",
      "naics_code": "<NAICS>",
      "opportunity_type": "<SBIR Phase I|SBIR Phase II|OTA|BAA|Solicitation|Pre-Solicitation>",
      "value_estimate": "<dollar estimate if available>",
      "due_date": "<ISO date or null>",
      "set_aside": "<set-aside type or null>",
      "fit_score": <1-10>,
      "fit_reasoning": "<specific reasoning tied to company capabilities>",
      "clearance_required": "<Secret|Top Secret|TS/SCI|None|Unknown>",
      "cmmc_level": "<1|2|3|null>",
      "ota_pathway": <true|false>,
      "sbir_phase": "<Phase I|Phase II|Phase III|null>",
      "program_office": "<specific program office acronym if known>",
      "incumbent": "<incumbent company name or null>",
      "incumbent_award_value": "<dollar value or null>",
      "recompete_notes": "<recompete analysis or null>",
      "recommendation": "<BID|NO BID|MONITOR>",
      "action_items": ["<specific next step>", ...],
      "notice_id": "<SAM.gov notice ID or null>"
    }
  ]
}`;

const TOOLS: Anthropic.Tool[] = [
  {
    name: 'search_dod_opportunities',
    description:
      'Search SAM.gov for open DOD contract opportunities. Filters to DOD agencies only. Returns the top 20 results sorted by relevance.',
    input_schema: {
      type: 'object' as const,
      properties: {
        naics_codes: {
          type: 'array',
          items: { type: 'string' },
          description: 'NAICS codes to search (e.g. ["541715", "541512"])',
        },
        keywords: {
          type: 'string',
          description:
            'Search keywords (e.g. "artificial intelligence autonomous unmanned systems")',
        },
        set_aside_types: {
          type: 'array',
          items: { type: 'string' },
          description:
            'SAM.gov set-aside codes to filter by (e.g. ["SBA"] for 8(a), ["SBP"] for small business)',
        },
        posted_after: {
          type: 'string',
          description: 'ISO date — only return opportunities posted after this date',
        },
        opportunity_type: {
          type: 'string',
          description:
            'Filter by type: "SBIR", "STTR", "OTA", or omit for all opportunities',
        },
      },
      required: ['naics_codes', 'keywords'],
    },
  },
  {
    name: 'get_opportunity_detail',
    description:
      'Get the full solicitation text, requirements, and contact information for a specific SAM.gov notice ID. Call this for the most promising opportunities to understand exact requirements.',
    input_schema: {
      type: 'object' as const,
      properties: {
        notice_id: {
          type: 'string',
          description: 'The SAM.gov notice ID (e.g. "SPE7M225R0019")',
        },
      },
      required: ['notice_id'],
    },
  },
  {
    name: 'search_dod_award_history',
    description:
      'Search USASpending.gov for recent DOD contract awards in a NAICS code. Use this to identify incumbents, understand competitive pricing, and spot expiring contracts that will be recompeted.',
    input_schema: {
      type: 'object' as const,
      properties: {
        naics_code: {
          type: 'string',
          description: 'Single NAICS code to search (e.g. "541715")',
        },
        keywords: {
          type: 'string',
          description: 'Optional keywords to narrow the search',
        },
        agency_name: {
          type: 'string',
          description:
            'Optional DOD sub-agency to filter by (e.g. "Air Force", "DARPA", "Defense Advanced Research Projects Agency")',
        },
        years_back: {
          type: 'number',
          description: 'How many years of history to search (default: 3)',
        },
      },
      required: ['naics_code'],
    },
  },
];

async function executeTool(
  name: string,
  input: Record<string, unknown>
): Promise<string> {
  switch (name) {
    case 'search_dod_opportunities': {
      const results = await searchDodOpportunities({
        naics_codes: input.naics_codes as string[],
        keywords: input.keywords as string,
        set_aside_types: input.set_aside_types as string[] | undefined,
        posted_after: input.posted_after as string | undefined,
        opportunity_type: input.opportunity_type as string | undefined,
      });
      if (!results.length) return 'No opportunities found.';
      return JSON.stringify(results, null, 2);
    }

    case 'get_opportunity_detail': {
      const detail = await getOpportunityDetail(input.notice_id as string);
      return detail;
    }

    case 'search_dod_award_history': {
      const awards = await searchDodAwardHistory({
        naics_code: input.naics_code as string,
        keywords: input.keywords as string | undefined,
        agency_name: input.agency_name as string | undefined,
        years_back: input.years_back as number | undefined,
      });
      return formatAwardRecords(awards);
    }

    default:
      return `Unknown tool: ${name}`;
  }
}

export async function runAgent(profile: CompanyProfile): Promise<PipelineResult> {
  const userMessage = `Analyze DOD contract opportunities for the following company:

Company: ${profile.company_name}
Capabilities: ${profile.capabilities}
NAICS Codes: ${profile.naics_codes.join(', ')}
${profile.certifications?.length ? `Certifications: ${profile.certifications.join(', ')}` : ''}
${profile.clearances?.length ? `Security Clearances: ${profile.clearances.join(', ')}` : ''}
${profile.focus_areas?.length ? `Focus Areas: ${profile.focus_areas.join(', ')}` : ''}
${profile.keywords ? `Additional Keywords: ${profile.keywords}` : ''}

Please:
1. Search for open DOD opportunities across all relevant NAICS codes
2. Get full details on the 3-5 most promising opportunities
3. Search award history for the key NAICS codes to identify incumbents and pricing
4. Return a complete pipeline analysis as the JSON PipelineResult object described in your instructions`;

  const messages: Anthropic.MessageParam[] = [
    { role: 'user', content: userMessage },
  ];

  let tokenUsage = {
    input_tokens: 0,
    output_tokens: 0,
    cache_read_input_tokens: 0,
    cache_creation_input_tokens: 0,
  };

  // Agentic loop
  while (true) {
    const response = await client.messages.create({
      model: MODEL,
      max_tokens: 8192,
      system: [
        {
          type: 'text',
          text: SYSTEM_PROMPT,
          cache_control: { type: 'ephemeral' },
        },
      ],
      tools: TOOLS,
      messages,
    });

    // Accumulate token usage
    tokenUsage.input_tokens += response.usage.input_tokens;
    tokenUsage.output_tokens += response.usage.output_tokens;
    const usageAny = response.usage as unknown as Record<string, number>;
    tokenUsage.cache_read_input_tokens += usageAny.cache_read_input_tokens ?? 0;
    tokenUsage.cache_creation_input_tokens += usageAny.cache_creation_input_tokens ?? 0;

    // If Claude is done, parse the final response
    if (response.stop_reason === 'end_turn') {
      const textBlock = response.content.find((b) => b.type === 'text');
      const rawText = textBlock && textBlock.type === 'text' ? textBlock.text : '';

      // Extract JSON from the response (Claude sometimes wraps it in markdown)
      const jsonMatch = rawText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        // Fallback if Claude didn't return valid JSON
        return {
          company: profile.company_name,
          generated_at: new Date().toISOString(),
          summary:
            'Agent completed analysis but did not return structured pipeline data.',
          pipeline: [],
          token_usage: tokenUsage,
        };
      }

      try {
        const parsed = JSON.parse(jsonMatch[0]) as PipelineResult;
        parsed.token_usage = tokenUsage;
        parsed.generated_at = parsed.generated_at ?? new Date().toISOString();
        return parsed;
      } catch {
        return {
          company: profile.company_name,
          generated_at: new Date().toISOString(),
          summary: `Analysis complete but JSON parse failed. Raw: ${rawText.slice(0, 500)}`,
          pipeline: [],
          token_usage: tokenUsage,
        };
      }
    }

    // Claude wants to use tools — execute them
    if (response.stop_reason === 'tool_use') {
      // Add Claude's response to messages
      messages.push({ role: 'assistant', content: response.content });

      // Execute all tool calls and collect results
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const block of response.content) {
        if (block.type !== 'tool_use') continue;

        const result = await executeTool(
          block.name,
          block.input as Record<string, unknown>
        );

        toolResults.push({
          type: 'tool_result',
          tool_use_id: block.id,
          content: result,
        });
      }

      // Add tool results back to messages
      messages.push({ role: 'user', content: toolResults });
      continue;
    }

    // Unexpected stop reason
    break;
  }

  return {
    company: profile.company_name,
    generated_at: new Date().toISOString(),
    summary: 'Agent loop exited unexpectedly.',
    pipeline: [],
    token_usage: tokenUsage,
  };
}
