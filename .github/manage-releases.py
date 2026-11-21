import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

MAX_APK = 100 * 1024 * 1024


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(apk, channel, filename, tools):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.apk", filename):
        raise ValueError("Nama fail APK tidak sah.")
    if not apk.is_file() or not 0 < apk.stat().st_size <= MAX_APK:
        raise ValueError("APK tiada dalam folder app atau saiznya melebihi had.")
    signed = subprocess.check_output([tools / "apksigner", "verify", "--print-certs", apk],
                                     text=True)
    digests = re.findall(r"^Signer #[0-9]+ certificate SHA-256 digest: ([a-f0-9]{64})$",
                         signed, re.MULTILINE)
    if digests != [channel["signerSha256"]]:
        raise ValueError("Sijil APK tidak sepadan dengan app berdaftar.")
    badging = subprocess.check_output([tools / "aapt", "dump", "badging", apk], text=True)
    package = re.search(r"^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']+)'",
                        badging, re.MULTILINE)
    if not package or package[1] != channel["package"]:
        raise ValueError("Pakej APK tidak sepadan dengan app berdaftar.")
    version = package[3]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Nombor versi mesti dalam format seperti 1.2.3.")
    with apk.open("rb") as stream:
        checksum = hashlib.file_digest(stream, "sha256").hexdigest()
    return dict(version=version, versionCode=int(package[2]), apk=filename,
                sha256=checksum, size=apk.stat().st_size)


def run(action, app, filename, notes, tools):
    channels = load_json(Path(".github/channels.json"))
    if app not in channels:
        raise ValueError("App belum didaftarkan dalam saluran pengedaran.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", app):
        raise ValueError("Nama saluran tidak sah.")
    folder = Path(app)
    manifest = folder / "latest.json"
    current = load_json(manifest) if manifest.exists() else None

    if action == "Terbitkan":
        if not filename or not notes.strip() or len(notes.encode()) > 4000:
            raise ValueError("Isi nama APK dan nota keluaran, sehingga 4,000 bait.")
        result = validate(folder / filename, channels[app], filename, tools)
        if result["versionCode"] <= (current or {}).get("versionCode", 0):
            raise ValueError("Kod versi APK mesti lebih tinggi daripada keluaran semasa.")
        updated = {**result, "notes": notes.strip()}
    else:
        if not current:
            raise ValueError("Saluran ini belum mempunyai keluaran.")
        if action in ("Semak", "Sambung"):
            result = validate(folder / current["apk"], channels[app], current["apk"], tools)
            if any(current.get(key) != value for key, value in result.items()):
                raise ValueError("Butiran APK tidak sepadan dengan maklumat keluaran.")
        updated = dict(current)
        if action == "Jeda":
            updated["paused"] = True
        elif action == "Sambung":
            updated.pop("paused", None)

    if updated != current:
        temp = manifest.with_suffix(".tmp")
        temp.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(manifest)

    status = "Dijeda" if updated.get("paused") else "Aktif"
    print(f"{channels[app]['name']} {updated['version']} · {status}")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(f"## {channels[app]['name']}\n\n"
                         f"Operasi **{action}** · Versi **{updated['version']}** · {status}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["Semak", "Terbitkan", "Jeda", "Sambung"])
    parser.add_argument("app")
    parser.add_argument("--apk", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--tools", type=Path, required=True)
    opts = parser.parse_args()
    try:
        run(opts.action, opts.app, opts.apk, opts.notes, opts.tools)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
