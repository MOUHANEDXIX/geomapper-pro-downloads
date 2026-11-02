# GeoMapper Pro: Stable 1.0.5 and Beta 1.3.13

Published October 30, 2026. These expanded notes describe the already published installers and their companion website/backend work. Adding these notes does not replace installer bytes, change a version, or change update requirements.

Stable 1.0.5 is the recommended edition without the experimental assistant. Beta 1.3.13 includes the same core improvements plus the assistant and local Ollama workflow. Ordinary height/Z stays unchanged; no vertical datum or geoid calculation has been added. Geocentric Cartesian Z remains a coordinate component.

## GeoMapper Pro Stable v1.0.5

Published: 2026-10-30T16:42:40Z. Installer: [GeoMapperProSetup.exe](https://github.com/MOUHANEDXIX/geomapper-pro-downloads/releases/download/v1.0.5/GeoMapperProSetup.exe) (211,431,507 bytes).

### Coordinates and heights

- Ordinary input height/Z is preserved; no vertical datum or geoid conversion has been added. Geocentric Cartesian Z remains a coordinate component.
- Google Earth export uses the saved results' source system and sheet and preserves the displayed height.
- The website's Carthage geographic / UTM 32 same-datum conversion was corrected. The existing cross-datum model and computational sheet mapping remain unchanged pending independent OTC controls.
- Sheet metadata inspection and an independent-checkpoint comparison tool were added. Internal round trips and held-out checkpoints do not certify survey accuracy.

### Projects, recovery and coordinate import

- Save and reopen .gmproj projects with table cells/results, systems, formats, sheet context, model identity, raster paths/GCP roles/Z and vector paths.
- Project saves are atomic; failed opens preserve the current workspace. Missing linked files can be relocated. Raster pixels and vector geometry remain in their linked source files.
- Recovery drafts are separated by backend, account and edition. Project documents exclude account/session credentials.
- Preview coordinate imports and choose delimiter, header, decimal separator, ID/X/Y/Z/sheet columns and X/Y units. Duplicate mappings are rejected and Z is preserved; limits are 64 MiB and 100,000 rows.
- An offline result map and escaped transformation reports use the actual output. Reopening projects no longer duplicates interface actions.

### Raster controls and diagnostics

- Adding, moving, editing, deleting or changing a GCP role invalidates the old fit. Export requires a successful recalculation, including direct export calls.
- Fit points calculate the affine model; Checkpoints measure held-out error; Excluded points take part in neither. Fit and Checkpoint RMSE and point residuals are reported separately.
- At least three non-collinear Fit controls are still required. Older GCPs default to Fit. The table is read-only; use the GCP edit dialog.
- GCP height/Z survives edits, project saves and reopening. A Checkpoint role alone does not establish independent OTC provenance.

### Raster files and exports

- Corrected world-file pixel-centre calculations and inverse loading, including rotation and shear. Reopen PNG, JPEG and BMP with recognized world-file extensions, PRJ and STT sidecars.
- Embedded TIFF metadata takes precedence over conflicting sidecars. STT is kept as a local-system description without an invented EPSG code.
- Exports encode the chosen supported format through GDAL instead of renaming source bytes. Supported pixel values, nodata, masks and band metadata are preserved; unsupported band/type combinations fail safely.
- Temporary staging and rollback protect existing destination files and sidecars on failure or cancellation. Exporting over the source raster is rejected.

### Responsive coordinate, raster and vector work

- Large coordinate jobs run outside the interface thread. Vector conversion and referenced-raster reprojection support progress, cooperative cancellation and private worker engines.
- STT raster processing uses bounded window reads. Cancellation before publication leaves existing raster outputs intact; vector cancellation retains completed layers and skips remaining ones.
- Late results from an old account/session are discarded. Controls recover after jobs finish, and closing drains native workers asynchronously to avoid late dialogs or thread-destruction crashes.

### Accounts and passwords

- Each backend/account has its own in-memory GIS workspace. Logout removes private pages immediately; another account cannot see the previous account's coordinates, file links, GCPs, vectors or dialogs.
- Callbacks and account dialogs verify their originating session before applying results. Signing back into the same account can recover its unsaved workspace during that application session.
- Password changes/resets revoke existing sessions atomically; reset codes are consumed once. Account locks protect concurrent login/password-change transactions.
- New passwords use 8–128 Unicode characters with at least one non-whitespace character. Intentional edge spaces are significant; exact PBKDF2-SHA256 hashes use 260,000 iterations, while legacy hashes remain supported.

### Plans, payments and administrator controls

- Case-insensitive username/email uniqueness and a non-destructive conflict preflight protect account records. Concurrent requests create one pending payment request per user/plan with randomized references.
- Mark unpaid remains bookkeeping. Separate Suspend/Resume actions control premium access while preserving login and coordinates; paid time continues during suspension, and resuming needs a valid paid period.
- Tier changes take effect at renewal. Account/dashboard responses show the next plan and date; same-tier renewals extend paid time and queued changes follow existing paid/scheduled time.
- Periodic subscription transitions are idempotent. Prices, durations and included modules remain source-controlled; new subscription audit snapshots exclude account credentials and unrelated profile fields.

### Website and update reliability

- Clean local public routes work. Raster previews wait for OTC transformation data before cross-system GCP conversion, preserve GCP Z and keep identity conversions available offline.
- Avatar rendering escapes stored content; password forms clear revoked browser sessions. The dashboard shows suspended access and scheduled plan changes.
- Sensitive authentication actions have identifier-based limits and explicit trusted-proxy parsing. Dependency locks, isolated CI, build receipts and packaging checks improve release reproducibility.
- Desktop updates verify SHA-256 and Ed25519 signatures. Versioned installers are immutable and older releases remain available for rollback; an updater signature is separate from a Windows publisher certificate.

## GeoMapper Pro Beta v1.3.13 - not stable

Published: 2026-10-30T16:42:41Z. Installer: [GeoMapperProBetaSetup.exe](https://github.com/MOUHANEDXIX/geomapper-pro-downloads/releases/download/v1.3.13-beta/GeoMapperProBetaSetup.exe) (213,664,894 bytes).

### All Stable 1.0.5 improvements, plus beta AI

- Beta includes the coordinate, project/recovery, import, raster, vector, account and reliability improvements listed for Stable 1.0.5 above.
- Ordinary height/Z remains unchanged, and no vertical/geoid conversion or independent OTC accuracy certification is introduced.
- The beta assistant supports a local Ollama workflow. Stable excludes the experimental assistant and its AI-only code paths.

### Local validation and raster interpretation

- Deterministic coordinate checks run locally across the full table, including invalid/nonfinite values and duplicate identifiers/coordinates after the first ten rows.
- Fit, Checkpoint and Excluded roles are separated in raster context. Checkpoint RMSE is described as held-out error rather than OTC certification.
- CSV suggestions distinguish Northing from height. Report, support and raster diagnostic sections display the validated result fields.

### Privacy, response validation and session ownership

- Model requests use bounded samples by default. Full dataset context requires both privacy settings to permit it.
- Recursive filtering removes recognized credentials, recovery codes, hashes, sensitive local paths and secret-like text. Arbitrary unlabeled personal text still needs review before sharing.
- Strict schemas validate model responses before display. Invalid responses use deterministic local fallback, and model output cannot remove or lower local warnings.
- AI jobs and conversations are scoped to their account/session; late callbacks after logout are discarded.

## Service operations after these installers were published

P1 added public availability checks, database readiness checks, disposable PostgreSQL staging/restore verification, diagnostic CI limits and future-build publisher-signing preparation. The public monitor checks static website/download metadata every 15 minutes and runs the API/CORS/feed checks every six hours. These are service/release-process changes; they are not a new desktop installer version.

The backend readiness endpoint is live. The P1 website privacy/analytics bundle and this expanded website changelog require a verified Cloudflare deployment. A separate cloud staging project and actual Windows publisher signing remain pending their required organization/permission/identity inputs. Prepared signing support is not an issued publisher certificate, and an Ed25519 updater signature is not Authenticode.

## Accuracy and file-handling limits

- No new independent OTC/checkpoint dataset was supplied. Existing cross-datum calibration and computational sheet mapping have not been silently replaced, and these notes do not certify survey accuracy.
- The corrected Carthage geographic / UTM 32 website route is a same-datum fix. A small internal round-trip error alone is not proof of accuracy against an independent field reference.
- A held-out raster Checkpoint measures error for that point; its role does not prove its provenance or independence from model fitting.
- Project files link raster pixels and vector geometries rather than embedding them. Keep or relocate those source files when sharing a project.
- Raster format/band/type support remains driver-dependent. Unsupported combinations fail rather than silently changing data.
- Tests and synthetic acceptance checks cover selected workflows. Partner acceptance on a separate Windows machine is still useful for the actual files, drivers and account permissions used there.

The website changelog provides English and French sections. The compact backend update-feed summaries, installer versions, publication dates, sizes, URLs, hashes and Ed25519 signatures are preserved by this documentation update.
