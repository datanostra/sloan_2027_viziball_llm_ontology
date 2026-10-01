# From Play-by-Play to Semantic Analytics

## A Possession-Based Basketball Ontology for LLM Question Answering

This repository contains the experimental pipeline and benchmark associated with the research project:

**From Play-by-Play to Semantic Analytics: A Possession-Based Basketball Ontology for LLM Question Answering**

The project investigates whether basketball play-by-play data can be transformed into a semantic, possession-based representation that allows a Large Language Model (LLM) to answer contextual basketball questions without generating analytical SPARQL queries.

Instead of asking the LLM to directly query raw basketball data, the system exposes a controlled basketball ontology. The LLM maps natural-language questions to ontology concepts and analytical operations, while deterministic query execution retrieves the corresponding information from the knowledge graph.

The benchmark evaluates both the semantic interpretation performed by the LLM and the correctness of the ontology-based analytical results.

---

## Overview

The experimental pipeline is:

```text
Basketball play-by-play data
        │
        ▼
Action reconstruction
        │
        ▼
Possession reconstruction
        │
        ▼
RDF knowledge graph
        │
        ▼
Basketball ontology
        │
        ▼
Semantic inference
        │
        ▼
Natural-language question
        │
        ▼
LLM ontology interpretation
        │
        ▼
Deterministic ontology query
        │
        ▼
Answer
```

The LLM does **not generate SPARQL queries**.

Its role is restricted to translating a natural-language question into a structured semantic query based on the ontology.

For example:

```text
Question:
"What proportion of possessions while trailing resulted in points?"
```

can be mapped to:

```python
{
    "concepts": [
        "TrailingPossession",
        "ScoringPossession"
    ],
    "operation": "RATIO",
    "denominator_concepts": [
        "TrailingPossession"
    ]
}
```

The analytical result is then computed deterministically from the RDF graph.

---

## Ontology

The possession-based ontology defines basketball concepts that can be composed to express contextual analytical questions.

Examples include:

```text
LateGameSituation
CloseGameSituation
ClutchSituation

LeadingPossession
TrailingPossession
TiedPossession
OnePossessionGameSituation

ScoringPossession
TurnoverPossession
SecondChancePossession
ThreePointScoringPossession
```

Concepts can be combined.

For example:

```text
TrailingPossession
        +
ScoringPossession
```

represents possessions in which the offensive team was trailing and subsequently scored.

This allows complex basketball situations to be expressed semantically without manually implementing one analytical query for every possible combination.

---

## Benchmark

The ontology benchmark contains **100 natural-language questions**.

Questions cover several dimensions, including:

- direct ontology questions;
- linguistic paraphrases;
- implicit formulations;
- intentionally ambiguous formulations;
- single-concept queries;
- two-concept compositions;
- three-or-more-concept compositions;
- counts;
- ratios;
- player rankings.

Examples include:

```text
How many clutch possessions occurred in the game?

How many possessions while trailing resulted in points?

What proportion of one-possession-game possessions resulted in points?

How many late-game possessions while trailing resulted in a made three-pointer?

Who was the most clutch player?
```

The benchmark intentionally retains some ambiguous natural-language formulations. This makes it possible to study semantic interpretation failures rather than constructing a benchmark designed to achieve perfect accuracy.

---

## Evaluation

Each benchmark question is evaluated at several levels.

### Semantic correctness

Tests whether the LLM generated the expected structured ontology query.

This includes:

```text
concepts
operation
denominator concepts
entity
metric
order
limit
```

### Ontology correctness

Tests whether execution against the inferred RDF graph produces the same result as an independent ground-truth implementation.

### End-to-end correctness

Tests the complete pipeline:

```text
Natural language
      ↓
LLM interpretation
      ↓
Ontology concepts
      ↓
Query execution
      ↓
Answer
```

This separation makes it possible to distinguish errors caused by:

- natural-language interpretation;
- ontology/query execution;
- data reconstruction;
- ambiguous formulations.

---

# Installation

## 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd sloan_2027_viziball_llm_ontology
```

## 2. Create a Python environment

Using `venv`:

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

The benchmark requires access to the basketball source database used to reconstruct games and possessions.

Database credentials must **not** be stored in the source code.

Create a local file named:

```text
.env
```

at the root of the repository.

Example:

```env
NEO4J_URI=neo4j+s://your-instance.neo4j.io
NEO4J_USER=your_readonly_user
NEO4J_PASSWORD=your_password
```

The application loads these variables with `python-dotenv`.

The corresponding Python configuration is:

```python
import os

from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
```

## Database permissions

For reproducibility and security, the benchmark should use a **read-only Neo4j account**.

The benchmark does not require write access to the source basketball database.

A Neo4j administrator can configure a dedicated role, for example:

```cypher
CREATE ROLE sloan_reader_role;
```

Grant access to the basketball database:

```cypher
GRANT ACCESS ON DATABASE BCL
TO sloan_reader_role;
```

Grant graph read permissions:

```cypher
GRANT MATCH {*}
ON GRAPH BCL
TO sloan_reader_role;
```

Then assign the role to the benchmark user:

```cypher
GRANT ROLE sloan_reader_role
TO sloan_reader;
```

The exact administration syntax may depend on the Neo4j version and edition.

---

## Security

Never commit `.env` to Git.

The repository's `.gitignore` should contain:

```gitignore
.env
__pycache__/
*.pyc
```

An optional `.env.example` can be committed instead:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_readonly_user
NEO4J_PASSWORD=your_password
```

---

# Running the Benchmark

From the repository root:

```bash
python main.py
```

For a syntax check before a long benchmark run:

```bash
python -m py_compile main.py
python -m py_compile ontology_benchmark.py
```

The program processes games sequentially.

For each game, the pipeline:

```text
1. Loads the game data
2. Reconstructs play-by-play actions
3. Reconstructs possessions
4. Builds the factual RDF graph
5. Adds the basketball ontology
6. Performs semantic inference
7. Executes the 100-question benchmark
8. Saves each result immediately
9. Clears the in-memory RDF graph
10. Continues with the next game
```

Processing games independently limits memory usage and makes long benchmark runs easier to recover.

---

# Checkpointing and Crash Recovery

Benchmark results are persisted **after each question**.

This is intentional: a long multi-game experiment should not lose completed results if execution is interrupted.

Two output formats are generated:

```text
benchmark_results/
├── ontology_benchmark_results.csv
└── ontology_benchmark_results.jsonl
```

The JSONL output acts as the primary checkpoint format.

When execution resumes, already completed `(game_id, question_id)` instances can be detected and skipped.

This makes the benchmark suitable for long-running experiments across an entire season.

---

# Results

## CSV

The main analysis-friendly output is:

```text
benchmark_results/ontology_benchmark_results.csv
```

Each row corresponds to one:

```text
(game, question)
```

benchmark instance.

With 100 questions and `N` games, a complete experiment therefore contains:

```text
100 × N
```

rows.

The CSV is intended for:

- statistical analysis;
- error analysis;
- aggregation by question type;
- generation of tables;
- generation of figures.

---

## JSONL

The checkpoint/raw experimental output is:

```text
benchmark_results/ontology_benchmark_results.jsonl
```

Each line contains one complete benchmark result represented as JSON.

JSONL preserves structured fields such as concept lists and query representations more naturally than CSV and is therefore useful for detailed post-hoc analysis and reproducibility.

---

# Result Dimensions

The benchmark records information required to analyze performance beyond a single accuracy score.

Depending on the benchmark item, stored metadata includes dimensions such as:

```text
game_id
question_id
question

query_type
linguistic_type
difficulty
concept_count

expected_operation
expected_concepts
expected_denominator

actual_operation
actual_concepts
actual_denominator

ground_truth_answer
ontology_answer
llm_answer

semantic_correct
ontology_correct
end_to_end_correct

error_stage
error_type
error_message
```

This enables results to be grouped by semantic and linguistic complexity.

For example:

```text
Single concept
Composition of 2 concepts
Composition of 3+ concepts

Direct formulation
Paraphrase
Implicit formulation
Ambiguous formulation

COUNT
RATIO
RANK
```

---

# Error Analysis

A central goal of the benchmark is not only to measure accuracy but also to identify **where errors occur**.

For example, a question may select the correct ontology concepts while selecting the wrong analytical operation:

```text
Expected:
COUNT

Predicted:
RATIO
```

Such a case is classified as a semantic interpretation failure rather than an ontology execution failure.

Conversely, if the structured semantic query is correct but its result differs from independently computed ground truth, the failure occurs at the ontology/data execution level.

This distinction is important when evaluating LLM-based analytical systems: a plausible natural-language interpretation is not sufficient to guarantee an analytically correct answer.

---

# Repository Structure

The core experimental code is organized approximately as follows:

```text
sloan_2027_viziball_llm_ontology/
│
├── main.py
│
├── rdf_builder.py
│
├── ontology_benchmark.py
│
├── ontology_ground_truth.py
│
├── ontology_parser.py
│
├── ontology_query.py
│
├── requirements.txt
│
├── README.md
│
├── .env.example
│
├── .gitignore
│
├── ontology/
│   ├── viziball_ontology.py
│   └── llm_schema.txt
│
└── benchmark_results/
    ├── ontology_benchmark_results.csv
    └── ontology_benchmark_results.jsonl
```

---

# Reproducing the Experiment

To reproduce the experiment:

```text
1. Clone the repository
2. Install Python dependencies
3. Configure read-only Neo4j credentials
4. Configure the games used by the benchmark
5. Run `python main.py`
6. Wait for all game/question pairs to complete
7. Analyze `benchmark_results/ontology_benchmark_results.csv`
```

A clean run should start with an empty result directory if the goal is to reproduce the complete experiment from scratch.

Existing JSONL results may cause completed instances to be skipped by the checkpoint/recovery mechanism.

---

# Research Motivation

Traditional sports analytics systems frequently expose either predefined statistics or require analysts to explicitly formulate database queries.

Large Language Models provide a natural-language interface but introduce another problem: generated analytical queries can be syntactically valid and semantically plausible while still representing the wrong analytical question.

This project explores a different architecture.

The LLM does not directly construct the final database query. Instead, it operates over a constrained semantic layer defined by a basketball ontology.

The hypothesis is that a possession-based ontology can provide enough structure to support complex and contextual basketball questions while keeping analytical execution deterministic and inspectable.

The benchmark is designed to evaluate that hypothesis empirically.

---

# Research

This repository supports the research paper:

> **From Play-by-Play to Semantic Analytics: A Possession-Based Basketball Ontology for LLM Question Answering**

The work focuses on basketball play-by-play data, possession reconstruction, knowledge graphs, semantic inference, ontology-guided LLM question answering, and systematic evaluation of semantic and analytical correctness.

Future extensions include richer high-level basketball concepts, additional data sources beyond play-by-play, broader semantic reasoning capabilities, and application of the methodology to other sports.