"""Bounded, anonymous public checks; reports never contain URLs or response bodies."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SITE = "https://geomapperpro.pages.dev"
API = "https://geomapper-pro-backend.onrender.com"
DOWNLOAD_REPO = "MOUHANEDXIX/geomapper-pro-downloads"
MAX_BODY = 524288
CDN_HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
FIELDS = ("channel", "latest_version", "download_url", "sha256", "signature", "signature_algorithm",
          "installer_filename", "installer_size_bytes")


class BodyTooLarge(ValueError):
    pass


def origin(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path not in ("", "/") or parsed.port not in (None, 443)):
        raise ValueError("Invalid public origin")
    host = parsed.hostname.lower()
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError("Invalid public origin")
    except ValueError:
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}", host) or host.endswith((".local", ".localhost")):
            raise ValueError("Invalid public origin") from None
    return value.rstrip("/")


class SafeRedirects(HTTPRedirectHandler):
    max_redirections = 3

    def __init__(self, hosts):
        self.hosts = hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if (parsed.scheme != "https" or parsed.hostname not in self.hosts or parsed.username
                or parsed.password or parsed.port not in (None, 443)):
            raise ValueError("Unsafe redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, *, method="GET", origin_header=None, timeout=15):
    headers = {"User-Agent": "GeoMapper-Public-Monitor/1", "Accept": "application/json,text/html,*/*"}
    if origin_header:
        headers["Origin"] = origin_header
    host = urlsplit(url).hostname
    hosts = CDN_HOSTS if host == "github.com" else {host}
    opener = build_opener(SafeRedirects(hosts))
    with opener.open(Request(url, headers=headers, method=method), timeout=timeout) as response:
        values = {key.lower(): value for key, value in response.headers.items()}
        body = response.read(MAX_BODY + 1) if method == "GET" else b""
        if len(body) > MAX_BODY:
            raise BodyTooLarge("Response exceeds inspection limit")
        return response.status, values, body


def release(value, channel, repository):
    """Validate public metadata without treating it as verified installer bytes."""
    if not isinstance(value, dict) or value.get("channel") != channel:
        raise ValueError("Invalid release metadata")
    version = value.get("latest_version")
    if not isinstance(version, str) or len(version) > 40 or not re.fullmatch(r"\d+(?:\.\d+){1,3}(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Invalid release metadata")
    filename = "GeoMapperProSetup.exe" if channel == "stable" else "GeoMapperProBetaSetup.exe"
    tag = f"v{version}" + ("-beta" if channel == "beta" else "")
    parsed = urlsplit(value.get("download_url", ""))
    parts = [unquote(part) for part in parsed.path.split("/")]
    if (parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.query or parsed.fragment
            or len(parts) != 7 or "/".join(parts[1:3]) != repository
            or parts[3:5] != ["releases", "download"] or parts[-1] != filename
            or parts[-2] != tag or any("/" in part for part in parts[1:])):
        raise ValueError("Invalid release metadata")
    size = value.get("installer_size_bytes")
    if type(size) is not int or not 0 < size < 4_294_967_296 or value.get("installer_filename") != filename:
        raise ValueError("Invalid release metadata")
    sha = value.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", sha):
        raise ValueError("Invalid release metadata")
    if value.get("signature_algorithm") != "ed25519-sha256":
        raise ValueError("Invalid release metadata")
    try:
        if len(base64.b64decode(value.get("signature", ""), validate=True)) != 64:
            raise ValueError("Invalid signature metadata")
    except (ValueError, TypeError):
        raise ValueError("Invalid release metadata") from None
    result = {key: value[key] for key in FIELDS}
    result["sha256"] = sha.lower()
    return result


class Monitor:
    def __init__(self, site=SITE, api=API, repository=DOWNLOAD_REPO, *, transport=fetch, sleep=time.sleep):
        self.site, self.api = origin(site), origin(api)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Invalid repository")
        self.repository, self.transport, self.sleep = repository, transport, sleep
        self.checks = {}

    def mark(self, name, ok, reason=None, **fields):
        self.checks[name] = {"ok": bool(ok), **fields}
        if reason and not ok:
            self.checks[name]["reason"] = reason

    def request(self, name, url, *, method="GET", api=False, timeout=15):
        started = time.monotonic()
        status, headers, body = None, {}, b""
        try:
            status, headers, body = self.transport(url, method=method,
                origin_header=self.site if api else None, timeout=timeout)
            self.mark(name, 200 <= status < 300, None if 200 <= status < 300 else "HTTPStatus")
        except HTTPError as error:
            status = error.code
            try:
                error.close()
            except Exception:
                pass
            self.mark(name, False, "HTTPStatus")
        except (TimeoutError, URLError) as error:
            timed_out = isinstance(error, TimeoutError) or isinstance(getattr(error, "reason", None), TimeoutError)
            self.mark(name, False, "Timeout" if timed_out else "NetworkError")
        except BodyTooLarge:
            self.mark(name, False, "ResponseTooLarge")
        except Exception:
            self.mark(name, False, "TransportError")
        self.checks[name].update(status=status, elapsed_ms=round((time.monotonic() - started) * 1000))
        if api and self.checks[name]["ok"] and headers.get("access-control-allow-origin") not in (self.site, "*"):
            self.checks[name].update(ok=False, reason="CORSRejected")
        return (headers, body) if self.checks[name]["ok"] else None

    def document(self, name, response):
        if response is None:
            return None
        try:
            value = json.loads(response[1])
            if not isinstance(value, dict):
                raise ValueError("Expected an object")
            return value
        except Exception:
            self.checks[name].update(ok=False, reason="InvalidJSON")
            return None

    def metadata(self, name, value, channel):
        try:
            result = release(value, channel, self.repository)
            self.mark(name, True, version=result["latest_version"])
            return result
        except Exception:
            self.mark(name, False, "InvalidReleaseMetadata")
            return None

    def download(self, name, value):
        response = self.request(name, value["download_url"], method="HEAD")
        if response is None:
            return
        try:
            matches = int(response[0].get("content-length", "")) == value["installer_size_bytes"]
        except (TypeError, ValueError):
            matches = False
        if not matches:
            self.checks[name].update(ok=False, reason="DownloadSizeMismatch")

    def ready(self):
        attempts = []
        for index, timeout in enumerate((75, 45)):
            response = self.request("api.readiness", self.api + "/readyz", api=True, timeout=timeout)
            value = self.document("api.readiness", response)
            if value is not None and value.get("ok") is not True:
                self.checks["api.readiness"].update(ok=False, reason="NotReady")
            check = self.checks["api.readiness"]
            attempts.append(dict(check))
            if check["ok"]:
                break
            retry = (check.get("status") in (502, 503, 504) or check.get("reason") in ("Timeout", "NetworkError", "InvalidJSON"))
            if index == 0 and retry:
                self.sleep(15)
            else:
                break
        self.checks["api.readiness"]["attempts"] = attempts
        return self.checks["api.readiness"]["ok"]

    def run(self, mode="static"):
        if mode not in ("static", "full"):
            raise ValueError("Unknown monitor mode")
        self.checks = {}
        home = self.request("site.home", self.site)
        if home is not None and b"GeoMapper" not in home[1]:
            self.checks["site.home"].update(ok=False, reason="UnexpectedWebsite")
        config_response = self.request("site.config", self.site + "/config.js")
        config = None
        if config_response is not None:
            try:
                match = re.fullmatch(rb"\s*window\.GeoMapperWebConfig\s*=\s*(\{.*\})\s*;\s*", config_response[1], re.S)
                config = json.loads(match[1]) if match else None
                if not isinstance(config, dict) or origin(config.get("apiBaseUrl", "")) != self.api or origin(config.get("siteUrl", "")) != self.site:
                    raise ValueError("Configuration mismatch")
            except Exception:
                self.checks["site.config"].update(ok=False, reason="ConfigurationMismatch")
                config = None
        changelog = self.document("site.changelog", self.request("site.changelog", self.site + "/changelog.json"))
        items = changelog.get("releases", []) if changelog else []
        releases = {}
        for channel, field in (("stable", "downloadUrl"), ("beta", "betaDownloadUrl")):
            rows = [item for item in items if isinstance(item, dict) and item.get("channel") == channel] if isinstance(items, list) else []
            value = self.metadata(channel + ".metadata", rows[0] if rows else None, channel)
            if value is not None:
                releases[channel] = value
                self.mark(channel + ".site_link", config is not None and config.get(field) == value["download_url"], "ConfigurationMismatch")
                self.download(channel + ".download", value)
        if mode == "full" and self.ready():
            health = self.document("api.health", self.request("api.health", self.api + "/healthz", api=True))
            if health is not None and health.get("ok") is not True:
                self.checks["api.health"].update(ok=False, reason="Unhealthy")
            for channel in ("stable", "beta"):
                name = "api." + channel
                feed = self.document(name, self.request(name, self.api + "/app/version?" + urlencode({"current_version": "0.0.0", "channel": channel}), api=True))
                value = self.metadata(name + ".metadata", feed, channel)
                if value is not None:
                    self.mark(name + ".site_agreement", value == releases.get(channel), "ReleaseMetadataMismatch")
                    if channel not in releases:
                        self.download(name + ".download", value)
        return {"schema_version": 1, "checked_at": datetime.now(timezone.utc).isoformat(), "mode": mode,
                "passed": all(check["ok"] for check in self.checks.values()), "checks": self.checks,
                "scope": "Anonymous website, metadata and HEAD availability checks; full mode adds API readiness. Installer bytes/signatures, authenticated actions and mail delivery are not verified."}


def summary(report):
    lines = ["## GeoMapper public monitoring", "", f"Result: **{'PASS' if report['passed'] else 'FAIL'}** ({report['mode']}).", "",
             "| Check | Result | HTTP | Detail |", "| --- | --- | --- | --- |"]
    for name, check in report["checks"].items():
        lines.append(f"| {name} | {'PASS' if check['ok'] else 'FAIL'} | {check.get('status') or '—'} | {check.get('reason', '') if not check['ok'] else ''} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("static", "full"), default="static")
    parser.add_argument("--site", default=SITE)
    parser.add_argument("--api", default=API)
    parser.add_argument("--download-repository", default=DOWNLOAD_REPO)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        monitor = Monitor(args.site, args.api, args.download_repository)
    except Exception:
        parser.error("Invalid endpoint/repository configuration; use public HTTPS origins without credentials or query strings.")
    report = monitor.run(args.mode)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "monitor.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "summary.md").write_text(summary(report), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "mode": report["mode"], "checks": len(report["checks"])}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
