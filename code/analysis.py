from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def summarize_by_baseline(df: pd.DataFrame, metric_cols: List[str]) -> pd.DataFrame:
    grouped = df.groupby(["experiment_id", "baseline"], as_index=False)
    out = grouped[metric_cols].agg(["mean", "std", "count"]).reset_index()
    out.columns = ["_".join([c for c in col if c]).strip("_") for col in out.columns.to_flat_index()]
    for metric in metric_cols:
        if f"{metric}_std" in out:
            out[f"{metric}_se"] = out[f"{metric}_std"] / np.sqrt(out[f"{metric}_count"].clip(lower=1))
            out[f"{metric}_ci95"] = 1.96 * out[f"{metric}_se"]
    return out


def confirmatory_regime_check(df: pd.DataFrame, experiment_id: str) -> Dict[str, float]:
    sub = df[df["experiment_id"] == experiment_id].copy()
    if sub.empty:
        return {"n": 0}

    if experiment_id == "EXP-H1-CERTIFIED_TRIGGER_SECURITY":
        by_mode = sub.groupby("counterexample_mode")["overall_violation_rate"].mean().to_dict()
        return {
            "n": int(len(sub)),
            "nominal_violation_mean": float(by_mode.get("none", np.nan)),
            "stress_violation_mean": float(np.mean([v for k, v in by_mode.items() if k != "none"])) if len(by_mode) > 1 else np.nan,
        }

    if experiment_id == "EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION":
        by_delta = sub.groupby("target_delta")["coverage_error_pp"].mean().to_dict()
        max_abs = float(max(abs(v) for v in by_delta.values())) if by_delta else np.nan
        return {"n": int(len(sub)), "max_abs_coverage_error_pp": max_abs}

    if experiment_id == "EXP-H3-FAIRNESS_POLICY_SURFACE":
        nd_points = sub[["mean_utilization_percent", "gini_coefficient", "overall_violation_rate_percent"]].copy()
        # Simple dominance proxy: top decile by utilization and low gini/viol.
        score = nd_points["mean_utilization_percent"] - 25 * nd_points["gini_coefficient"] - 3 * nd_points["overall_violation_rate_percent"]
        return {"n": int(len(sub)), "non_dominated_proxy_count": int((score >= np.quantile(score, 0.9)).sum())}

    if experiment_id == "EXP-H4-CROSS_SOLVER_SHADOW_MODE":
        high_stress = sub[sub["stress_case"] != "nominal"]
        nominal = sub[sub["stress_case"] == "nominal"]
        return {
            "n": int(len(sub)),
            "nominal_delta_util_mean": float(nominal["delta_tool_utilization_percent"].mean()),
            "stress_delta_util_mean": float(high_stress["delta_tool_utilization_percent"].mean()) if not high_stress.empty else np.nan,
        }

    return {"n": int(len(sub))}


def evaluate_acceptance(df: pd.DataFrame) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}

    h1 = df[df.experiment_id == "EXP-H1-CERTIFIED_TRIGGER_SECURITY"]
    nominal = h1[h1.counterexample_mode == "none"]
    cond_h1 = bool((nominal["certified_false_accept_rate"] <= 1e-12).all())
    cond_gap = bool((h1["compute_optimality_gap_J_pi_minus_J_pi_star"] >= -1e-12).all())
    out["EXP-H1-CERTIFIED_TRIGGER_SECURITY"] = {
        "pass": bool(cond_h1 and cond_gap),
        "checks": {
            "nominal_false_accept_zero": cond_h1,
            "optimality_gap_nonnegative": cond_gap,
        },
    }

    h2 = df[df.experiment_id == "EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION"]
    cond_h2 = bool((h2["coverage_error_pp"].abs() <= 0.5).mean() >= 0.95)
    cond_overhead = bool((h2["calibration_overhead_percent"] <= 15.0).mean() >= 0.8)
    out["EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION"] = {
        "pass": bool(cond_h2 and cond_overhead),
        "checks": {
            "coverage_error_within_0_5pp_majority": cond_h2,
            "overhead_within_15pct_majority": cond_overhead,
        },
    }

    h3 = df[df.experiment_id == "EXP-H3-FAIRNESS_POLICY_SURFACE"]
    utilitarian = h3[h3["baseline"].str.contains("Utilitarian", case=False, na=False)]
    best = h3[h3["beta"] == "1.0"]
    improvement = float(utilitarian["worst_decile_curtailment_percent"].mean() - best["worst_decile_curtailment_percent"].mean())
    cond_h3 = bool(improvement >= 10.0)
    out["EXP-H3-FAIRNESS_POLICY_SURFACE"] = {
        "pass": cond_h3,
        "checks": {"worst_decile_improvement_ge_10": cond_h3},
    }

    h4 = df[df.experiment_id == "EXP-H4-CROSS_SOLVER_SHADOW_MODE"]
    cond_u = bool((h4["delta_tool_utilization_percent"] <= 1.5).mean() >= 0.95)
    cond_v = bool((h4["delta_tool_violation_pp"] <= 0.1).mean() >= 0.95)
    cond_r = bool((h4["reproducibility_pass_rate_percent"] >= 95).mean() >= 0.95)
    out["EXP-H4-CROSS_SOLVER_SHADOW_MODE"] = {
        "pass": bool(cond_u and cond_v and cond_r),
        "checks": {
            "delta_tool_utilization_le_1_5_majority": cond_u,
            "delta_tool_violation_le_0_1_majority": cond_v,
            "reproducibility_ge_95_majority": cond_r,
        },
    }
    return out
