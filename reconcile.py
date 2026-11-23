import argparse
import csv
import json
import os
import urllib.request
from pathlib import Path


def load_csv(path, key):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        if key not in columns:
            raise ValueError(f"Missing key column: {key}")
        rows = list(reader)
    records = {}
    duplicates = []
    for number, row in enumerate(rows, start=2):
        identifier = row[key].strip()
        if not identifier:
            raise ValueError(f"Blank key at row {number} in {path}")
        if identifier in records:
            duplicates.append(identifier)
        else:
            records[identifier] = row
    return columns, records, sorted(set(duplicates))


def compare(before, after, key="id"):
    before_columns, old, old_duplicates = load_csv(before, key)
    after_columns, new, new_duplicates = load_csv(after, key)
    if before_columns != after_columns:
        raise ValueError("Both CSV files must have the same columns in the same order")
    fields = [column for column in before_columns if column != key]
    uncertain = set(old_duplicates) | set(new_duplicates)
    changed = []
    for identifier in sorted((old.keys() & new.keys()) - uncertain):
        differences = {field: {"before": old[identifier][field], "after": new[identifier][field]}
                       for field in fields if old[identifier][field] != new[identifier][field]}
        if differences:
            changed.append({key: identifier, "fields": differences})
    return {
        "key": key,
        "added": sorted((new.keys() - old.keys()) - uncertain),
        "removed": sorted((old.keys() - new.keys()) - uncertain),
        "changed": changed,
        "duplicate_keys": {"before": old_duplicates, "after": new_duplicates},
        "skipped_duplicate_keys": sorted(uncertain),
        "counts": {"added": len((new.keys() - old.keys()) - uncertain), "removed": len((old.keys() - new.keys()) - uncertain), "changed": len(changed)},
    }


def explain_report(report, provider, model=None):
    chosen_model = model or ("gpt-4o-mini" if provider == "openai" else "llama3.2")
    body = {
        "model": chosen_model,
        "messages": [
            {"role": "system", "content": "Summarize this CSV comparison for a human reviewer in at most 120 words. Use only the JSON report. Mention duplicate warnings. Do not invent causes or say records were fixed."},
            {"role": "user", "content": json.dumps(report)},
        ],
    }
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("Set OPENAI_API_KEY before using --explain openai")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    elif provider == "ollama":
        body["stream"] = False
        url = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
        headers = {"Content-Type": "application/json"}
    else:
        raise ValueError("Unsupported model provider")
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    return (result["choices"][0]["message"]["content"] if provider == "openai" else result["message"]["content"]).strip()


def main():
    parser = argparse.ArgumentParser(description="Compare two CSV exports by a stable record key")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--key", default="id")
    parser.add_argument("--output", default="reconciliation.json")
    parser.add_argument("--explain", choices=("openai", "ollama"), help="Add a model-written summary of the report")
    parser.add_argument("--model", help="Override the provider's default model")
    args = parser.parse_args()
    report = compare(args.before, args.after, args.key)
    if args.explain:
        report["model_summary"] = explain_report(report, args.explain, args.model)
        report["model_summary_status"] = "draft_for_review"
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Added: {report['counts']['added']}, removed: {report['counts']['removed']}, changed: {report['counts']['changed']}")
    if report["skipped_duplicate_keys"]:
        print(f"Review duplicate IDs before relying on the report: {', '.join(report['skipped_duplicate_keys'])}")
    print(f"Review report: {args.output}")


if __name__ == "__main__":
    main()
