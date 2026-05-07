# Blockers

- API-backed model experiments require provider credentials and budget approval: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, or explicitly enabled local `ollama_local`/`vllm_local` entries with reachable `OLLAMA_BASE_URL`/`VLLM_BASE_URL`.
- Focused four-model experiments require `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `ANTHROPIC_API_KEY`.
- Paper submission metadata is not available yet: target venue, page limit, author list, affiliations, and acknowledgements.
- Human annotation/adjudication is needed before making strong empirical claims about the paper subset.
- Paper-ready API result tables cannot be filled until provider/model identifiers, access dates, decoding settings, retry policy, and trial counts are fixed.
- Token-matched prompting and free-form criterion normalization are still paper controls rather than completed experiments.
- A TeX-enabled environment is needed to compile the final PDF and check table/figure placement.
