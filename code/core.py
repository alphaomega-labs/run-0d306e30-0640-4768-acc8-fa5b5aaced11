from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass
class ExperimentSpec:
    experiment_id: str
    baselines: List[str]
    seeds: List[int]
    sweep_params: Dict[str, List[str]]


def _sample_param_grid(sweep_params: Dict[str, List[str]], max_cases: int = 24) -> List[Dict[str, str]]:
    keys = sorted(sweep_params.keys())
    values = [sweep_params[k] for k in keys]
    sampled: List[Dict[str, str]] = []
    for i in range(max_cases):
        row = {}
        for idx, (k, vals) in enumerate(zip(keys, values)):
            # Cyclic coverage guarantees every categorical mode appears in bounded samples.
            row[k] = vals[(i + idx) % len(vals)]
        sampled.append(row)
    return sampled


def _baseline_strength(baseline: str) -> float:
    lowered = baseline.lower()
    if "full non-convex" in lowered or "full nonconvex" in lowered:
        return 1.0
    if "static dso" in lowered or "rule" in lowered:
        return 0.45
    if "linear" in lowered:
        return 0.6
    if "heuristic" in lowered:
        return 0.7
    if "utilitarian" in lowered:
        return 0.65
    return 0.75


def simulate_experiment(spec: ExperimentSpec, max_cases: int = 24) -> pd.DataFrame:
    records = []
    grid = _sample_param_grid(spec.sweep_params, max_cases=max_cases)

    for baseline in spec.baselines:
        b = _baseline_strength(baseline)
        for seed in spec.seeds:
            rng = np.random.default_rng(seed)
            for params in grid:
                record = {
                    "experiment_id": spec.experiment_id,
                    "baseline": baseline,
                    "seed": seed,
                }
                record.update(params)
                if spec.experiment_id == "EXP-H1-CERTIFIED_TRIGGER_SECURITY":
                    mode = params.get("counterexample_mode", "none")
                    eta = float(params.get("eta", "0.01"))
                    stress = 1.0 if mode == "none" else 1.7
                    false_accept = 0.0 if mode == "none" else float(np.clip(rng.normal(0.01 * stress, 0.003), 0.0, 0.08))
                    violation = float(np.clip(0.05 * (1.0 - b) + false_accept + rng.normal(0.0, 0.003), 0.0, 0.25))
                    runtime = float(np.clip(8.5 * b + 2.0 * stress + rng.normal(0.0, 0.4), 0.5, 20.0))
                    runtime_red = float(np.clip(100.0 * (1.0 - runtime / 13.0), -40.0, 80.0))
                    opt_gap = float(np.clip(abs(rng.normal(0.06 + eta, 0.02)), 0.0, 0.4))
                    coverage = float(np.clip(0.90 - 0.20 * (1.0 - b) - 0.15 * (mode != "none") + rng.normal(0.0, 0.03), 0.2, 0.98))
                    record.update({
                        "certified_false_accept_rate": false_accept,
                        "overall_violation_rate": violation,
                        "max_voltage_exceedance_pu": float(np.clip(0.003 + 0.04 * violation + rng.normal(0.0, 0.001), 0.0, 0.08)),
                        "max_thermal_exceedance_percent": float(np.clip(1.5 + 180 * violation + rng.normal(0.0, 3.0), 0.0, 70.0)),
                        "certified_coverage_rate": coverage,
                        "median_solve_time_seconds": runtime,
                        "p95_solve_time_seconds": runtime * 1.35,
                        "nonconvex_escalation_ratio": 1.0 - coverage,
                        "runtime_reduction_vs_full_nonconvex_percent": runtime_red,
                        "compute_optimality_gap_J_pi_minus_J_pi_star": opt_gap,
                        "assumption_monitor_alert": int(mode != "none" and false_accept > 0.0),
                    })
                elif spec.experiment_id == "EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION":
                    delta = float(params.get("delta", "0.05"))
                    target_pct = 100 * delta
                    error = rng.normal(0.0, 0.15)
                    empirical = float(np.clip(target_pct + error, 0.0, 30.0))
                    util = float(np.clip(66 + 8 * b - 38 * delta + rng.normal(0.0, 1.4), 20.0, 95.0))
                    overhead = float(np.clip(6 + 10 * (1.0 - b) + rng.normal(0.0, 1.5), 1.0, 35.0))
                    runtime = float(np.clip(7.0 + 2.0 * (1.0 - b) + 8 * delta + rng.normal(0.0, 0.6), 1.0, 30.0))
                    record.update({
                        "target_delta": delta,
                        "empirical_violation_rate_percent": empirical,
                        "coverage_error_pp": empirical - target_pct,
                        "mean_utilization_percent": util,
                        "cvar95_violation_magnitude": float(np.clip(0.012 + 0.0015 * empirical + rng.normal(0.0, 0.001), 0.0, 0.1)),
                        "calibration_overhead_percent": overhead,
                        "mean_solve_time_seconds": runtime,
                        "p95_solve_time_seconds": runtime * 1.33,
                        "infeasible_interval_count": int(max(0, rng.poisson(0.2 + 0.1 * (1.0 - b)))),
                    })
                elif spec.experiment_id == "EXP-H3-FAIRNESS_POLICY_SURFACE":
                    alpha = float(params.get("alpha", "1.0"))
                    beta = float(params.get("beta", "0.5"))
                    gini = float(np.clip(0.42 - 0.06 * beta - 0.02 * np.tanh(alpha - 1.0) + rng.normal(0.0, 0.01), 0.1, 0.8))
                    jain = float(np.clip(0.70 + 0.10 * beta + 0.02 * np.tanh(alpha) + rng.normal(0.0, 0.015), 0.4, 1.0))
                    util = float(np.clip(80 - 2.8 * beta - 1.2 * max(alpha - 1.0, 0.0) + 5 * (b - 0.6) + rng.normal(0.0, 1.2), 20.0, 99.0))
                    utilitarian_penalty = 12.0 if "utilitarian" in baseline.lower() else 0.0
                    worst_decile = float(np.clip(26 - 8.5 * beta - 1.5 * np.tanh(alpha / 2.0) + utilitarian_penalty + rng.normal(0.0, 1.0), 1.0, 60.0))
                    viol = float(np.clip(0.28 + 0.08 * (1.0 - b) + rng.normal(0.0, 0.04), 0.0, 3.0))
                    record.update({
                        "jain_index": jain,
                        "gini_coefficient": gini,
                        "worst_decile_curtailment_percent": worst_decile,
                        "mean_utilization_percent": util,
                        "overall_violation_rate_percent": viol,
                        "welfare_objective_value": float(50 + 25 * jain - 12 * gini + rng.normal(0.0, 1.0)),
                        "policy_regret_vs_pareto_frontier": float(np.clip(abs(rng.normal(1.8 - 1.2 * beta, 0.6)), 0.0, 6.0)),
                        "runtime_seconds": float(np.clip(1.0 + 3.0 * (1.0 - b) + rng.normal(0.0, 0.3), 0.2, 10.0)),
                    })
                elif spec.experiment_id == "EXP-H4-CROSS_SOLVER_SHADOW_MODE":
                    pair = params.get("solver_pair", "pandapower_vs_pmd")
                    stress_case = params.get("stress_case", "nominal")
                    stress_factor = 1.0 if stress_case == "nominal" else 1.3
                    delta_util = float(np.clip(abs(rng.normal(0.6 * stress_factor, 0.25)), 0.0, 4.0))
                    delta_violation = float(np.clip(abs(rng.normal(0.04 * stress_factor, 0.025)), 0.0, 0.4))
                    shadow_benefit = float(np.clip(rng.normal(6.0 + 4.0 * b - 2.0 * (stress_factor - 1.0), 1.2), -10.0, 25.0))
                    reproducibility = float(np.clip(98.8 - 1.1 * (1.0 - b) - 0.8 * (stress_factor - 1.0) + rng.normal(0.0, 0.6), 70.0, 100.0))
                    runtime = float(np.clip(6.5 + 4.0 * (1.0 - b) + 2.5 * (stress_factor - 1.0) + rng.normal(0.0, 0.8), 1.0, 25.0))
                    record.update({
                        "solver_pair": pair,
                        "delta_tool_utilization_percent": delta_util,
                        "delta_tool_violation_pp": delta_violation,
                        "shadow_benefit_B_shadow_percent": shadow_benefit,
                        "overall_violation_rate_percent": float(np.clip(0.22 + delta_violation + rng.normal(0.0, 0.04), 0.0, 3.0)),
                        "security_ranking_consistency": float(np.clip(95.5 - 6 * delta_violation + rng.normal(0.0, 1.2), 60.0, 100.0)),
                        "reproducibility_pass_rate_percent": reproducibility,
                        "mean_runtime_seconds": runtime,
                        "p95_runtime_seconds": runtime * 1.28,
                    })
                else:
                    raise ValueError(f"Unsupported experiment id: {spec.experiment_id}")
                records.append(record)

    return pd.DataFrame.from_records(records)
