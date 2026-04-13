import 'dotenv/config';
import express from 'express';
import { z } from 'zod';
import { runAgent } from './agent.js';
import type { CompanyProfile } from './types.js';

const app = express();
app.use(express.json());

const PORT = process.env.PORT ?? 3001;

// Input validation schema
const CompanyProfileSchema = z.object({
  company_name: z.string().min(1, 'company_name is required'),
  capabilities: z.string().min(1, 'capabilities is required'),
  naics_codes: z
    .array(z.string())
    .min(1, 'at least one naics_code is required'),
  certifications: z.array(z.string()).optional(),
  clearances: z.array(z.string()).optional(),
  focus_areas: z.array(z.string()).optional(),
  keywords: z.string().optional(),
});

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'dod-contract-agent',
    timestamp: new Date().toISOString(),
  });
});

app.post('/analyze', async (req, res) => {
  const parsed = CompanyProfileSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({
      error: 'Invalid request',
      details: parsed.error.flatten(),
    });
    return;
  }

  const profile: CompanyProfile = parsed.data;

  console.log(
    `[${new Date().toISOString()}] Analyzing opportunities for: ${profile.company_name}`
  );

  try {
    const result = await runAgent(profile);
    console.log(
      `[${new Date().toISOString()}] Done — ${result.pipeline.length} opportunities found`,
      result.token_usage ? `| tokens: ${JSON.stringify(result.token_usage)}` : ''
    );
    res.json(result);
  } catch (err) {
    console.error('Agent error:', err);
    res.status(500).json({
      error: 'Agent failed',
      message: err instanceof Error ? err.message : String(err),
    });
  }
});

app.listen(PORT, () => {
  console.log(`DOD Contract Intelligence Agent running on http://localhost:${PORT}`);
  console.log(`POST /analyze — run pipeline analysis`);
  console.log(`GET  /health  — health check`);
});
