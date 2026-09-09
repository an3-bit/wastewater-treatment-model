"""
Economic KPI and Capital Budgeting Module for Stage 8.

Calculates Net Present Value (NPV), Internal Rate of Return (IRR), Simple & Discounted Payback,
and Maximum Economically Justifiable Implementation CAPEX.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from economics.cost_config import EconomicConfig


@dataclass
class FinancialAppraisalResult:
    incremental_annual_benefit_kes: float
    implementation_capex_kes: float
    discount_rate: float
    project_lifetime_years: int
    npv_5yr_kes: float
    npv_10yr_kes: float
    irr_pct: Optional[float]
    simple_payback_years: float
    discounted_payback_years: Optional[float]
    max_justifiable_capex_1yr_kes: float
    max_justifiable_capex_2yr_kes: float
    max_justifiable_capex_3yr_kes: float


def calculate_financial_appraisal(
    incremental_annual_benefit_kes: float,
    config: EconomicConfig,
    capex_override: Optional[float] = None,
) -> FinancialAppraisalResult:
    """
    Evaluate discounted cash flow financial metrics for digital twin adoption.
    """
    annual_cf = float(incremental_annual_benefit_kes)
    capex = float(capex_override) if capex_override is not None else config.digital_twin_implementation_capex_kes
    r = config.discount_rate

    # Maximum Justifiable CAPEX based on target payback
    max_capex_1yr = annual_cf * 1.0
    max_capex_2yr = annual_cf * 2.0
    max_capex_3yr = annual_cf * 3.0

    # Simple Payback
    simple_payback = (capex / annual_cf) if annual_cf > 0 else 999.0

    # 5-year and 10-year NPV
    def compute_npv(years: int) -> float:
        discounted_cfs = [annual_cf / ((1.0 + r) ** t) for t in range(1, years + 1)]
        return float(-capex + sum(discounted_cfs))

    npv_5 = compute_npv(5)
    npv_10 = compute_npv(10)

    # IRR
    irr_val: Optional[float] = None
    if annual_cf > 0 and capex > 0:
        cfs = [-capex] + [annual_cf] * config.project_lifetime_years
        try:
            # Numerical IRR solver via numpy_financial or polynomial roots
            roots = np.roots(cfs[::-1])
            real_roots = [r.real for r in roots if np.isreal(r) and r.real > 0]
            if real_roots:
                # rate = (1 / root) - 1
                rates = [(1.0 / root) - 1.0 for root in real_roots]
                valid_rates = [rate for rate in rates if rate > -1.0]
                if valid_rates:
                    irr_val = float(min(valid_rates) * 100.0)
        except Exception:
            irr_val = None

    # Discounted Payback
    discounted_payback: Optional[float] = None
    cum_pv = -capex
    for t in range(1, 21):
        cum_pv += annual_cf / ((1.0 + r) ** t)
        if cum_pv >= 0:
            discounted_payback = float(t)
            break

    return FinancialAppraisalResult(
        incremental_annual_benefit_kes=annual_cf,
        implementation_capex_kes=capex,
        discount_rate=r,
        project_lifetime_years=config.project_lifetime_years,
        npv_5yr_kes=npv_5,
        npv_10yr_kes=npv_10,
        irr_pct=irr_val,
        simple_payback_years=simple_payback,
        discounted_payback_years=discounted_payback,
        max_justifiable_capex_1yr_kes=max_capex_1yr,
        max_justifiable_capex_2yr_kes=max_capex_2yr,
        max_justifiable_capex_3yr_kes=max_capex_3yr,
    )
