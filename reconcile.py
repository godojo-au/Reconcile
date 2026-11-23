import argparse
import csv
import json
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
    changed = []
    for identifier in sorted(old.keys() & new.keys()):
        differences = {field: {"before": old[identifier][field], "after": new[identifier][field]}
                       for field in fields if old[identifier][field] != new[identifier][field]}
        if differences:
            changed.append({key: identifier, "fields": differences})
    return {
        "key": key,
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "changed": changed,
        "duplicate_keys": {"before": old_duplicates, "after": new_duplicates},
        "counts": {"added": len(new.keys() - old.keys()), "removed": len(old.keys() - new.keys()), "changed": len(changed)},
    }


def main():
    parser = argparse.ArgumentParser(description="Compare two CSV exports by a stable record key")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--key", default="id")
    parser.add_argument("--output", default="reconciliation.json")
    args = parser.parse_args()
    report = compare(args.before, args.after, args.key)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Added: {report['counts']['added']}, removed: {report['counts']['removed']}, changed: {report['counts']['changed']}")
    print(f"Review report: {args.output}")


if __name__ == "__main__":
    main()
