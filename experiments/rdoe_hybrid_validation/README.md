# RDOE Hybrid Validation Simulation

## Goal
Implement and execute the `experiment_design` matrix (`EXP-H1..EXP-H4`) for hybrid proof+empirical validation of robust dynamic operating envelopes.

## Layout
- `src/rdoe_validation/core.py`: synthetic but hypothesis-aligned experiment generator.
- `src/rdoe_validation/analysis.py`: metric aggregation, acceptance checks, confirmatory analyses.
- `src/rdoe_validation/plotting.py`: seaborn-styled multi-panel PDF figure generation.
- `src/rdoe_validation/sympy_checks.py`: symbolic validations aligned with `phase_outputs/SYMPY.md`.
- `run_experiments.py`: CLI entrypoint.
- `configs/experiment_config.json`: experiment plan configuration.
- `tests/test_metrics.py`: reproducibility and acceptance-map tests.

## Reproducible Commands
From workspace root:

```bash
experiments/.venv/bin/python experiments/rdoe_hybrid_validation/run_experiments.py \
  --config experiments/rdoe_hybrid_validation/configs/experiment_config.json \
  --output-dir experiments/rdoe_hybrid_validation \
  --figures-dir paper/figures \
  --tables-dir paper/tables \
  --data-dir paper/data \
  --log-path experiments/experiment_log.jsonl \
  --sympy-report-path experiments/rdoe_hybrid_validation/sympy/sympy_validation_report.txt \
  --results-summary-path experiments/rdoe_hybrid_validation/results_summary.json
```

## Notes
- Figures are written as PDF vector graphics for LaTeX compatibility.
- A PDF readability check is performed by rasterizing first pages via `pypdfium2`.
- Experiment logs are appended to `experiments/experiment_log.jsonl`.
