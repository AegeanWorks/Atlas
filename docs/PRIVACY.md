# Privacy — what leaves your machine

- **Sent to Meta Model API** (`https://api.meta.ai/v1`): ONLY the selected
  figure crop (base64 image) plus the optional caption note you type, plus a
  short noun phrase per SAM segmentation request.
- **Never sent**: the full document, other pages, your corrections file, your
  API key (sent only as the Authorization header, never in body/logs).
- **Local only**: originals under `data/documents`, crops under `data/figures`,
  analyses, corrections, cache. Keys come from `MODEL_API_KEY`/`META_API_KEY`
  environment variables; `AtlasConfig.redacted()` is the only log-safe view.
- Document text extraction runs in-process — no network, no external project
  or session required.
