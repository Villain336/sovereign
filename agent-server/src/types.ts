export interface CompanyProfile {
  company_name: string;
  capabilities: string;
  naics_codes: string[];
  certifications?: string[];   // e.g. ["8(a)", "SDVOSB", "HUBZone", "WOSB", "Small Business"]
  clearances?: string[];       // e.g. ["Secret", "Top Secret", "TS/SCI"]
  focus_areas?: string[];      // e.g. ["SBIR", "OTA", "DARPA", "AFRL", "Space Force"]
  keywords?: string;           // free-text capability keywords
}

export interface SamOpportunity {
  notice_id: string;
  title: string;
  agency: string;
  sub_agency?: string;
  naics_code?: string;
  set_aside_type?: string;
  opportunity_type: string;    // "SBIR", "STTR", "OTA", "Solicitation", "BAA", etc.
  response_deadline?: string;
  posted_date?: string;
  description: string;
  value_estimate?: string;
  place_of_performance?: string;
  contact_email?: string;
}

export interface AwardRecord {
  awardee: string;
  award_amount: number;
  awarding_agency: string;
  award_date?: string;
  period_end?: string;
  naics_code?: string;
  description?: string;
}

export interface Opportunity {
  title: string;
  agency: string;
  naics_code?: string;
  opportunity_type: string;
  value_estimate?: string;
  due_date?: string;
  set_aside?: string;
  fit_score: number;           // 1-10
  fit_reasoning: string;
  clearance_required?: string;
  cmmc_level?: string;         // "1", "2", or "3"
  ota_pathway: boolean;
  sbir_phase?: string;         // "Phase I", "Phase II", "Phase III"
  program_office?: string;
  incumbent?: string;
  incumbent_award_value?: string;
  recompete_notes?: string;
  recommendation: "BID" | "NO BID" | "MONITOR";
  action_items: string[];
  notice_id?: string;
}

export interface PipelineResult {
  company: string;
  generated_at: string;
  summary: string;
  pipeline: Opportunity[];
  token_usage?: {
    input_tokens: number;
    output_tokens: number;
    cache_read_input_tokens: number;
    cache_creation_input_tokens: number;
  };
}
