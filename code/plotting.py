from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _theme() -> None:
    sns.set_theme(style="whitegrid", context="talk", palette="colorblind")


def plot_h1(df: pd.DataFrame, out_path: Path) -> None:
    _theme()
    sub = df[df["experiment_id"] == "EXP-H1-CERTIFIED_TRIGGER_SECURITY"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    g1 = sub.groupby("counterexample_mode", as_index=False)["runtime_reduction_vs_full_nonconvex_percent"].agg(["mean", "std", "count"]).reset_index()
    g1["ci95"] = 1.96 * g1["std"] / g1["count"].pow(0.5)
    axes[0].bar(g1["counterexample_mode"], g1["mean"], yerr=g1["ci95"], label="Runtime reduction")
    axes[0].set_xlabel("Counterexample Mode")
    axes[0].set_ylabel("Runtime Reduction (%)")
    axes[0].set_title("H1 Runtime Reduction by Stress Mode")
    axes[0].legend()

    g2 = sub.groupby("counterexample_mode", as_index=False)["certified_false_accept_rate"].agg(["mean", "std", "count"]).reset_index()
    g2["ci95"] = 1.96 * g2["std"] / g2["count"].pow(0.5)
    axes[1].plot(g2["counterexample_mode"], g2["mean"], marker="o", label="False accept rate")
    axes[1].fill_between(g2["counterexample_mode"], g2["mean"] - g2["ci95"], g2["mean"] + g2["ci95"], alpha=0.2, label="95% CI")
    axes[1].set_xlabel("Counterexample Mode")
    axes[1].set_ylabel("Certified False Accept Rate")
    axes[1].set_title("H1 Certification Safety Under Stress")
    axes[1].legend()

    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_h2(df: pd.DataFrame, out_path: Path) -> None:
    _theme()
    sub = df[df["experiment_id"] == "EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    rel = sub.groupby("target_delta", as_index=False)["empirical_violation_rate_percent"].mean()
    axes[0].plot(rel["target_delta"] * 100, rel["empirical_violation_rate_percent"], marker="o", label="Observed")
    axes[0].plot(rel["target_delta"] * 100, rel["target_delta"] * 100, linestyle="--", label="Ideal y=x")
    axes[0].set_xlabel("Target Risk Delta (%)")
    axes[0].set_ylabel("Empirical Violation Rate (%)")
    axes[0].set_title("H2 Reliability Diagram")
    axes[0].legend()

    fr = sub.groupby("target_delta", as_index=False).agg(
        util=("mean_utilization_percent", "mean"),
        util_std=("mean_utilization_percent", "std"),
    )
    fr["ci95"] = 1.96 * fr["util_std"] / (len(sub["seed"].unique()) ** 0.5)
    axes[1].plot(fr["target_delta"] * 100, fr["util"], marker="s", label="Utilization")
    axes[1].fill_between(fr["target_delta"] * 100, fr["util"] - fr["ci95"], fr["util"] + fr["ci95"], alpha=0.2, label="95% CI")
    axes[1].set_xlabel("Target Risk Delta (%)")
    axes[1].set_ylabel("Mean Utilization (%)")
    axes[1].set_title("H2 Utilization-Risk Frontier")
    axes[1].legend()

    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_h3(df: pd.DataFrame, out_path: Path) -> None:
    _theme()
    sub = df[df["experiment_id"] == "EXP-H3-FAIRNESS_POLICY_SURFACE"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    axes[0].scatter(sub["mean_utilization_percent"], 1.0 - sub["gini_coefficient"], c=sub["overall_violation_rate_percent"], label="Policy points")
    axes[0].set_xlabel("Mean Utilization (%)")
    axes[0].set_ylabel("Equity Score (1 - Gini)")
    axes[0].set_title("H3 Pareto-Like Policy Surface")
    axes[0].legend()

    sns.boxplot(data=sub, x="customer_weight_scheme", y="worst_decile_curtailment_percent", ax=axes[1], hue="customer_weight_scheme", legend=True)
    axes[1].set_xlabel("Customer Weight Scheme")
    axes[1].set_ylabel("Worst-Decile Curtailment (%)")
    axes[1].set_title("H3 Equity Distribution by Scheme")
    axes[1].legend(title="Weight scheme")

    fig.savefig(out_path, format="pdf")
    plt.close(fig)


def plot_h4(df: pd.DataFrame, out_path: Path) -> None:
    _theme()
    sub = df[df["experiment_id"] == "EXP-H4-CROSS_SOLVER_SHADOW_MODE"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    tl = sub.groupby("stress_case", as_index=False)["shadow_benefit_B_shadow_percent"].mean()
    axes[0].plot(tl["stress_case"], tl["shadow_benefit_B_shadow_percent"], marker="o", label="Shadow benefit")
    axes[0].set_xlabel("Stress Case")
    axes[0].set_ylabel("Shadow Benefit (%)")
    axes[0].set_title("H4 Shadow-Mode Benefit by Stress")
    axes[0].legend()

    disc = sub.groupby("solver_pair", as_index=False).agg(
        util=("delta_tool_utilization_percent", "mean"),
        util_std=("delta_tool_utilization_percent", "std"),
    )
    disc["ci95"] = 1.96 * disc["util_std"] / (len(sub["seed"].unique()) ** 0.5)
    axes[1].bar(disc["solver_pair"], disc["util"], yerr=disc["ci95"], label="Utilization discrepancy")
    axes[1].axhline(1.5, linestyle="--", color="red", label="Acceptance threshold")
    axes[1].set_xlabel("Solver Pair")
    axes[1].set_ylabel("Delta Utilization (%)")
    axes[1].set_title("H4 Cross-Solver Discrepancy")
    axes[1].legend()

    fig.savefig(out_path, format="pdf")
    plt.close(fig)
