# Public deployment monitoring

`scripts/monitor_public_deployment.py` is a dependency-free, anonymous operational
check. `.github/workflows/public-monitor.yml` runs it in the existing public
`MOUHANEDXIX/geomapper-pro-downloads` repository. The private application repository
keeps a reviewed copy; its exact-repository job guard prevents duplicate scheduled
runners. Publishing these files and activating the schedule is a separate root
deployment action. This document does not establish that monitoring or account
notifications have been activated.

## Cadence and free-service behavior

- At minutes 7, 22, 37 and 52 UTC: check Cloudflare homepage identity, public
  `config.js`, static stable/beta changelog metadata and installer HEAD responses.
  These runs make **no API requests** and do not download installer bodies.
- At 00:17, 06:17, 12:17 and 18:17 UTC: also check `/readyz`, `/healthz`, both
  `/app/version` channels, CORS and agreement with the website's published release
  metadata. In Africa/Lagos these are 01:17, 07:17, 13:17 and 19:17.
- Manual **Run workflow → full** performs the same API checks after a deployment.

Render documents that a free web service sleeps after 15 idle minutes and takes
about a minute to start. Polling the API every 15 minutes would defeat that idle
policy. Only the four full batches, manual runs and normal user traffic wake it.
They still count against the workspace's shared free instance allowance.
[Render free-service limits](https://render.com/docs/free).

Ordinary requests have a 15-second socket timeout and a 512 KiB inspection cap.
Readiness gets up to two attempts: 75 seconds, a 15-second pause, then 45 seconds.
Only transient network/server/loading failures are retried. A successful cold
start records both attempts but passes the batch. An unsuccessful readiness check
skips further API requests. The workflow has an eight-minute final limit.

GitHub schedules are approximate: queue delays and dropped scheduled runs are
possible. Scheduled public workflows can be automatically disabled after 60 days
without repository activity. Check the Actions page periodically and re-enable a
disabled workflow explicitly; monitoring does not create artificial commits.
[GitHub scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Standard GitHub-hosted runners in public repositories are free; private
repositories draw from the owner's included compute. No new paid vendor or
private application source is required for the public monitor.
[GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

## Alerts and ownership

The workflow fails when a check fails, writes a readable Actions step summary and
retains sanitized JSON/Markdown failure artifacts for seven days. A later green
run shows recovery. No emails, chat messages, issues or webhook requests are sent
by the script, and it needs no API credentials.

The owner must enable **GitHub Settings → Notifications → Actions** email or web
notifications, optionally **Only notify for failed workflows**. Scheduled-run
notifications go to the account that created or last changed the cron schedule,
or re-enabled that schedule. Repository access alone does not establish that the
intended owner receives alerts. Verify the actual account setting and actor during
activation, then deliberately exercise a synthetic failed workflow and recovery.
Failure-only settings do not promise a recovery email. There is no invented alert
address or automatic issue creation.
Use **Run workflow**, choose **static** and enable **exercise_alert** for one
deliberate failed notification exercise. Its step summary labels the failure as
intentional. Confirm the intended owner's actual GitHub/email notification, then
run **static** again with **exercise_alert** disabled to record recovery. The
option defaults to false and cannot affect scheduled checks.
[GitHub workflow notifications](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs).

## Checks and interpretation

Both release channels require a version, versioned public asset URL in the known
downloads repository, expected filename, positive byte size, 64-digit SHA256 and
well-formed 64-byte Ed25519 signature metadata. Stable requires tag `v{latest_version}`
and `GeoMapperProSetup.exe`; beta requires `v{latest_version}-beta` and
`GeoMapperProBetaSetup.exe`. Both sources agreeing on a mislabeled old tag or the
other channel's installer still fails. The public HEAD response must
advertise the expected byte size. Full mode compares those fields with the API.
These checks establish metadata consistency and availability; they do not fetch
or hash installer bytes, verify the cryptographic signature, install the app,
authenticate a user, send mail or establish continuous uptime. Release acceptance
and database restoration remain separate workflows.

Reports contain check labels, pass/fail, HTTP status, timing, bounded readiness
attempts and controlled failure codes. They exclude response bodies, URLs,
redirect query strings, headers, exception text, credentials and account data.
Redirects stay HTTPS and are limited to the original host, or the known GitHub
release CDN hosts for installer HEAD requests. Redirected asset tokens are never
recorded. The script uses only GET and HEAD and never reads local `.env` files.

## Reproduce and maintain

```powershell
python -B scripts/monitor_public_deployment.py --mode static --output-dir .tools/monitor-static
python -B scripts/monitor_public_deployment.py --mode full --output-dir .tools/monitor-full
python -m unittest discover -s tests -p test_public_monitoring.py -v
```

Use full mode deliberately because it can wake Render. Repository variables
`MONITOR_SITE_URL` and `MONITOR_API_URL` can override public HTTPS origins; never
put credentials or query strings there. Changing domains requires reviewing the
website configuration and CORS together. The public runtime needs only the new
script, workflow and this guide; do not copy application code, calibration data,
credentials, local evidence or private configuration into the downloads repo.
