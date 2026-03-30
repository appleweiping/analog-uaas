# UAAS: Uncertainty-Aware Adaptive Sampling for Surrogate-Assisted Analog Circuit Optimization

> **Surrogate models break at decision boundaries. We quantify where, and act accordingly.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PyTorch%20%7C%20GPyTorch-orange.svg)]()
[![Simulator](https://img.shields.io/badge/Simulator-SPICE%20Compatible-green.svg)]()

---

## Problem Statement

Analog circuit optimization under performance constraints requires repeated SPICE-level simulation to evaluate candidate designs. While surrogate models (e.g., Gaussian Processes, neural networks) can approximate circuit performance and reduce simulation overhead, their deployment in high-stakes optimization pipelines introduces a class of **reliability failures** that are distinct from prediction accuracy.

Specifically, the **feasibility boundary**—the region separating constraint-satisfying from constraint-violating designs—constitutes a structurally ambiguous zone where surrogate confidence collapses and classification error rates are highest. Optimization algorithms operating over these surrogates are systematically drawn toward this boundary during convergence, precisely where model reliability is lowest.

This work addresses the following core problem:

> *How can a surrogate-assisted optimization loop maintain constraint-feasibility guarantees and convergence stability when the surrogate's predictive reliability degrades near the feasibility boundary—without resorting to exhaustive simulation?*

This is a **reliability problem**, not an accuracy problem. A surrogate with 98% global accuracy may still induce catastrophic misclassification along a 2% boundary slice that dominates the feasibility decision.

---

## Failure Mode Analysis

The central failure mode motivating UAAS is **boundary-induced misclassification** under surrogate-guided optimization.

### Formal Characterization

Let $\mathcal{F} \subset \mathbb{R}^d$ denote the feasible region defined by $K$ performance constraints $g_k(\mathbf{x}) \leq 0$, and let $\hat{g}_k$ be the surrogate approximation. The **predicted feasibility boundary** $\hat{\partial}\mathcal{F}$ is defined as $\{\mathbf{x} : \hat{g}_k(\mathbf{x}) = 0\}$ for some $k$.

Near $\hat{\partial}\mathcal{F}$, the surrogate exhibits:

1. **Epistemic uncertainty inflation**: Sparse training data in boundary regions yields high posterior variance in GP surrogates, causing unreliable constraint classification.
2. **Classification boundary misalignment**: The true boundary $\partial\mathcal{F}$ and predicted boundary $\hat{\partial}\mathcal{F}$ diverge under insufficient local sampling density, leading to **feasibility errors**—infeasible designs classified as feasible, or valid solutions discarded.
3. **Optimization attractor effect**: Gradient-based and evolutionary optimizers converge toward regions of surrogate optimality that are disproportionately co-located with constraint boundaries, amplifying the above failure modes during exploitation phases.

### Consequence

Uncorrected, this failure mode results in: (a) acceptance of infeasible solutions, (b) premature termination in local infeasible traps, and (c) irreproducible optimization trajectories dependent on surrogate initialization.

---

## Method Overview

UAAS constructs a **closed-loop, simulation-scheduling system** that tightly couples surrogate inference, uncertainty quantification, and adaptive simulation dispatch. The system operates on the principle that simulation budgets should be allocated not uniformly, but **proportionally to the decision risk induced by surrogate uncertainty**.

The architecture comprises four interdependent modules:

| Module | Role |
|---|---|
| **Surrogate Engine** | GP-based performance modeling with posterior uncertainty |
| **Uncertainty Quantifier** | Boundary proximity scoring and predictive confidence estimation |
| **Decision Policy** | Simulation vs. surrogate routing under risk-calibrated thresholds |
| **Adaptive Sampler** | Active learning over boundary-adjacent regions |

The system operates as a closed loop: surrogate predictions inform candidate selection, uncertainty scores gate simulation dispatch, and simulation outcomes update the surrogate posterior—iteratively refining boundary resolution without a fixed simulation schedule.

---

## Key Contributions

1. **Boundary-Aware Reliability Framework.** We formalize the notion of *surrogate-induced feasibility error* and establish its dependence on local epistemic uncertainty, providing a principled basis for simulation triggering near constraint boundaries.

2. **Uncertainty-Gated Simulation Scheduling.** We propose a decision policy that conditions SPICE simulation dispatch on a composite uncertainty signal combining predictive variance and boundary proximity distance, achieving significant simulation reduction without feasibility loss.

3. **Closed-Loop Adaptive Sampling.** UAAS integrates an active learning component that preferentially augments surrogate training data in boundary-adjacent regions, correcting epistemic uncertainty inflation through targeted informativeness-guided sampling.

4. **Empirical Reliability Characterization.** We provide systematic evaluation of feasibility error rates, boundary resolution quality, and optimization convergence stability across representative analog circuit benchmarks, demonstrating that reliability—not accuracy—is the operative metric for surrogate deployment in constrained optimization.

---

## Framework Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     UAAS Closed-Loop System                     │
│                                                                 │
│  Initial DoE ──► Surrogate Fit ──► Uncertainty Quantification   │
│       ▲                                    │                    │
│       │                                    ▼                    │
│  SPICE Update ◄── Simulation Gate ◄── Decision Policy           │
│       │                │                                        │
│       │          [High Risk]  [Low Risk]                        │
│       │               │           │                             │
│       └── Retrain ◄───┘    Surrogate Eval ──► Optimizer         │
│                                                    │            │
│                          Adaptive Sampler ◄────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

**Step 1 — Initialization.** Design of Experiments (DoE) via Latin Hypercube Sampling generates an initial dataset $\mathcal{D}_0 = \{(\mathbf{x}_i, \mathbf{y}_i)\}_{i=1}^{N_0}$ from SPICE simulation.

**Step 2 — Surrogate Construction.** Independent GP surrogates $\{\hat{g}_k\}_{k=1}^K$ are fitted per performance metric, providing both predictive mean $\mu_k(\mathbf{x})$ and posterior variance $\sigma_k^2(\mathbf{x})$.

**Step 3 — Uncertainty Quantification.** For each candidate $\mathbf{x}$, a composite risk score $\rho(\mathbf{x})$ is computed as a function of $\sigma_k^2(\mathbf{x})$ and signed boundary distance $\delta_k(\mathbf{x}) = \mu_k(\mathbf{x}) / \sigma_k(\mathbf{x})$, calibrated to identify boundary-proximal, high-uncertainty regions.

**Step 4 — Decision Policy.** A threshold policy routes candidates to SPICE simulation when $\rho(\mathbf{x}) > \tau$ (adaptive or fixed), and to surrogate evaluation otherwise. This gate enforces reliability-constrained optimization without exhaustive simulation.

**Step 5 — Adaptive Boundary Sampling.** A targeted acquisition function selects informative boundary-adjacent samples for surrogate augmentation, reducing epistemic uncertainty in the most decision-critical regions.

**Step 6 — Surrogate Update and Re-optimization.** Simulation results incrementally update the surrogate posterior. The optimizer re-evaluates candidates over the refined landscape. The loop continues until a simulation budget $N_{\max}$ or convergence criterion is met.

---

## Repository Structure

```
UAAS/
├── core/
│   ├── surrogate/
│   │   ├── gp_model.py            # GP surrogate with uncertainty outputs
│   │   ├── ensemble.py            # Multi-model ensembling for epistemic estimation
│   │   └── calibration.py         # Posterior calibration utilities
│   ├── uncertainty/
│   │   ├── quantifier.py          # Composite risk score computation
│   │   ├── boundary_distance.py   # Signed constraint boundary proximity
│   │   └── acquisition.py         # Active learning acquisition functions
│   ├── decision/
│   │   ├── policy.py              # Simulation dispatch policy (threshold-based)
│   │   ├── scheduler.py           # Budget-aware simulation scheduling
│   │   └── adaptive_threshold.py  # Dynamic threshold adjustment
│   └── optimizer/
│       ├── bo_loop.py             # Bayesian optimization integration
│       └── cmaes_interface.py     # CMA-ES optimizer adapter
├── simulation/
│   ├── spice_wrapper.py           # SPICE simulator interface (ngspice/HSPICE)
│   ├── netlist_generator.py       # Parametric netlist construction
│   └── result_parser.py          # Simulation output parsing
├── benchmarks/
│   ├── circuits/                  # Benchmark circuit netlists
│   │   ├── two_stage_opamp/
│   │   ├── lna/
│   │   └── vco/
│   └── specs/                     # Performance specification files
├── experiments/
│   ├── configs/                   # Experiment configuration (YAML)
│   ├── run_experiment.py          # Unified experiment runner
│   └── ablation/                  # Ablation study scripts
├── evaluation/
│   ├── metrics.py                 # Reliability and optimization metrics
│   ├── feasibility_error.py       # Boundary misclassification analysis
│   └── convergence.py             # Optimization convergence utilities
├── baselines/
│   ├── pure_bo.py                 # Standard BO without uncertainty gating
│   ├── random_sampling.py         # Monte Carlo baseline
│   ├── vanilla_surrogate.py       # Surrogate-only (no simulation scheduling)
│   └── safe_bo.py                 # SafeOpt-style constraint handling
├── notebooks/
│   ├── failure_mode_analysis.ipynb
│   ├── boundary_visualization.ipynb
│   └── results_reproduction.ipynb
├── configs/
│   └── default.yaml
├── requirements.txt
└── README.md
```

---

## Experiment Setup

Experiments are conducted on three representative analog circuit benchmarks of increasing complexity:

| Circuit | Parameters | Constraints | Technology |
|---|---|---|---|
| Two-Stage Op-Amp | 6 | 5 (gain, BW, PM, CMRR, power) | 180nm CMOS |
| Low-Noise Amplifier (LNA) | 8 | 6 (NF, S11, gain, IIP3, BW, power) | 65nm CMOS |
| Voltage-Controlled Oscillator (VCO) | 7 | 5 (freq range, PN, power, tuning, FoM) | 65nm CMOS |

**Simulation backend:** ngspice (open-source) and HSPICE (proprietary); abstracted through a unified `spice_wrapper` interface.

**Surrogate:** Single-output GP per performance metric (RBF + Matérn kernels evaluated); hyperparameters optimized via marginal likelihood maximization.

**Optimization budget:** $N_{\max} \in \{50, 100, 200\}$ total SPICE calls per run; averaged over 20 independent random seeds.

**Computational environment:** All surrogate operations and optimization loops run on CPU (Intel Xeon); SPICE simulations are parallelized across available cores via the scheduler module.

---

## Evaluation Metrics

UAAS is evaluated on **reliability-centric** metrics rather than surrogate prediction accuracy alone:

| Metric | Definition | Significance |
|---|---|---|
| **Feasibility Error Rate (FER)** | Fraction of top-$k$ returned solutions that are SPICE-infeasible | Primary reliability metric; quantifies boundary misclassification consequence |
| **Simulation Reduction Ratio (SRR)** | $1 - N_{\text{sim}} / N_{\text{total\_eval}}$ | Efficiency of the decision gate |
| **Boundary Resolution Quality (BRQ)** | IoU between predicted and true feasibility boundary (sampled) | Structural correctness of boundary localization |
| **Convergence Stability (CS)** | Variance of best feasible objective across seeds at fixed budget | Reliability of optimization trajectory |
| **Pareto Hypervolume (HV)** | Standard multi-objective volume indicator (for multi-spec circuits) | Solution quality in constraint-satisfying region |

> **Note:** Global RMSE of the surrogate is intentionally excluded as a primary metric. A low-RMSE surrogate may still induce high FER if prediction error concentrates along the feasibility boundary.

---

## Baselines

UAAS is compared against the following established methods:

| Baseline | Description | Limitation Targeted |
|---|---|---|
| **Random Sampling + SPICE** | Pure Monte Carlo over design space | No surrogate acceleration |
| **Vanilla Surrogate BO** | Standard Bayesian Optimization without uncertainty gating | No simulation scheduling; full surrogate trust |
| **SafeOpt** | Conservative constraint-safe Bayesian optimization | Conservative to infeasibility; not designed for optimization throughput |
| **Expected Feasibility (EF)** | Acquisition weighting by constraint satisfaction probability | No explicit boundary-proximity risk scoring |
| **UAAS (no adaptive sampling)** | Ablation: uncertainty gating without boundary-targeted resampling | Validates contribution of adaptive sampling component |
| **UAAS (fixed threshold)** | Ablation: static $\tau$ vs. adaptive threshold policy | Validates contribution of dynamic threshold |

---

## Reproducibility

All experiments are fully reproducible via configuration files under `experiments/configs/`. Random seeds are fixed and logged per run.

```bash
# Install dependencies
pip install -r requirements.txt

# Run primary experiment (Two-Stage Op-Amp, budget=100)
python experiments/run_experiment.py --config configs/opamp_n100.yaml --seed 0

# Run full benchmark sweep (20 seeds, all circuits)
bash scripts/run_all_benchmarks.sh

# Reproduce ablation study
python experiments/ablation/run_ablation.py --circuit lna --ablation uncertainty_gate
```

Surrogate training data, simulation logs, and raw results for all reported experiments are archived under `experiments/results/` and indexed by circuit, seed, and method. Figures in the paper are generated via `notebooks/results_reproduction.ipynb`.

> For proprietary HSPICE users: replace `simulator: ngspice` with `simulator: hspice` and provide the binary path in `configs/default.yaml`. All other pipeline components are simulator-agnostic.

---

## Future Work

- **Heteroscedastic surrogate models** that explicitly capture input-dependent noise in SPICE outputs, particularly relevant for post-layout simulation with parasitic variance.
- **Multi-fidelity simulation scheduling** integrating fast (behavioral-level) and slow (SPICE-level) simulators under the same uncertainty-gated decision framework.
- **Transferable surrogate initialization** across topologically similar circuits via meta-learning, reducing cold-start simulation overhead on new design instances.
- **Formal reliability certificates**: connecting the uncertainty quantification framework to PAC-style bounds on feasibility error, providing optimization guarantees beyond empirical validation.

---

## Citation

If you use UAAS in your research, please cite:

```bibtex
@inproceedings{uaas2025,
  title     = {UAAS: Uncertainty-Aware Adaptive Sampling for Reliable Surrogate-Assisted Analog Circuit Optimization},
  author    = {[Authors]},
  booktitle = {Proceedings of the IEEE/ACM International Conference on Computer-Aided Design (ICCAD)},
  year      = {2025}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center"><i>Reliability is not a property of the surrogate. It is a property of the system.</i></p>