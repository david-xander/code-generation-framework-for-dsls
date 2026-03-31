# Build the dataset (format and tools)

This folder contains helper scripts used to assemble the JSON datasets used in our experiments and example JSON datasets (`DS1.json`, `DS2.json`). The source data for the `Pan` dataset is similar to the HuggingFace collection referenced in the paper and the Abukhalaf dataset is provided under `Abukhalaf/`.

## Provided build scripts
- `build_Pan_dataset.py` — build a single JSON dataset from the `Pan/` subfolders.
- `build_Abukhalaf_dataset.py` — build a single JSON dataset from the `Abukhalaf/` subfolders.

Run the scripts from this folder:
```bash
python build_Pan_dataset.py Pan DS1.json
python build_Abukhalaf_dataset.py Abukhalaf DS2.json
```

## What the scripts expect
Each domain folder (for example, `Pan/bank/`) typically contains:
- `classdiag.puml` — PlantUML class diagram for the domain.
- `classdiag.txt` — textual serialization of the class diagram (optional).
- `constraints.json` — constraint items and related metadata (used by the builder).
- `spec.txt` — natural language descriptions of the constraints (optional).

## JSON dataset structure
The experiment runner expects a JSON array where every item (domain entry) contains at least these fields (read by `dslexp/main.py`):

- `domain_name` (string): unique domain identifier used in result filenames.
- `domain_context` (string): textual context used in prompts (domain description, background, example usage).
 - `plantuml_model` (string): TEXTUAL PlantUML model content (the full PlantUML source as a string). **Do not** supply a filesystem path; the runner expects the PlantUML source inline in the JSON.
 - `nl_model` (string): a natural-language description of the model (used by prompt templates). This field is required.
- `constraints` (array): list of constraint objects; each constraint object should include:
  - `specification` (string): the natural-language coding task (what the generated code should implement).
  - optional metadata fields such as `id`, `comment`, `source`.

Example JSON element (note `plantuml_model` contains inline PlantUML text):
```json
{
  "domain_name": "Library",
  "domain_context": "A library domain with Book, Author and Loan entities...",
  "plantuml_model": "@startuml\nclass Book\nclass Author\nBook --> Author\n@enduml",
  "nl_model": "Books have authors, loans track borrowers and dates.",
  "constraints": [
    {"specification": "A book must have at least one author."},
    {"specification": "A loan cannot exceed 30 days."}
  ]
}
```

## Notes for replicators
- The build scripts collect model files, constraint descriptions and metadata and output a single JSON array file that the experiment runner expects.
- To create your own dataset, create one folder per domain with the files described above and run the corresponding build script.
- If your source data layout differs, adapt the build script or open an issue and provide the directory layout.

For any further guidance about the exact fields the runner reads, see `dslexp/main.py` and the `Experiment` class in `dslexp/explib.py`.
# Build the dataset
