# P3 Microsoft Store distribution assessment

Assessment date: 2 November 2026. This completes the roadmap's request to
**consider Store distribution**. It is not a Store submission or a claim that a
package passed Microsoft certification. The standard versioned Windows
installer/update route remains the release path for this patch.

## Decision

Prepare a separate Stable MSIX pilot after the publisher has a verified Partner
Center registration and reserved app identity. Keep Beta's current experimental
distribution while its external model/runtime setup is evaluated. Do not make
Store packaging a replacement for the working installer during the raster patch.

MSIX is the better long-term candidate for Store-managed installation and
updates. The existing EXE can also be submitted, but that route needs trusted
Authenticode signing for the installer and packaged PE files and retains the
publisher's update responsibility. The current Ed25519 updater signature does
not satisfy that publisher-signing requirement.
[Microsoft distribution comparison](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/choose-distribution-path),
[EXE package requirements](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msi/app-package-requirements).

## Observed project readiness

| Area | Evidence | Required Store work |
| --- | --- | --- |
| App identity | No verified Store product/package identity has been supplied in this workspace. | Use the exact reserved Partner Center identity and publisher values; never derive them from a GitHub username or invent a publisher. |
| Windows binaries | Existing PyInstaller/Inno workflow produces distinct x64 Stable/Beta executables with frozen GIS checks and provenance. | Produce a separate full-trust desktop MSIX build; run the actual package under a standard Windows user. |
| Signing/tooling | Existing Ed25519 updater key is available. No Code Signing EKU certificate or SignTool was found in the checked stores/SDK/PATH locations; MakeAppx was not found on PATH or the checked SDK bin location. | Confirm the intended packaging tools and certification tooling before generating a candidate. Do not claim a trusted publisher from an updater signature. |
| Writable data | [paths.py](../app/core/paths.py) uses LocalAppData for frozen writable data and the PyInstaller extraction directory for bundled resources. | Test package redirection, source-file access, export destinations and retained account/project/recovery data. The missing-LocalAppData fallback writes beside the EXE and must not be relied on in a package. |
| Updates | [update_manager.py](../app/core/update_manager.py) downloads a verified EXE and starts the existing installer/restart helper. | Give an MSIX edition its own tested update policy. A Store-managed build must not accidentally launch the direct-install EXE updater. Leave the current direct edition unchanged. |
| GIS helpers | The approved ODA bundle contains 57 files, 72,672,461 bytes, all matching the prior accepted build manifest. Qt/GDAL/PROJ/rasterio/pyogrio are exercised by frozen checks. | Verify helper execution, temporary extraction, DLL/plugin discovery, CAD conversions and licensing/redistribution terms in the actual package. |
| Beta AI | Beta can prepare a local Ollama runtime/model through an explicit user flow. | Review external executable/model downloads and startup behavior before including them in a Store package; no model installation or Store approval is presumed. |
| Acceptance | Existing tests cover source, frozen executables and disposable direct-installer installation/upgrade/uninstall. | Add MSIX install, upgrade, uninstall/data retention, clean-user and Windows App Certification Kit results. Direct-installer tests do not certify MSIX. |

Microsoft requires an active developer account and a reserved app before
submission. Package identity must match the registered values. Microsoft
re-signs certified Store MSIX packages; that does not prove local sideloading or
replace the missing package acceptance results.
[MSIX submission](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/create-app-submission),
[app identity](https://learn.microsoft.com/en-us/windows/apps/publish/view-app-identity-details),
[Store signing guidance](https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-started-with-the-microsoft-store).

## Concrete pilot acceptance

1. Supply the reserved package identity/publisher and choose Stable for the pilot.
   Review Store listing/privacy/support details and redistribution terms.
2. Install or select the approved Windows packaging/certification tools. Build
   from an exact source commit into a new private output directory, recording
   all hashes. No production installer is overwritten.
3. Add an explicit Store edition/update policy and full-trust manifest using the
   real identity. Test paths, permissions, helper processes and file access.
4. Install on a disposable clean Windows account. Test login/session replacement,
   projects/recovery, coordinates/Z, raster/GCP/export/reopen, vector/CAD and
   shutdown. Upgrade from the prior accepted MSIX and check data retention.
5. Run the Windows App Certification Kit and retain its report. Only then submit
   through the owner's verified Partner Center account and inspect certification
   feedback before claiming Store availability.

Package install locations are protected, packaged AppData can be redirected and
helper/process assumptions need real verification. These are reasons to run a
separate pilot, not reasons to silently modify the existing direct build.
[Microsoft desktop packaging preparation](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-prepare).

No Store account was created, name reserved, certificate purchased, MSIX package
signed, developer fee accepted or product submitted by this assessment.
