# Simulation Pipeline & Experiment Protocol

---

## Part 1: Simulation Pipeline

> 文件路径：`docs/simulation_pipeline.md`

This document defines the full simulation pipeline in Stage-2.

### Overview

The pipeline transforms circuit design parameters into structured simulation records:

```
design → netlist → simulation → metrics → record → dataset
```

Each stage is explicitly modularized to ensure reproducibility and extensibility.

---

### Pipeline Steps

#### 1. Design Sampling

- **Input:** design space (`configs/circuit/opamp.yaml`)
- **Output:** parameter vectors

```bash
py -3.12 -m scripts.generate_initial_designs
```

#### 2. Netlist Generation

- Convert parameters into Spectre/SPICE netlist
- Ensures deterministic mapping

**Module:** `src/circuits/netlist_writer.py`

#### 3. Simulation Execution

Two modes:

| Mode | Description |
|------|-------------|
| **Mock Mode** | Fast synthetic simulation — used for pipeline validation |
| **Real Mode** | Calls Spectre — requires template + extraction script |

Switch via config:

```yaml
simulation:
  use_mock: true   # or false for real mode
```

#### 4. Metrics Extraction

- Extract: `gain`, `GBW`, `PM`, `power`
- Prefer text-based metrics output (`metrics.txt`)

#### 5. Failure Detection

Failure types:

- `simulation_error`
- `metrics_missing`
- `simulation_flagged_failure`

**Module:** `src/simulation/failure_checker.py`

#### 6. Record Construction

Each run produces a structured record:

```json
{
  "design": { "...": "..." },
  "metrics": { "...": "..." },
  "simulation_failed": false,
  "failure_reasons": [],
  "is_feasible": true,
  "violations": { "...": "..." },
  "margins": { "...": "..." }
}
```

#### 7. Dataset Export

```bash
py -3.12 -m scripts.parse_raw_results
```

Outputs:

- **CSV** — flat format
- **JSON** — structured format

---

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| Deterministic pipeline | Same inputs always produce same outputs |
| Structured failure semantics | All failures are typed and traceable |
| Config-driven execution | Behavior controlled via YAML configs |
| Mock/Real unified interface | Same code path for both modes |

### Stage-2 Objective

> Transform circuit optimization into a **programmable data generation system**.
> NOT to optimize performance yet.

---

## Part 2: Experiment Protocol

> 文件路径：`docs/experiment_protocol.md`

---

### Execution Rules

All scripts **MUST** be executed using:

```bash
py -3.12 -m scripts.<script_name>
```

---

### Standard Workflow

#### Step 1: Generate Designs

```bash
py -3.12 -m scripts.generate_initial_designs
```

#### Step 2: Run Simulations

```bash
py -3.12 -m scripts.run_batch_simulations
```

#### Step 3: Parse Results

```bash
py -3.12 -m scripts.parse_raw_results
```

#### Step 4: Analyze Results

```bash
py -3.12 -m scripts.analyze_results
```

---

### Data Requirements

Each dataset **MUST** contain:

- Design parameters
- Performance metrics
- Constraint margins
- Simulation status
- Failure reasons

---

### Stage-2 Exit Criteria

Stage-2 is considered **complete** if all of the following are met:

1. Pipeline runs end-to-end without manual intervention
2. Mock mode produces a stable dataset
3. Real mode validated on at least 1–2 samples
4. Failure categories are explicitly defined
5. Data integrity checks pass
6. Summary statistics can be generated

---

### Notes

- Stage-2 focuses on **system reliability**, not optimization performance
- All future stages depend on this pipeline being stable and reproducible