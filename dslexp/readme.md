# Experiment runner (dslexp)

This folder contains the experiment code and runner used to evaluate LLMs on DSL generation tasks.

The main entry is `main.py`. It implements the full evaluation pipeline and exposes the CLI options used to control pass@k, individual steps, templates, domain filtering and more. For a full project-level overview and examples, see the root README.

Quick usage (run from the repo root or from this folder):

```bash
# from repo root
python dslexp/main.py path/to/dataset.json --k 1

# run only step 1 for domain MyDomain
python dslexp/main.py path/to/dataset.json --k 1 --step 1 --domain MyDomain

# run steps 1..4
python dslexp/main.py path/to/dataset.json --k 1 --start 1 --end 4
```

Key implementation notes:
- The `Experiment` class (in `explib.py`) encapsulates the code generation and prompting logic.
- Models used for generation and repair are configured in `main.py` (variables `models`, `code_repair_model`, and `judging_model`).
- The runner writes intermediate CSVs into `_results/1_code_generation` and subsequent step folders. The final compact CSVs are written into `_results/final`.
- The code generation step will skip already-existing output files; this allows safe resumption after interruption.

Environment / LLM configuration:
- The code reads API keys from environment variables using `os.getenv()` — see `dslexp/llm_prompting.py` for the exact variable names (`OPENAI_API_KEY`, `AZUREAI_ENDPOINT_URL`, `AZUREAI_API_KEY`) and implementations for each provider.
- The Ollama client host is configured inside `dslexp/llm_prompting.py` (search for `OLlamaClient(host=...)`). If you run Ollama on a different host or port, change the host string there.

Result folders mapping:
- Outputs are stored under `_results/` with per-step subfolders (see root README for the full mapping). Adjust paths in `dslexp/main.py` if you want a different base results directory.

If you need to change prompt templates, look for template helpers and prompt files in this folder or in the `datasets` prompts files shipped with the dataset.

For dataset format, examples and build scripts, see `datasets/readme.md`.