<div align="center">

# Microsoft Security Incident Prediction

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-1.4-FFF000?logo=duckdb&logoColor=black)
![PyArrow](https://img.shields.io/badge/PyArrow-24.x-red?logo=apachearrow&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.3-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-%3C2.0-013243?logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%3C1.8-F7931E?logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-3.x-3776AB)
![Poetry](https://img.shields.io/badge/Poetry-dependency%20management-60A5FA?logo=poetry&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?logo=pydantic&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64)
![mypy](https://img.shields.io/badge/mypy-strict-2A6DB2)

> Stack designed for large-scale data (~13M rows / ~2 GB in train): **DuckDB** for
> out-of-core SQL queries without loading the full CSV into RAM, **PyArrow/Parquet** as
> the columnar exchange format between pipeline phases, **configurable chunking** during
> data acquisition.

</div>

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Layer Responsibilities](#3-layer-responsibilities)
4. [Technology Stack & Dependencies](#4-technology-stack--dependencies)
5. [Configuration Layer](#5-configuration-layer)
6. [Expected Outputs per Phase & Model](#6-expected-outputs-per-phase--model)
7. [Output Structure](#7-output-structure)
8. [Quick Start](#8-quick-start)
9. [Roadmap](#9-roadmap)

---

## 1. Overview

End-to-end Machine Learning framework for clustering analysis of Microsoft security
incidents, based on the **GUIDE** dataset, released by Microsoft on Kaggle as part of
*Microsoft Security Incident Prediction*
(<https://www.kaggle.com/datasets/Microsoft/microsoft-security-incident-prediction>).
The codebase is structured around **CRISP-DM** phases (phases 2–5), exposed through a
**Facade API** and driven entirely by **YAML configuration files** — no source code
changes are required to switch datasets, problem types, or hyperparameters.

The architecture enforces strict separation of concerns via established software design
patterns (Facade, Builder, Factory, Template Method, Registry, Strategy, Artifact
Repository, DAO, among others), making each module independently testable and
replaceable.

### 1.1 What Is the GUIDE Dataset?

**GUIDE** (Generalized User Incident Detection and Evaluation) is a real-world
cybersecurity dataset collected by Microsoft from its **Defender XDR** (Extended
Detection and Response) platform — the security product deployed across thousands of
companies worldwide. Over a two-week observation window, Microsoft logged every security
event detected across **6,100+ organizations**, capturing more than **13 million
individual pieces of evidence** organized into **1.6 million alerts** and **1 million
incidents**. Every incident was reviewed by a human security analyst who assigned a
triage label.

### 1.2 Why This Dataset Exists

Security teams receive thousands of security alerts every day. The vast majority are
false alarms. Analysts lose enormous amounts of time investigating threats that do not
exist. This dataset was created to train machine learning models capable of
automatically classifying whether an alert is a genuine threat — helping analysts focus
only on what matters.

### 1.3 What Makes It Unusual

Both the training and the test split contain the full set of columns, **including the
target column `IncidentGrade`**. This is unusual for Kaggle datasets: it means the test
set can be used for a proper final benchmark evaluation rather than only for submission
scoring.

### 1.4 Dataset Scale at a Glance

| Metric                          | Value              |
|----------------------------------|---------------------|
| Training file size               | ~2 GB               |
| Test file size                   | ~1 GB               |
| Total evidence rows (train)      | ~13 million rows    |
| Total incidents                  | ~1 million          |
| Total alerts                     | ~1.6 million        |
| Organizations represented        | 6,100+              |
| MITRE ATT&CK techniques covered  | 441                 |
| Entity types                     | 33                  |
| Observation window               | 2 weeks             |

### 1.5 The Three-Level Hierarchy

Each **row in the CSV is a piece of evidence**. Evidence is the most granular unit:
multiple evidence rows are grouped into an alert, and multiple alerts are grouped into an
incident.

```
Incident  (1 row per incident — identified by IncidentId)
  └── Alert  (1 or more alerts per incident — identified by AlertId)
        └── Evidence  (1 or more evidence rows per alert — each CSV row)
                └── Entity  (the object involved: a file, an IP, a user...)
```

Because a single incident can involve many entities across many alerts, **the same
`IncidentId` and `IncidentGrade` repeat across multiple rows**. This is intentional — the
label is assigned at the incident level and propagated to every evidence row belonging
to that incident.

### 1.6 Train vs Test Split

| Feature                     | Train                          | Test                              |
|-------------------------------|----------------------------------|-------------------------------------|
| Approximate rows              | ~13 million                     | ~6 million                          |
| Contains `IncidentGrade`      | Yes                              | Yes                                 |
| Contains `Usage` column       | No                               | Yes                                 |
| Recommended usage              | All development phases (2–4)   | Final evaluation only (Phase 4.3)   |

The `Usage` column appears only in the test split. It indicates how each row was
originally intended to be used in the original Kaggle benchmark partition.

---

## 2. Project Structure

```
Project_ML_Security_Incident_Prediction/
│
├── config/                                        # YAML-driven configuration — no hardcoded params
│   ├── datasets/
│   │   └── dataset_config.yml                     # Source: path, separator, encoding, chunking strategy
│   ├── pipelines/
│   │   ├── active_profile.yml                      # Active pipeline profile
│   │   ├── base_pipeline_config.yml                # Phase 2 config
│   │   └── clustering_pipeline_config.yml          # Phases 3→5 config
│   └── rule/
│       ├── categoria_dataset.json                  # Feature categorization rules
│       ├── regole_business_soc.json                # SOC domain rules for validation
│       └── schema_dataset.json                     # Reference dataset schema
│
├── data/                                          # Raw data only — never modified by the pipeline
│   └── raw/
│       ├── train/                                 # GUIDE_Train.csv (~13M rows, ~2 GB)
│       └── test/                                  # GUIDE_Test.csv  (~6M rows,  ~1 GB)
│
├── docs/                                          # Project documentation
│
├── notebooks/                                     # Entry points — delegate exclusively to api/
│
├── outputs/                                       # All pipeline outputs (auto-generated, git-ignored)
│   └── runs/<task>/<dataset_key>/<timestamp>/
│
├── src/
│   └── crispdm/                                   # Core framework package
│       ├── api/                                   # ← Facade layer (only public interface)
│       ├── common/                                # ← Cross-cutting utilities
│       ├── configuration/                         # ← Config subsystem: Load → DTO → Validate → Build
│       ├── data/                                  # ← Data ingestion & quality
│       ├── feature/                                # ← Feature engineering & splitting
│       ├── interpretation/                         # ← Explainability & error analysis
│       ├── model/                                 # ← Training, evaluation & registry
│       ├── phase/                                  # ← CRISP-DM phase runners
│       ├── pipeline/                               # ← Task-level orchestrators
│       ├── registry/                                # ← Model/algorithm registry
│       ├── reporting/                               # ← Artifact persistence & plots
│       ├── __init__.py
│       └── main.py                                 # Framework entry point
│
├── pyproject.toml                                 # Poetry dependency manifest
├── poetry.lock                                    # Locked dependency tree
└── README.md                                      # This file — technical architecture
```

---

## 3. Layer Responsibilities

Each layer maintains a strict contract, enabling independent phase execution without
forcing unnecessary re-runs.

| Layer | Responsibility | Key Components |
|-------|-----------------|-------------------|
| **API** | Single entry point (Facade). Hides all internal complexity from notebooks. | `api/` |
| **Configuration** | Four-step configuration subsystem: Load → Resolve → Validate → Build. | `configuration/` |
| **Common** | Stateless cross-cutting utilities, no business logic, usable from any layer. | `common/` |
| **Data** | Raw data ingestion and structural characterisation. No transformation occurs in this layer. | `data/` |
| **Feature** | Cleaning, encoding, feature engineering and scaling. Applied sequentially in Phase 3. | `feature/` |
| **Model** | Algorithm selection, training and evaluation of the clustering models (K-Means, DBSCAN). | `model/` |
| **Interpretation** | Post-training analysis for model transparency: cluster interpretation and result diagnostics. | `interpretation/` |
| **Phase** | Independent runners for the four CRISP-DM phases. Phase 2 is task-agnostic; Phases 3–5 are task-aware. | `phase/` |
| **Pipeline** | Task-level orchestrators: one runner per problem type, calling phases 2→5 in sequence. No algorithm logic lives here. | `pipeline/` |
| **Registry** | Dynamic registry of available algorithms, decoupling algorithm selection from its implementation. | `registry/` |
| **Reporting** | Artifact persistence following the *artifact policy*: output exclusively as PNG or JSON. | `reporting/` |
| **Entry Point** | Main entry point for the entire application. | `main.py` |

---

## 4. Technology Stack & Dependencies

The project uses **Poetry** for dependency management, with Python `>=3.10,<3.11`.

### Core Dependencies (runtime)

| Library              | Version          | Role in the pipeline                                                 |
|------------------------|-------------------|--------------------------------------------------------------------------|
| `pandas`               | `>=2.3.3,<3.0`    | Tabular data manipulation                                                |
| `numpy`                 | `<2`               | Core numerical computing                                                 |
| `duckdb`                | `>=1.4.4,<2.0`    | Out-of-core SQL queries on the ~2 GB CSV, without loading it fully into RAM |
| `pyarrow`               | `>=24.0.0,<25.0`  | Columnar Parquet format, efficient data exchange between phases          |
| `scikit-learn`          | `<1.8.0`          | Clustering algorithms (K-Means, DBSCAN) and validation metrics           |
| `xgboost`               | `>=3.2.0,<4.0`    | Tree-based algorithms for supervised comparison/benchmarking             |
| `category-encoders`     | `<2.9.0`          | Advanced categorical encoding (Frequency/Ordinal)                        |
| `pydantic`              | `>=2.13.4,<3.0`   | Configuration validation and typing (DTOs)                               |
| `omegaconf`             | `>=2.3.0,<3.0`    | Hierarchical merging and resolution of YAML files                        |
| `pyyaml`                | `>=6.0.3,<7.0`    | Parsing of YAML configuration files                                      |
| `matplotlib` / `seaborn` | `>=3.10.7` / `>=0.13.2` | Statistical visualization and graphical reporting               |
| `kagglehub`             | `==0.3.3`         | Programmatic download of the GUIDE dataset from Kaggle                   |

### Development Dependencies (dev)

| Tool                | Role                                                            |
|-----------------------|--------------------------------------------------------------------|
| `jupyterlab` / `notebook` / `jupyter` | Notebook environment for exploratory analysis and reporting |
| `ipykernel` / `ipywidgets`             | Kernel and interactive widgets for notebooks                |
| `ruff`                                  | Linting and code formatting (NumPy docstring style)          |
| `mypy`                                  | Static type-checking in `strict` mode                        |
| `pandas-stubs`                          | Type annotations for pandas                                   |
| `deptry`                                | Detection of unused/missing dependencies                      |
| `scipy`                                 | Statistical tests (Kolmogorov-Smirnov, distributions)          |

---

## 5. Configuration Layer

All pipeline behaviour is controlled through YAML. No source code changes are needed to
switch algorithms, hyperparameters, feature strategies, or output settings.

### Files

```
config/
├── datasets/
│   └── dataset_config.yml                     # Source: path, separator, encoding, chunking strategy
├── pipelines/
│   ├── active_profile.yml                      # Active pipeline profile
│   ├── base_pipeline_config.yml                # Phase 2 config
│   └── clustering_pipeline_config.yml          # Phases 3→5 config
└── rule/
    ├── categoria_dataset.json                  # Feature categorization rules
    ├── regole_business_soc.json                # SOC domain rules
    └── schema_dataset.json                     # Reference dataset schema
```

### Dataset Config Key Fields (`dataset_config.yml`)

| Field                     | Value                               | Note                                                             |
|-----------------------------|----------------------------------------|----------------------------------------------------------------------|
| `paths.train`                | `data/raw/train/GUIDE_Train.csv`     | ~13M rows, ~2 GB                                                    |
| `paths.test`                 | `data/raw/test/GUIDE_Test.csv`       | ~6M rows, ~1 GB                                                     |
| `csv_params.sep`             | `,`                                    | —                                                                     |
| `csv_params.low_memory`      | `false`                                | **Critical** — prevents silent dtype corruption on large files       |
| `download_executor`          | `src/crispdm/data/download_data.py`  | Reference to the acquisition module                                  |

---

## 6. Expected Outputs per Phase & Model

All outputs follow the **artifact policy**: every item is a PNG, JSON, or Parquet file,
persisted under `outputs/runs/<task>/<dataset_key>/<timestamp>/`. Each phase produces a
set of self-descriptive artifacts, inspectable without re-running the code:

| Phase | Folder | Main Artifacts | Content |
|-------|---------|-------------------|-----------|
| **Phase 2 — Data Understanding** | `phase2_data_understanding/` | `*.parquet`, `*.json`, `*.png` | Stratified train/test sample, column schema, cardinality, missing data, leakage, data drift, visual EDA |
| **Phase 3 — Data Preparation** | `phase3_data_preparation/` | `*.parquet`, `*.json` | Selected/cleaned features, encoding (Frequency/Ordinal), feature engineering, final model-ready dataset |
| **Phase 4 — Modeling** | `phase4_data_modeling/` | `*.pkl`, `*.parquet`, `*.json`, `*.png` | Trained models (K-Means, DBSCAN), hyperparameter tuning, cluster assignment, internal validation metrics |
| **Phase 5 — Evaluation & Interpretation** | `phase5_evaluation_and_interpretation/` | `*.json`, `*.png` | Cluster profiles, confusion matrices, process audit, decision-making recommendations |

This structure guarantees that each phase is **independently auditable**: a reviewer can
inspect the artifacts of a single phase without having to re-run the entire upstream
pipeline.

---

## 7. Output Structure

Every run produces a self-contained, reproducible snapshot under `outputs/`:

```
outputs/runs/<task>/<dataset_key>/<timestamp>/
├── logs/                                        # Full execution log
├── phase2_data_understanding/
├── phase3_data_preparation/
├── phase4_data_modeling/
└── phase5_evaluation_and_interpretation/
```

---

## 8. Quick Start

### Prerequisites

- Python 3.10
- [Poetry 2.0+](https://python-poetry.org/docs/#installation) installed

### Installation & Execution

```bash
# 1. Clone the repository
git clone https://github.com/Catalinaqi/Project_ML_Security_Incident_Prediction.git
cd Project_ML_Security_Incident_Prediction

# 2. Install dependencies via Poetry (core + dev tools)
poetry install

# 3. Configure the active profile (dev vs prod)
# Edit config/pipelines/active_profile.yml to set sample_rows
# or to run the full ~13M-row dataset

# 4. Run the pipeline via the Facade API
poetry run python src/crispdm/main.py
```

### Code Quality Checks (Dev)

```bash
poetry run ruff check .
poetry run mypy src/
poetry run deptry src/
```

---

## 9. Roadmap

* [x] **Phase 2**: Data Understanding — acquisition, stratified sampling, statistical diagnostics.
* [x] **Phase 3**: Data Preparation — selection, cleaning, encoding (Frequency/Ordinal) and feature engineering.
* [x] **Phase 4**: Modeling — training and tuning of K-Means and DBSCAN, internal validation (Silhouette, Davies-Bouldin).
* [x] **Phase 5**: Evaluation & Interpretation — cluster interpretation, K-Means vs DBSCAN comparison, audit and decision making.
* [ ] **Evolution toward CRISP-ML(Q)**: extend the current workflow with the explicit *Monitoring* and *Maintenance* phases of CRISP-ML(Q), to manage cluster drift over time on production data.
* [ ] **Refactoring**: containerization (Docker) and CI/CD pipelines.
* [ ] **MLflow integration**: experiment tracking and model registry.
* [ ] **Supervised benchmark**: systematic comparison between the unsupervised clustering approach and a supervised classifier (XGBoost) on the same feature space.
* [ ] **Unit & integration testing**: extended test coverage across the `feature/`, `model/`, and `phase/` modules.