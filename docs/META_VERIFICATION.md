# Meta verification (checked 2026-11-01, https://dev.meta.ai/docs/*)

- Overview: base URL `https://api.meta.ai/v1`, auth `Bearer $MODEL_API_KEY`.
- Muse Spark models: `muse-spark-1.3`, `muse-spark-1.2`, `muse-spark-1.1`;
  Contributor mode: `muse-spark-1.3-contributor`, `muse-spark-1.2-contributor`.
- Muse Wonder: `muse-wonder-1.0` (same requests as Spark; complex reasoning).
- Context window Spark/Wonder: 1,048,576 tokens.
- Image understanding: Responses API `input_image` (plain string URL/data/file_id)
  or Chat Completions `image_url` object; images only in `user` messages; base64
  `data:` URLs supported; Files API `file_id` supported; max 50 images/request;
  inline image max 50 MB; supported MIME jpeg/jpg/png/gif/webp/x-icon.
- Perception grounding: normalized **0–1000** grid, (0,0) top-left; convert with
  `to_pixels(x) = round(x * width / 1000)`; clamp edge 1001; CSS % = /10.
  Modes: point `{x,y}`, box `{bbox:[{x_min,y_min,x_max,y_max}]}`, count
  `{points,count}`; keep grounding instruction in the user message.
- Structured output: Chat Completions `response_format: {type: json_schema,
  json_schema: {...}}` (Responses: `text.format`); schema-constrained decoding.
- SAM 3.1: model `sam-3.1` via `POST /v1/responses` (+ `/v1/files`); input is a
  short noun-phrase `input_text` + `input_image`; output is special-token text
  with one box + pixel mask per match; video tracks across frames. Muse names
  the object → SAM cuts the mask (pairing used by Atlas).
