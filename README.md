# Logistics Accruals Automation Framework

## Project Overview
This framework automates the logistics accruals process which currently relies on large Excel workbooks, manual validations, and data transformations. The tool reads Power BI exports and MBST database dumps, applies business rules, and generates accrual-ready outputs for SAP posting.

---

## Team Roles
- **Mubashir** – Lead Developer (architecture, framework, core modules)
- **Gnanadeep** – Tester + Support Developer (testing, mapping updates, documentation)

---

## Meeting Objectives & Expected Inputs
This session is for gathering all requirements and aligning on deliverables, pain points, and required automation modules.

### Key Questions to Answer in the Meeting:
1. **Which 18 countries/DCs are remaining?**
2. **What are the file formats for Power BI, UTMS, MBST, Final Billing?**
3. **Any outlier plants/countries with different formats or logic?**
4. **What are all the manual intervention steps right now?**
5. **What is the expected output structure for JV/SAP posting?**
6. **What frequency and schedule is expected for this framework to run?**
7. **Will past month files (e.g. July for August accruals) always be stored centrally?**
8. **How are countries expected to send input files (like exceptions)?**
9. **Is the MBST master data fixed or refreshed every month?**
10. **Can plant/ship-to exclusions be maintained centrally?**

---

## Proof of Concept (POC) – Action Items for Stakeholder Review
These items will be demoed in the next meeting as functional POC modules:

| ID | Feature | Description | Owner | Target Date |
|----|---------|-------------|--------|-------------|
| 1  | Power BI File Loader | Load 60MB+ Power BI Excel file, validate columns, extract accrual tab data | Mubashir | Day 3 |
| 2  | Formula Preservation | Re-apply formulas for AO:AS columns after new data paste | Mubashir | Day 4 |
| 3  | Country Mapping Fixer | Auto-correct multiple countries per CC using DC country logic | Mubashir | Day 5 |
| 4  | Exception Exclusion | Load multiple exception files, deduplicate, filter | Mubashir | Day 6 |
| 5  | MBST Mapping Optimizer | Generate reusable mapping from 430MB file | Mubashir | Day 7 |
| 6  | France UTMS Parser | Parse and process July UTMS file, apply % uplift logic | Mubashir | Day 8 |
| 7  | CLI Demo | Run month/country-specific flow with logging | Mubashir | Day 9 |
| 8  | Accrual Output Writer | Output final JV-ready file | Gnanadeep | Day 10 |

---

## Realistic Implementation Timeline (2 Developer Team)

### Week 1: Foundation & Core Engine
- Project scaffolding, CLI setup, logging, folder structure
- Power BI loader module with validations
- Mapping logic, formula handling
- Basic test files for validation

### Week 2: Data Transformations
- Exception file consolidation and filtering
- MBST parser + reusable monthly percentage map
- Output formatter for JV file
- Initial CLI integration for 1 country end-to-end

### Week 3: Special Cases and Testing
- France logic from UTMS files
- Exclusion config for plants and ship-tos
- Final cleanup and formatting logic
- Full test pass with Gnanadeep support

### Week 4: UAT Readiness
- Document usage guide + test instructions
- Final validation across 2–3 sample countries
- Integrate missing day logic
- Package CLI for production use

---

## Folder Structure
```text
project_root/
├── accruals/
│   ├── __init__.py
│   ├── config.py              # Configuration loader (paths, constants)
│   ├── cli.py                 # CLI interface using argparse or typer
│   ├── main.py                # Entry point to run the framework
│   ├── loader/
│   │   ├── __init__.py
│   │   ├── excel_loader.py    # Read/write Excel data (Power BI, MBST, etc.)
│   │   ├── file_validator.py  # Validates column structure, sheet names, etc.
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── mapping.py         # Apply country/plant mapping logic
│   │   ├── exception_handler.py  # Handle exceptions from country inputs
│   │   ├── accrual_engine.py  # Perform base, fuel, waste, and missing calc
│   │   ├── france_logic.py    # France-specific logic using UTMS files
│   ├── outputs/
│   │   ├── __init__.py
│   │   ├── jv_preparer.py     # Output final data for posting
│   │   ├── logger.py          # Loguru setup
├── tests/
│   ├── __init__.py
│   ├── test_mapping.py
│   ├── test_exception_handler.py
│   ├── test_accrual_engine.py
├── data/
│   ├── input/
│   │   ├── power_bi_august.xlsx
│   │   ├── mbst_db.xlsx
│   │   ├── france_utms_july.xlsx
│   ├── output/
│   │   ├── accrual_august_output.xlsx
├── configs/
│   ├── params.yaml            # Month, exclusion list, file names
├── README.md                  # Project overview & instructions
├── requirements.txt           # Required pip packages
```

---

## CLI Example
```bash
python accruals/main.py run --month August --country NL
```

---

## Sample Code Snippets

**main.py**
```python
from accruals.cli import run_cli

if __name__ == '__main__':
    run_cli()
```

**cli.py**
```python
import typer
from accruals.processors.accrual_engine import process_accruals

def run_cli():
    app = typer.Typer()

    @app.command()
    def run(month: str, country: str = "ALL"):
        process_accruals(month, country)

    app()
```

**config.py**
```python
import yaml
from pathlib import Path

CONFIG_PATH = Path("configs/params.yaml")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)
```

**params.yaml**
```yaml
month: "August"
exclude_countries: ["GR", "IR", "UK"]
power_bi_path: "data/input/power_bi_august.xlsx"
mbst_path: "data/input/mbst_db.xlsx"
output_path: "data/output/accrual_august_output.xlsx"
```

**requirements.txt**
```text
openpyxl
pandas
loguru
pyyaml
typer
```

---

## TODO List
- [ ] Validate Power BI input
- [ ] Generate accruals for one country end-to-end
- [ ] Handle MBST mapping file optimization
- [ ] Exclude logic from config
- [ ] Add UTMS France workflow
- [ ] Export final accrual file for JV
- [ ] Full test suite
- [ ] Document workflows

---

> This framework is modular, testable, and ready for future scalability (cloud pipelines, dashboards, APIs).

---


