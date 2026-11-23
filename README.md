# Reconcile

A Python tool for comparing two CSV exports by record ID. It reports added, removed, and changed records, plus duplicate IDs, so a person can review differences without checking rows by hand.

## Try it

Python 3.10+; no packages or API key needed.

```sh
python3 reconcile.py examples/before.csv examples/after.csv --output reconciliation.json
python3 -m unittest -v
```

Use `--key column_name` when your stable ID column is not `id`. Both files need the same column names and order. The sample data is synthetic. The report is saved locally as JSON and includes old and new values for changed fields.

Duplicate IDs are reported and excluded from the comparison because no single row can represent them reliably. Blank IDs or mismatched columns stop the run. Resolve duplicate warnings before relying on the comparison. No data leaves your computer.

## Optional model-written summary

The comparison always comes from the CSV files. A model can draft a short explanation of the JSON report for a reviewer. The draft is labelled `draft_for_review` and does not change the counts or differences.

For an API model, create your own key and set it in your shell. This sends the report values to the API, so use only data you may share. Never commit your key.

```sh
export OPENAI_API_KEY="your-own-key"
python3 reconcile.py examples/before.csv examples/after.csv --explain openai
```

For a local model, install [Ollama](https://ollama.com/), pull a model, and start its local service:

```sh
ollama pull llama3.2
python3 reconcile.py examples/before.csv examples/after.csv --explain ollama --model llama3.2
```

The API default is `gpt-4o-mini`; the local default is `llama3.2`. Use `--model` to select another available model. Set `OLLAMA_HOST` if the local service is elsewhere. API availability and pricing depend on your account. A model failure stops the command without writing a misleading partial report; run again without `--explain` for the deterministic result.

## Why this project

Use it for spreadsheet exports, inventory snapshots, or process records. The report is designed for review; the tool does not make business decisions or connect to live systems.
