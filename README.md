# Reconcile

A small Python tool for comparing two CSV exports by record ID. It reports added, removed, and changed records, plus duplicate IDs, so a person can review differences without checking rows by hand.

## Try it

Python 3.10+; no packages or API key needed.

```sh
python3 reconcile.py examples/before.csv examples/after.csv --output reconciliation.json
python3 -m unittest -v
```

Use `--key column_name` when your stable ID column is not `id`. Both files need the same column names and order. The sample data is synthetic. The report is saved locally as JSON and includes old and new values for changed fields.

Duplicate IDs are reported, and only their first row is compared. Blank IDs or mismatched columns stop the run. Check duplicate warnings before relying on the comparison. No data leaves your computer.

## Why this project

This is a portfolio demonstration of a repeatable data quality workflow. It can help with spreadsheet exports, inventory snapshots, or process records. It does not make business decisions or claim to reconcile live systems.
