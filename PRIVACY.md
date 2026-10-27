# Privacy

This Dify plugin connects to PopNow. PopNow's service policy is https://popnow.ai/privacy; contact support@popnow.ai for privacy requests.

## Data transmitted

The API key entered in Dify is sent only as an Authorization header to `https://api.popnow.ai`. Dify controls credential storage and deployment logs. The plugin itself does not persist keys, prompts, files or outputs, and contains no analytics or telemetry endpoint.

Model searches, generation prompts, supplied text, model inputs and reference media URLs are sent to PopNow to fulfill the requested operation. PopNow may send the necessary content to its generation providers and retrieve reference media. The task identifier is sent to PopNow for status lookup. The API balance response may contain account billing information. Returned task data and signed output URLs are passed back to the calling Dify workflow, which may retain them according to its configuration.

The plugin does not read local files, download generated media or reference URLs, access browser history, or collect payment card details. It follows no redirects and uses a fixed API origin. Error messages omit request bodies, credentials and upstream response bodies. It does not intentionally collect health data, biometrics, children's data, precise location or other sensitive personal content; do not include such data in prompts or reference files.

## Retention and control

PopNow stores tasks and generated content according to the service privacy policy and account settings. Dify may retain workflow inputs, results and logs independently. Revoke the dedicated API key in the PopNow API console to stop its access. Contact support@popnow.ai about PopNow account data or deletion requests; contact your Dify administrator about workflow retention.
