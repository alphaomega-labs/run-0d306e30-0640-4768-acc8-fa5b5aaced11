from __future__ import annotations
# mypy: disable-error-code=attr-defined

from pathlib import Path
from typing import Dict

import sympy as sp


def run_sympy_validation(report_path: Path) -> Dict[str, object]:
    m, B, eta, r = sp.symbols("m B eta r", real=True)
    L, d = sp.symbols("L d", nonnegative=True, real=True)
    c_ncv, c_lin = sp.symbols("c_ncv c_lin", positive=True, real=True)
    c_gap = sp.symbols("c_gap", positive=True, real=True)
    q = sp.symbols("q", nonnegative=True, real=True)
    p = sp.symbols("p", positive=True, real=True)
    p_slack = sp.symbols("p_slack", nonnegative=True, real=True)

    expr_chain = (-m + sp.Abs(r)).subs({m: B + eta, sp.Abs(r): B})
    dmm_c1_chain_ok = sp.simplify(expr_chain + eta) == 0

    b_expr = sp.Rational(1, 2) * L * d**2
    dmm_c1_residual_nonneg = sp.ask(sp.Q.nonnegative(b_expr))

    gap = (c_ncv - c_lin) * q * (1 - p)
    dmm_c2_gap_factorized = sp.simplify(sp.factor(gap) - gap) == 0
    gap_admissible = c_gap * q * p_slack
    dmm_c2_gap_nonnegative_under_admissibility = sp.ask(sp.Q.nonnegative(gap_admissible))

    strict_case = gap.subs({q: sp.Rational(1, 2), p: sp.Rational(3, 4), c_ncv: 3, c_lin: 1})
    dmm_c2_strict_positive_example = bool(strict_case > 0)

    ui, alpha, u0 = sp.symbols("ui alpha u0", positive=True, real=True)
    alpha_f = ui ** (1 - alpha) / (1 - alpha)
    d1 = sp.diff(alpha_f, ui)
    d2 = sp.diff(d1, ui)

    log_b = sp.log(ui - u0)
    lb1 = sp.diff(log_b, ui)
    lb2 = sp.diff(lb1, ui)

    results = {
        "dmm_c1_chain_ok": bool(dmm_c1_chain_ok),
        "dmm_c1_residual_nonnegative": bool(dmm_c1_residual_nonneg),
        "dmm_c2_gap_factorized": bool(dmm_c2_gap_factorized),
        "dmm_c2_gap_nonnegative_under_admissibility": bool(dmm_c2_gap_nonnegative_under_admissibility),
        "dmm_c2_strict_positive_example": bool(dmm_c2_strict_positive_example),
        "hm_h3_alpha_derivative": str(sp.simplify(d1)),
        "hm_h3_alpha_second_derivative": str(sp.simplify(d2)),
        "hm_h3_log_derivative": str(sp.simplify(lb1)),
        "hm_h3_log_second_derivative": str(sp.simplify(lb2)),
    }

    report_path.write_text(
        "\n".join([
            "SymPy Validation Report",
            f"dmm_c1_chain_ok: {results['dmm_c1_chain_ok']}",
            f"dmm_c1_residual_nonnegative: {results['dmm_c1_residual_nonnegative']}",
            f"dmm_c2_gap_factorized: {results['dmm_c2_gap_factorized']}",
            f"dmm_c2_gap_nonnegative_under_admissibility: {results['dmm_c2_gap_nonnegative_under_admissibility']}",
            f"dmm_c2_strict_positive_example: {results['dmm_c2_strict_positive_example']}",
            f"hm_h3_alpha_derivative: {results['hm_h3_alpha_derivative']}",
            f"hm_h3_alpha_second_derivative: {results['hm_h3_alpha_second_derivative']}",
            f"hm_h3_log_derivative: {results['hm_h3_log_derivative']}",
            f"hm_h3_log_second_derivative: {results['hm_h3_log_second_derivative']}",
        ]) + "\n",
        encoding="utf-8",
    )
    return results
