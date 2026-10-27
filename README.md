# PopNow for Dify

Create images, videos, music and voiceovers through the [PopNow API](https://popnow.ai/docs). Discover model input schemas, obtain an exact USD quote, create an explicitly approved task, and retrieve its status and output URLs.

## Setup

1. Create a PopNow account and a dedicated API key in the [API console](https://popnow.ai/api/console/keys). Restrict the key's models, allowed IPs and daily/monthly/lifetime budget as needed.
2. Add funds to the **API USD balance** in [API billing](https://popnow.ai/api/console/billing). It starts at $0. Website credits and API USD are separate; website credits cannot pay for these tools. No subscription is required.
3. Install this plugin in Dify and enter the key in its secret credential field. Credential validation makes one read-only balance request.
4. Allow outbound HTTPS to `api.popnow.ai:443`. No arbitrary API host can be configured. References supplied in model inputs are sent to PopNow, which may retrieve them to fulfill the request.

Source: https://github.com/popnow-ai/popnow-dify . Support: support@popnow.ai . [Privacy](https://popnow.ai/privacy) · [Terms](https://popnow.ai/terms).

## Tools

| Tool | Purpose | Spends API funds? |
| --- | --- | --- |
| Find models | Search models and return input schemas and examples | No |
| API USD balance | Read the available API balance | No |
| Quote generation | Quote the exact model and input | No |
| Create approved task | Submit one task using its approved quote, USD cap and stable idempotency key | Yes |
| Task status | Read state and output URLs for a task ID | No |

### A complete generation

1. Use **Find models** with a search term such as `image`. Choose a returned full model path and construct `input_json` according to its schema. Model paths can contain several `/` separators; do not replace them with display names.
2. Use **Quote generation** with that exact model and input. Show `maxChargeUsd` and the requested content to the user. Obtain explicit approval even if the quote is zero.
3. Use **Create approved task** with unchanged model/input, `quote_id` from `quoteId`, and `approved_max_usd` copied from `maxChargeUsd` as a **decimal string**, such as `"0.012345678"`. Never round it through a binary float. Supply a unique, stable `idempotency_key` for this approved task. Do not let an Agent assume approval from a general creation request.
4. Use **Task status** with the returned task ID. Wait between polls while it is pending. Show the final output URLs; the plugin does not download generated files.

If a quote expires, inputs change, or a higher cost is required, quote again and obtain approval. A failed or timed-out create request must not be retried using a new idempotency key: keep the original key and the same payload to avoid duplicates. A pending task is not a failed generation. Do not retry terminal failures automatically. Refund/hold release follows the API's [billing policy](https://popnow.ai/docs/billing).

## Security and data

The plugin handles a PopNow API key and user content. It only calls five fixed HTTPS API paths. It does not run shell commands or user code, browse websites, access a database, read local files, fetch arbitrary URLs, or follow HTTP redirects. Reference URLs are passed to the model service, not downloaded by the plugin. It never collects payment card details or purchases balance. API spending is bounded by the approved quote and the key's server-enforced restrictions.

Use only content the user is authorized to supply. Avoid sensitive personal content in prompts. Generated outputs are private until the user chooses to share them; an output URL is data, not permission to post publicly. Read [PRIVACY.md](PRIVACY.md) for the data flow.

## Validation and limitations

Version 0.1.0 includes deterministic tests of request construction, exact USD strings, required approval fields, stable idempotency headers, JSON validation, redirect rejection and credential-safe errors. The official Dify SDK metadata loader and package CLI are checked before submission.

A complete generation in Dify Community Edition and Dify Cloud has **not** been run for this submission. The API contract is documented publicly; this limitation is disclosed in the Marketplace PR. Reviewers can request an independent funded API test account through support@popnow.ai. No credentials are included in source or the package.
