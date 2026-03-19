from rdoe_validation.analysis import evaluate_acceptance
from rdoe_validation.core import ExperimentSpec, simulate_experiment


def test_h1_optimality_gap_nonnegative() -> None:
    spec = ExperimentSpec(
        experiment_id="EXP-H1-CERTIFIED_TRIGGER_SECURITY",
        baselines=["Full non-convex robust UTOPF (no screening)"],
        seeds=[11],
        sweep_params={
            "counterexample_mode": ["none", "underestimated_L"],
            "eta": ["0.01"],
            "hessian_bound_inflation": ["1.0"],
            "loading_level": ["1.0"],
            "trust_region_radius_rho_pu": ["0.02"],
            "uncertainty_scale": ["1.0x"],
        },
    )
    df = simulate_experiment(spec, max_cases=6)
    assert (df["compute_optimality_gap_J_pi_minus_J_pi_star"] >= 0).all()


def test_acceptance_map_contains_all_experiments() -> None:
    experiments = [
        ExperimentSpec(
            experiment_id="EXP-H1-CERTIFIED_TRIGGER_SECURITY",
            baselines=["Full non-convex robust UTOPF (no screening)"],
            seeds=[11],
            sweep_params={
                "counterexample_mode": ["none"],
                "eta": ["0.01"],
                "hessian_bound_inflation": ["1.0"],
                "loading_level": ["1.0"],
                "trust_region_radius_rho_pu": ["0.02"],
                "uncertainty_scale": ["1.0x"],
            },
        ),
        ExperimentSpec(
            experiment_id="EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION",
            baselines=["KA03 static robust uncertainty box"],
            seeds=[101],
            sweep_params={
                "delta": ["0.05"],
                "regime_buckets": ["tod_only"],
                "rolling_window_steps": ["288"],
                "scaling_matrix_mode": ["identity"],
                "update_cadence": ["5min"],
            },
        ),
        ExperimentSpec(
            experiment_id="EXP-H3-FAIRNESS_POLICY_SURFACE",
            baselines=["Utilitarian max-utilization allocator"],
            seeds=[7],
            sweep_params={
                "alpha": ["1.0"],
                "beta": ["1.0"],
                "customer_weight_scheme": ["uniform"],
                "disagreement_scale": ["1.0"],
                "gamma_risk_penalty": ["0.1"],
            },
        ),
        ExperimentSpec(
            experiment_id="EXP-H4-CROSS_SOLVER_SHADOW_MODE",
            baselines=["Single-tool pandapower reference pipeline"],
            seeds=[13],
            sweep_params={
                "dso_baseline_mode": ["static_export_limit"],
                "harmonization_profile": ["standard"],
                "solver_pair": ["pandapower_vs_pmd"],
                "stress_case": ["nominal"],
                "time_resolution": ["15min"],
            },
        ),
    ]
    frames = [simulate_experiment(spec, max_cases=2) for spec in experiments]
    import pandas as pd

    full_df = pd.concat(frames, ignore_index=True)
    result = evaluate_acceptance(full_df)
    assert set(result.keys()) == {
        "EXP-H1-CERTIFIED_TRIGGER_SECURITY",
        "EXP-H2-ONLINE_UNCERTAINTY_CALIBRATION",
        "EXP-H3-FAIRNESS_POLICY_SURFACE",
        "EXP-H4-CROSS_SOLVER_SHADOW_MODE",
    }
