# Code Generation Framework for DSLs

This repository contains a generic, extensible framework for evaluating large language models (LLMs) generating code for domain-specific languages (DSLs) from textual specifications. The framework was used in the experiments described in: "Evaluating LLMs for DSL code generation: a framework for well-formedness and correctness" (Journal of Systems and Software, 2026). DOI: https://doi.org/10.1016/j.jss.2026.112871

**Abstract (short)**: The framework evaluates LLM-generated DSL code from two perspectives: well-formedness (syntactic / structural validity) and correctness (satisfying the constraint against the domain model). It supports experiments for constraint languages (OCL and Alloy) and a baseline general-purpose language (Python). The evaluation pipeline supports code generation, automated well-formedness checking, LLM-driven code repair, correctness judging, and producing compact final datasets for analysis.

**Repository layout**
- **datasets/**: Dataset sources, dataset build scripts and example JSON datasets (DS1.json, DS2.json).
- **dslexp/**: Framework code and experiment runners. See [dslexp/readme.md](dslexp/readme.md) for details.
- **_results/**: Generated results (created when running experiments).
- **requirements.txt**: Python dependencies.

**Quick highlights**
- **Run experiments**: The main experiment runner is `dslexp/main.py`. It exposes options for running individual steps, controlling pass@k, selecting domains, templates, languages and options.
- **Dataset format**: The framework expects dataset files in JSON format (see `datasets/readme.md` for the format and how to build datasets using provided scripts).

**Installation**
Prerequisites: Python 3.10+ (3.11 recommended), Git, and optionally Conda.

Conda (recommended):
```bash
conda create -n cg-python python=3.11 -y
conda activate cg-python
pip install -r requirements.txt
```

Pip only (system Python or venv):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `requirements.txt` file pins the packages used for parsing, evaluation tooling and LLM clients (OpenAI / Ollama etc.). Install it before running experiments.

**Environment variables / LLM credentials**
For security the code reads credentials from environment variables using `os.getenv()` (see `dslexp/llm_prompting.py`). Set one of the following depending on the provider you use:

- OpenAI (official API):
	- `OPENAI_API_KEY` — your OpenAI API key (the code uses `os.getenv("OPENAI_API_KEY")`).
- Azure OpenAI:
	- `AZUREAI_ENDPOINT_URL` — your Azure OpenAI endpoint URL
	- `AZUREAI_API_KEY` — your Azure API key
- Ollama / local LLMs:
	- The Ollama client host is configured in `dslexp/llm_prompting.py` (look for `OLlamaClient(host=...)`). Adjust if you run Ollama on a different host/port.

Always keep keys out of source code and do not commit them to repos.

**Running an experiment (examples)**
Run the full experiment on a dataset JSON (example dataset files live in `datasets/`):
```bash
python dslexp/main.py datasets/DS1.json --k 1
```
Run only one step (useful to resume or debug):
```bash
python dslexp/main.py datasets/DS1.json --k 1 --step 1
```
Run a range of steps (from `--start` to `--end`):
```bash
python dslexp/main.py datasets/DS1.json --k 1 --start 1 --end 4
```
Run the code generation step for a single domain (parallelization hint):
```bash
python dslexp/main.py datasets/DS1.json --k 1 --step 1 --domain MyDomain
```

Useful command-line options (see `dslexp/main.py` for full detail):
- `--k` : pass@k (number of generated candidates per task). Default: `1`.
- `--step` : run only this step (integer between 1 and 8). Mutually exclusive with `--start` and `--end`.
- `--start` / `--end` : run steps in the closed interval `[start, end)` (useful to run a sequence of steps).
- `--template` : use a specific prompt template (integer index matched by the prompt logic in `Experiment`).
- `--domain` : filter dataset to one domain (string matching `domain_name`). Useful to parallelize per-domain runs.
- `--language` : restrict to a language (e.g., `OCL`, `ALLOY`, `PYTHON`).
- `--option` : prompt option selector used by the experiment logic (integer).

Notes and constraints:
- `--step` is mutually exclusive with `--start` / `--end`.
- The runner will skip generating outputs that already exist on disk, enabling resumption of interrupted runs.
- Default models and behavior (e.g., `models`, `code_repair_model`, `judging_model`) are defined in `dslexp/main.py` and can be changed there.

**Experiment pipeline (steps)**
The main runner implements the following numbered pipeline (used as `--step` values):
- Step 1: Code generation (pass@k) — generate candidate implementations using configured LLM models.
- Step 2: Well-formedness check — run structural/syntactic checks on generated code.
- Step 3: Well-formedness code repair — attempt to fix invalid code via an LLM-based repair model.
- Step 4: Second pass well-formedness check — re-check repaired code.
- Step 5: Correctness judging — check whether code satisfies the constraint semantic intent.
- Step 6: Correctness code repair — attempt fixes for incorrect solutions via LLM.
- Step 7: Second pass correctness judging — re-check repaired candidates.
- Step 8: Final dataset generation — create compact CSVs with only the fields needed for analysis.

**Outputs and naming**
**Outputs and naming**
- Results are saved under `_results/` (note the leading underscore) in a series of subfolders that map to the pipeline steps:
	- `_results/1_code_generation` — step 1: generated candidates (CSV per domain/model/lang/option/instance)
	- `_results/2_wf_1` — step 2: first-pass well-formedness checks
	- `_results/3_wf_code_repair` — step 3: code repair runs targeting ill-formed solutions
	- `_results/4_wf_2` — step 4: second-pass well-formedness checks after repair
	- `_results/5_corr_1` — step 5: first-pass correctness judging
	- `_results/6_corr_code_repair` — step 6: correctness repair runs
	- `_results/7_corr_2` — step 7: second-pass correctness judging
	- `_results/final` — step 8: compact final CSVs with selected fields for analysis

- Code generation output file names follow the pattern:
	`{DOMAIN}_{MODEL}-{LANG}_op{OPTION}_pass@{K}_instance{N}.csv`

- The final CSVs produced in the `_results/final` folder include the columns:
	`INSTANCE, PASS@K, OPTION, DATASET, MODEL, DOMAIN_NAME, LANGUAGE, PS, TASK, RESULT, W.F., W.F.FEEDBACK, W.F.C.R., CORRECTNESS, C.FEEDBACK, C.C.R.`

**Dataset format**
See `datasets/readme.md` for a detailed description and examples. Important requirements used by the runner (strict):
- The dataset is a JSON array where each entry (domain) must include these fields:
	- `domain_name` (string): unique domain id used in filenames and logs.
	- `domain_context` (string): textual domain context used in prompts (background, prose description).
	- `plantuml_model` (string): TEXTUAL PlantUML model content (the full PlantUML source as a string). **Do not** provide a filesystem path — the framework expects the PlantUML content inline in the JSON.
	- `nl_model` (string): natural-language description of the class diagram (this field is required and is used by prompt templates to describe the model in plain language).
	- `constraints` (array): list of constraint objects. Each constraint object must include:
		- `specification` (string): the natural-language coding task to implement.
		- optional metadata such as `id`, `comment`, `source`.

Minimal example of a dataset JSON element (note `plantuml_model` contains PlantUML text and `nl_model` is present):
```json
{
	"domain_name": "Library",
	"domain_context": "A library domain with Book, Author and Loan entities and typical behaviors...",
	"plantuml_model": "@startuml\nclass Book\nclass Author\nBook --> Author\n@enduml",
	"nl_model": "Books have authors; loans link a borrower with a book and record start/end dates.",
	"constraints": [
		{"specification": "A book must have at least one author."},
		{"specification": "A loan cannot exceed 30 days."}
	]
}
```

If you want to build your own JSON datasets from the original source folders, see the `datasets/` build scripts and `datasets/readme.md`.

**Resuming runs & reproducibility**
- The code generation step checks whether the target CSV already exists and will skip generating again (this enables resuming interrupted runs).
- Default models and repair models are configured in `dslexp/main.py` (variables `models`, `judging_model`, and `code_repair_model`). Modify them there or in the `Experiment` class in `dslexp/explib.py`.

**Citing**
If you use this framework or datasets in research, please cite the paper (DOI above).

**BibTeX (please cite if used)**
```bibtex
@article{DELGADO2026112871,
  title = {A framework for assessing the capabilities of code generation of constraint domain-specific languages with large language models},
  journal = {Journal of Systems and Software},
  pages = {112871},
  year = {2026},
  issn = {0164-1212},
  doi = {https://doi.org/10.1016/j.jss.2026.112871},
  url = {https://www.sciencedirect.com/science/article/pii/S0164121226001044},
  author = {David Delgado and Lola Burgue\u00f1o and Robert Claris\u00f3},
  keywords = {Large language models, Domain-specific languages, framework, code generation, quality},
  abstract = {Large language models (LLMs) can be used to support software development tasks, e.g., through code completion or code generation. However, their effectiveness drops significantly when considering less popular programming languages such as domain-specific languages (DSLs). In this paper, we propose a generic framework for evaluating the capabilities of LLMs generating DSL code from textual specifications. The generated code is assessed from the perspectives of well-formedness and correctness. This framework is applied to a particular type of DSL, constraint languages, focusing our experiments on OCL and Alloy and comparing their results to those achieved for Python, a popular general-purpose programming language. Experimental results show that, in general, LLMs have better performance for Python than for OCL and Alloy. LLMs with smaller context windows such as open-source LLMs may be unable to generate constraint-related code, as this requires managing both the constraint and the domain model where it is defined. Moreover, some improvements to the code generation process such as code repair (asking an LLM to fix incorrect code) or multiple attempts (generating several candidates for each coding task) can improve the quality of the generated code. Meanwhile, other decisions like the choice of a prompt template have less impact. All these dimensions can be systematically analyzed using our evaluation framework, making it possible to decide the most effective way to set up code generation for a particular type of task.}
```

For more details about running experiments and building datasets, see [dslexp/readme.md](dslexp/readme.md) and [datasets/readme.md](datasets/readme.md).


