# Knowledge Notes: Robust Dynamic Operating Envelopes (RDOE) for Unbalanced Distribution Networks

## 1. Corpus Scope and Rationale

This acquisition set targets robust dynamic operating envelope computation under uncertainty in unbalanced three-phase feeders, with emphasis on non-convex UTOPF fidelity, tractability, fairness-aware allocation, and market-coupled deployment.

Source families:
- Core RDOE/DOE methods and recent variants (KA01-KA17, KA35)
- Unbalanced OPF theory and scalable algorithms (KA18-KA31)
- Reproducible toolchains and benchmark resources (KA32-KA41)

Coverage statistics:
- Total sources: 41
- Primary papers/reports: 35
- 2023+ sources: 17

## 2. Formal Problem Template

Across core works (KA01, KA02, KA03, KA04, KA15), DOE/RDOE is represented as a feasible operating region under network constraints:

- Feasibility region (KA01, KA15):
  - \mathcal{R}_t = {u_t | \exists x_t: h(x_t,u_t)=0, g(x_t,u_t)\le0}
- Robust extension (KA01, KA03):
  - \mathcal{E}_t = {u_t | \exists x_t: g(x_t,u_t,\xi_t)\le0, \forall \xi_t\in\Xi_t}
- Stochastic extension (KA04):
  - \min \mathbb{E}_{\xi}[f(x,u,\xi)] with scenario constraints.

Interpretation:
- Deterministic envelopes (DOE) maximize flexibility conditional on point forecasts.
- Robust envelopes (RDOE) sacrifice some utilization to preserve security under bounded uncertainty.
- Stochastic envelopes tune risk via scenario or probability constraints.

## 3. Non-Convex Fidelity vs Linearized Scalability

### 3.1 Non-convex UTOPF fidelity path

KA01 argues linearized methods can overestimate feasible capacity and risk violating physical limits. Non-convex AC constraints are retained, with sensitivity filtering to reduce dimension and solve burden.

Why this matters:
- For high-PV and unbalanced conditions, approximation error near voltage/current limits is operationally significant.
- Envelope policy failures are high-cost because they manifest as security violations, not just suboptimality.

### 3.2 Linearized robust path

KA02 and parts of KA05 use linearized sensitivity mapping:
- \Delta v \approx J_v \Delta p + K_v \Delta q
with robustified linear inequality forms.

Tradeoff observed across sources:
- Benefits: computationally fast, easy to embed in frequent updates.
- Risk: model mismatch under stressed or nonlinear operating regimes.

### 3.3 Hybrid insight

Cross-reading KA01/KA02/KA05 suggests practical architecture:
- Use fast linear methods for screening or warm-start.
- Use non-convex verification/refinement near active constraints or critical feeders.

## 4. Unbalanced OPF Theoretical Backbone

Key foundations supporting DOE computation:
- Branch-flow equations (KA26, KA27):
  - P/Q flow balances, voltage drop equation, and current-power relation.
- Convex exactness conditions in radial systems (KA28, KA29, KA30).
- Three-phase and delta-connection exactness extensions (KA18, KA31).
- Approximation/relaxation and online control methods (KA19, KA20, KA21, KA22).

Cross-paper consensus:
- Convex relaxations can be highly effective but exactness is conditional.
- Unbalanced and connection-rich feeders require careful model selection.
- Online and hierarchical algorithms are required for operational timescales.

## 5. Fairness and Allocation Mechanisms

Core fairness/allocation works: KA08, KA10, KA16, KA17.

Representative fairness formalism:
- \alpha-fair utility (KA08):
  - U(u)=\sum_i w_i u_i^{1-\alpha}/(1-\alpha)
- Bargaining objective (KA10/KA17):
  - \max \prod_i (u_i-u_i^0)

Key synthesis:
- Technical maximal envelopes can be inequitable among prosumers.
- Fairness definition materially affects curtailment/benefit distribution.
- Bargaining and welfare formulations can improve acceptance but require policy governance and transparent disagreement points.

## 6. Market-Coupled DOE Research

Studies KA09-KA14 connect envelopes to local markets, peer-to-peer trading, EV participation, and demand response.

Common structural pattern:
- Envelopes act as network-security constraints or admissible bid domains.
- Market objectives maximize welfare/trading utility under envelope bounds.

Converging claim:
- DOE is a practical interface between DSO security and decentralized market flexibility.

Open methodological issue:
- Many studies still rely on stylized behavior models; real participation uncertainty and strategic behavior remain underexplored.

## 7. Reproducibility and Implementation Resources

Mandatory seed analysis:
- KA36 cloned to knowledge/repos/pandapower.
- Inspected files: README.rst, LICENSE (BSD-3-Clause), pyproject.toml, CITATION.bib.
- Reproducibility signals:
  - Explicit dependency sets and optional extras.
  - Test configuration and strict markers.
  - Project metadata and documentation links.

Complementary code/data stack:
- KA37 PowerModels.jl
- KA38 PowerModelsDistribution.jl
- KA39 MATPOWER
- KA40 OpenDSSDirect.py
- KA41 SimBench

Practical recommendation for downstream experimentation:
- Use pandapower + SimBench as baseline environment.
- Add PowerModelsDistribution or OpenDSS-based validation for cross-solver robustness checks.

## 8. Similarities and Differences Across Papers

Similarities:
- Nearly all DOE methods enforce voltage/current/thermal constraints via OPF-like feasibility checks.
- Uncertainty handling appears as robust sets, stochastic scenarios, or implicit data-driven margins.
- Fairness has shifted from secondary to central objective in recent publications.

Differences:
- Model fidelity: non-convex AC vs linearized/approximate models.
- Optimization architecture: centralized, hierarchical, distributed, market-coupled.
- Validation context: synthetic benchmark feeders vs pilot-like scenarios.

Most consequential methodological fork:
- Whether to trust linearized envelopes operationally, or use non-convex methods with acceleration/sensitivity filtering.

## 9. Coverage Boundaries and Next-Phase Needs

Gaps identified:
- Limited open full-text access for some newest publisher articles restricts deep equation extraction.
- Sparse multi-year field deployment evidence.
- Regulatory performance criteria are less standardized than algorithmic metrics.

Downstream implications:
- In knowledge_distillation, normalize evaluation dimensions:
  - security violation rate,
  - envelope utilization/flexibility delivered,
  - solve time and update cadence,
  - fairness distribution metrics,
  - robustness against forecast/model error.

Linked source IDs for distillation seed:
- Core method candidates: KA01, KA02, KA03, KA04, KA05
- Fairness candidates: KA08, KA10, KA16
- Market-integration candidates: KA09, KA11, KA12, KA13, KA14
- Theory support: KA18, KA19, KA26, KA28, KA30, KA31
- Reproducibility stack: KA36-KA41
