"""Capture an actual independent Codex model response without editing it.

Uses the existing ChatGPT login, the configured model, and read-only ephemeral
sessions. Run with network access available. No output schema or expected
answer is supplied to the evaluated model.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cwd", type=Path)
    args = parser.parse_args()
    source = args.prompt.resolve()
    output = args.output.resolve()
    if output.exists():
        parser.error(f"Refusing to replace an existing recording: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    executable = shutil.which("codex")
    if not executable:
        parser.error("codex executable not found")
    command = [executable, "exec", "--ephemeral", "--sandbox", "read-only",
               "--skip-git-repo-check", "--color", "never", "--json",
               "--output-last-message", str(output), "-"]
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        command, input=source.read_text(encoding="utf-8"),
        encoding="utf-8", errors="replace", capture_output=True,
        cwd=str(args.cwd.resolve()) if args.cwd else str(source.parent),
    )
    # Output is written directly by Codex. This harness never rewrites it.
    events = output.with_suffix(output.suffix + ".events.jsonl")
    diagnostic = output.with_suffix(output.suffix + ".stderr.log")
    events.write_text(result.stdout, encoding="utf-8")
    diagnostic.write_text(result.stderr, encoding="utf-8")
    metadata = {
        "provider": "Codex CLI / OpenAI / existing ChatGPT authentication",
        "model_selection": "existing Codex configuration; no override",
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "prompt_path": str(source), "prompt_sha256": sha256(source),
        "output_path": str(output),
        "output_sha256": sha256(output) if output.exists() else None,
        "exit_code": result.returncode,
        "events_path": str(events), "diagnostic_path": str(diagnostic),
        "raw_recording": True,
    }
    output.with_suffix(output.suffix + ".metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "exit_code": result.returncode,
                      "sha256": metadata["output_sha256"]}, ensure_ascii=False))
    raise SystemExit(result.returncode or (0 if output.exists() else 1))


if __name__ == "__main__":
    main()
