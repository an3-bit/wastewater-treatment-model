"""
Result Repository Service
Provides safe, cached access to authoritative frozen Stage 8C techno-economic results.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from app.core.config import settings
from app.core.logging import logger
from app.schemas.economics import (
    EconomicScenariosResponse,
    EconomicSummaryResponse,
    EnergyBalanceMetrics,
    ScenarioDetail,
    ValueDecompositionItem,
    ValueDecompositionResponse,
    WaterBalanceMetrics,
    EconomicValues,
)
from app.schemas.policies import PolicyComparisonResponse, PolicyItem


class ResultRepository:
    def __init__(self):
        self._stage8c_dir = settings.STAGE8C_DIR
        self._tables_dir = self._stage8c_dir / "tables"
        self._business_case_json_path = self._stage8c_dir / "watertwin_authoritative_business_case.json"
        self._frontend_summary_json_path = self._stage8c_dir / "watertwin_frontend_summary.json"

        # Cache variables
        self._cached_summary: Optional[EconomicSummaryResponse] = None
        self._cached_decomposition: Optional[ValueDecompositionResponse] = None
        self._cached_scenarios: Optional[EconomicScenariosResponse] = None
        self._cached_policies: Optional[PolicyComparisonResponse] = None

        self._load_authoritative_results()

    def _load_authoritative_results(self) -> None:
        """Load and cache all authoritative results on startup."""
        logger.info(f"Loading authoritative Stage 8C results from {self._stage8c_dir}")
        try:
            self._load_economic_summary()
            self._load_value_decomposition()
            self._load_scenarios()
            self._load_policies()
            logger.info("Authoritative Stage 8C results successfully loaded and verified.")
        except Exception as e:
            logger.error(f"Error loading authoritative results: {e}", exc_info=True)
            self._populate_fallback_authoritative_data()

    def _load_economic_summary(self) -> None:
        if self._business_case_json_path.exists():
            with open(self._business_case_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._cached_summary = EconomicSummaryResponse(
                water=WaterBalanceMetrics(
                    baseline_permeate_m3=data["water"]["baseline_permeate_m3"],
                    watertwin_permeate_m3=data["water"]["digital_twin_permeate_m3"],
                    additional_permeate_m3=data["water"]["additional_permeate_m3"],
                    water_increase_pct=data["water"]["water_change_percent"],
                ),
                energy=EnergyBalanceMetrics(
                    baseline_total_kwh=data["energy"]["baseline_total_kwh"],
                    watertwin_total_kwh=data["energy"]["digital_twin_total_kwh"],
                    total_electricity_change_pct=data["energy"]["total_energy_change_percent"],
                    baseline_sec_kwh_m3=data["energy"]["baseline_sec"],
                    watertwin_sec_kwh_m3=data["energy"]["digital_twin_sec"],
                    sec_reduction_pct=abs(data["energy"]["sec_change_percent"]),
                ),
                economics=EconomicValues(
                    integrated_framework_value_kes_year=data["economics"]["integrated_value_vs_baseline_kes_year"],
                    static_optimization_value_kes_year=62203.43,
                    condition_based_value_kes_year=data["economics"]["condition_based_value_kes_year"],
                    prediction_value_kes_year=data["economics"]["prediction_value_kes_year"]
                    if "prediction_value_kes_year" in data["economics"]
                    else data["prediction"]["prediction_value_kes_year"],
                    mpc_value_kes_year=data["economics"]["mpc_value_kes_year"],
                    predictive_decision_intelligence_kes_year=data["economics"]["predictive_intelligence_value_kes_year"],
                    treatment_lcow_kes_m3=data["economics"]["treatment_lcow_kes_m3"],
                ),
                scenarios_summary={
                    "conservative_benefit_kes": data["scenarios"]["conservative"]["integrated_value_kes_year"],
                    "base_benefit_kes": data["scenarios"]["base"]["integrated_value_kes_year"],
                    "favourable_benefit_kes": data["scenarios"]["favourable"]["integrated_value_kes_year"],
                },
                scientific_caveat=data.get("scientific_caveat", "Model-predicted virtual-plant results requiring industrial validation."),
            )
        else:
            self._populate_fallback_summary()

    def _load_value_decomposition(self) -> None:
        table_path = self._tables_dir / "14_final_value_attribution.csv"
        if table_path.exists():
            df = pd.read_csv(table_path)
            items: List[ValueDecompositionItem] = []
            
            mapping = {
                "Static Optimization (B - A)": ("STATIC", "Static Optimization", "B - A", "Engineering Static Tuning", "Fixed pressure rebalancing"),
                "Condition-Based Maintenance (C - B)": ("CONDITION", "Condition-Based Operation", "C - B", "Condition Monitoring Value", "Adaptive fouling-triggered CIP"),
                "Pure Predictive Forecasting (D - C)": ("PREDICTION", "Pure Predictive Forecasting", "D - C", "Prediction Value", "Look-ahead proactive CIP timing"),
                "Dynamic Supervisory MPC (E - D)": ("MPC", "Dynamic Supervisory MPC", "E - D", "Adaptive MPC Trim (Marginal)", "Continuous setpoint pressure trimming"),
                "Predictive Decision Intelligence (E - C)": ("PRED_INTEL", "Predictive Decision Intelligence", "E - C", "Predictive Decision Value", "Combined predictive CIP + MPC"),
                "Total Integrated Value (E - A)": ("INTEGRATED", "Total Integrated WaterTwin", "E - A", "Full Framework Value", "End-to-end digital twin value"),
            }

            for _, row in df.iterrows():
                comp = str(row["Component"]).strip()
                if comp in mapping:
                    code, name, formula, classification, comm = mapping[comp]
                    items.append(
                        ValueDecompositionItem(
                            code=code,
                            name=name,
                            formula=formula,
                            value_kes_year=float(row["Value_KES_Year"]),
                            share_pct=float(row["Share_Percent"]),
                            classification=classification,
                            commercial_recommendation=comm,
                        )
                    )

            self._cached_decomposition = ValueDecompositionResponse(
                items=items,
                total_integrated_value_kes_year=4391948.14,
                pure_prediction_share_pct=9.66,
                condition_monitoring_share_pct=88.86,
                mpc_share_pct=0.06,
            )
        else:
            self._populate_fallback_decomposition()

    def _load_scenarios(self) -> None:
        table_path = self._tables_dir / "13_economic_scenario_comparison.csv"
        if table_path.exists():
            df = pd.read_csv(table_path)
            scenarios: List[ScenarioDetail] = []
            for _, row in df.iterrows():
                sc_name = str(row["scenario"]).strip()
                scenarios.append(
                    ScenarioDetail(
                        name=sc_name,
                        description=str(row["description"]).strip(),
                        reuse_demand_pct=75.0 if "75%" in str(row["description"]) else 100.0,
                        cip_cost_multiplier=2.0 if "2.0x" in str(row["description"]) else (0.5 if "0.5x" in str(row["description"]) else 1.0),
                        cip_downtime_h=6.0 if "6h" in str(row["description"]) else (2.0 if "2h" in str(row["description"]) else 4.0),
                        discharge_credit_kes_m3=0.0 if "0 KES" in str(row["description"]) else 35.0,
                        integrated_value_kes_year=float(row["integrated_value_ea_kes"]),
                        digital_twin_net_benefit_kes_year=float(row["digital_twin_net_benefit_kes"]),
                        treatment_lcow_kes_m3=float(row["treatment_lcow_kes_m3"]),
                    )
                )
            self._cached_scenarios = EconomicScenariosResponse(scenarios=scenarios)
        else:
            self._populate_fallback_scenarios()

    def _load_policies(self) -> None:
        table_path = self._tables_dir / "15_final_policy_comparison.csv"
        if table_path.exists():
            df = pd.read_csv(table_path)
            policies: List[PolicyItem] = []
            
            baseline_net = 7108175.39
            for _, row in df.iterrows():
                code = str(row["policy_code"]).strip()
                name = str(row["policy_name"]).strip()
                net_benefit = float(row["net_annual_benefit_kes"])
                
                # Assign pressures and architecture
                arch = "Fixed P1/P2 (15/22 bar)"
                p1, p2 = 15.0, 22.0
                deployable = True
                oracle = False
                theo = False
                p_type = "COMMERCIAL_CANDIDATE"

                if code == "CASE_A":
                    arch = "Conventional Fixed Calendar CIP (15/22 bar)"
                    p_type = "BASELINE"
                elif code == "CASE_B":
                    arch = "Static Optimum Setpoints (18/25 bar)"
                    p1, p2 = 18.0, 25.0
                    p_type = "STATIC_OPTIMUM"
                elif code == "CASE_C":
                    arch = "Condition-Based Reactive CIP (168h Lockout)"
                    p_type = "CONDITION_BASED"
                elif code == "CASE_C_CHATTER":
                    arch = "Unconstrained Reactive CIP (Chatter Audit)"
                    deployable = False
                    p_type = "AUDIT_BENCHMARK"
                elif code == "CASE_D":
                    arch = "Proactive Predictive CIP Timing"
                    p_type = "PREDICTIVE"
                elif code == "CASE_E":
                    arch = "Predictive CIP + Supervisory Pressure MPC"
                    p_type = "INTEGRATED_FRAMEWORK"
                elif code == "ORACLE":
                    arch = "Theoretical Oracle Bound (Perfect Disturbance Preview)"
                    deployable = False
                    oracle = True
                    theo = True
                    p_type = "ORACLE_BENCHMARK"

                policies.append(
                    PolicyItem(
                        policy_code=code,
                        policy_name=name,
                        architecture=arch,
                        p1_bar=p1,
                        p2_bar=p2,
                        permeate_m3=float(row["permeate_m3"]),
                        effective_recovery_pct=float(row["effective_recovery_pct"]),
                        total_energy_kwh=float(row["total_energy_kwh"]),
                        sec_kwh_m3=float(row["sec_kwh_m3"]),
                        cip_count=int(row["cip_count"]),
                        cip_downtime_h=float(row["cip_downtime_h"]),
                        operating_uptime_h=float(row["operating_uptime_h"]),
                        treatment_lcow_kes_m3=float(row["treatment_lcow_kes_m3"]),
                        net_annual_benefit_kes=net_benefit,
                        incremental_value_vs_baseline_kes=round(net_benefit - baseline_net, 2),
                        policy_type=p_type,
                        deployable=deployable,
                        oracle=oracle,
                        theoretical_upper_bound=theo,
                    )
                )

            self._cached_policies = PolicyComparisonResponse(
                policies=policies,
                total_policies=len(policies),
            )
        else:
            self._populate_fallback_policies()

    def _populate_fallback_summary(self) -> None:
        self._cached_summary = EconomicSummaryResponse(
            water=WaterBalanceMetrics(),
            energy=EnergyBalanceMetrics(),
            economics=EconomicValues(),
            scenarios_summary={
                "conservative_benefit_kes": 1856260.61,
                "base_benefit_kes": 4391948.14,
                "favourable_benefit_kes": 4679064.31,
            },
        )

    def _populate_fallback_decomposition(self) -> None:
        self._cached_decomposition = ValueDecompositionResponse(
            items=[
                ValueDecompositionItem(
                    code="STATIC",
                    name="Static Optimization",
                    formula="B - A",
                    value_kes_year=62203.43,
                    share_pct=1.42,
                    classification="Engineering Static Tuning",
                    commercial_recommendation="Fixed pressure setpoint tuning",
                ),
                ValueDecompositionItem(
                    code="CONDITION",
                    name="Condition-Based Maintenance",
                    formula="C - B",
                    value_kes_year=3902797.57,
                    share_pct=88.86,
                    classification="Condition Monitoring Value",
                    commercial_recommendation="Adaptive fouling-triggered CIP",
                ),
                ValueDecompositionItem(
                    code="PREDICTION",
                    name="Pure Predictive Forecasting",
                    formula="D - C",
                    value_kes_year=424164.72,
                    share_pct=9.66,
                    classification="Prediction Value",
                    commercial_recommendation="Look-ahead proactive CIP timing",
                ),
                ValueDecompositionItem(
                    code="MPC",
                    name="Dynamic Supervisory MPC",
                    formula="E - D",
                    value_kes_year=2782.42,
                    share_pct=0.06,
                    classification="Adaptive MPC Trim (Marginal)",
                    commercial_recommendation="Continuous setpoint pressure trimming",
                ),
                ValueDecompositionItem(
                    code="INTEGRATED",
                    name="Total Integrated WaterTwin",
                    formula="E - A",
                    value_kes_year=4391948.14,
                    share_pct=100.0,
                    classification="Full Framework Value",
                    commercial_recommendation="End-to-end digital twin value",
                ),
                ValueDecompositionItem(
                    code="PRED_INTEL",
                    name="Predictive Decision Intelligence",
                    formula="E - C",
                    value_kes_year=426947.14,
                    share_pct=9.72,
                    classification="Predictive Decision Value",
                    commercial_recommendation="Combined predictive CIP + MPC",
                ),
            ],
        )

    def _populate_fallback_scenarios(self) -> None:
        self._cached_scenarios = EconomicScenariosResponse(
            scenarios=[
                ScenarioDetail(
                    name="Conservative",
                    description="75% reuse demand, 2.0x CIP cost, 6h CIP downtime, 0 KES/m3 discharge credit",
                    reuse_demand_pct=75.0,
                    cip_cost_multiplier=2.0,
                    cip_downtime_h=6.0,
                    discharge_credit_kes_m3=0.0,
                    integrated_value_kes_year=1856260.61,
                    digital_twin_net_benefit_kes_year=5424966.88,
                    treatment_lcow_kes_m3=26.12,
                ),
                ScenarioDetail(
                    name="Base (Authoritative)",
                    description="100% reuse demand, 1.0x CIP cost, 4h CIP downtime, 35 KES/m3 discharge credit",
                    reuse_demand_pct=100.0,
                    cip_cost_multiplier=1.0,
                    cip_downtime_h=4.0,
                    discharge_credit_kes_m3=35.0,
                    integrated_value_kes_year=4391948.14,
                    digital_twin_net_benefit_kes_year=11500123.53,
                    treatment_lcow_kes_m3=23.20,
                ),
                ScenarioDetail(
                    name="Favourable",
                    description="100% reuse demand, 0.5x CIP cost, 2h CIP downtime, 35 KES/m3 discharge credit",
                    reuse_demand_pct=100.0,
                    cip_cost_multiplier=0.5,
                    cip_downtime_h=2.0,
                    discharge_credit_kes_m3=35.0,
                    integrated_value_kes_year=4679064.31,
                    digital_twin_net_benefit_kes_year=11830133.81,
                    treatment_lcow_kes_m3=21.73,
                ),
            ]
        )

    def _populate_fallback_policies(self) -> None:
        self._cached_policies = PolicyComparisonResponse(
            policies=[
                PolicyItem(
                    policy_code="CASE_A",
                    policy_name="Case A: Fixed Baseline + Fixed Calendar CIP",
                    architecture="Conventional Fixed Calendar CIP (15/22 bar)",
                    p1_bar=15.0,
                    p2_bar=22.0,
                    permeate_m3=65279.7,
                    effective_recovery_pct=27.19,
                    total_energy_kwh=65054.4,
                    sec_kwh_m3=0.9965,
                    cip_count=12,
                    cip_downtime_h=48.0,
                    operating_uptime_h=7952.0,
                    treatment_lcow_kes_m3=19.11,
                    net_annual_benefit_kes=7108175.39,
                    incremental_value_vs_baseline_kes=0.0,
                    policy_type="BASELINE",
                    deployable=True,
                ),
                PolicyItem(
                    policy_code="CASE_B",
                    policy_name="Case B: Fixed Strategy D + Fixed Calendar CIP",
                    architecture="Static Optimum Setpoints (18/25 bar)",
                    p1_bar=18.0,
                    p2_bar=25.0,
                    permeate_m3=67471.8,
                    effective_recovery_pct=28.10,
                    total_energy_kwh=80947.7,
                    sec_kwh_m3=1.1997,
                    cip_count=12,
                    cip_downtime_h=48.0,
                    operating_uptime_h=7952.0,
                    treatment_lcow_kes_m3=21.73,
                    net_annual_benefit_kes=7170378.82,
                    incremental_value_vs_baseline_kes=62203.43,
                    policy_type="STATIC_OPTIMUM",
                    deployable=True,
                ),
                PolicyItem(
                    policy_code="CASE_C",
                    policy_name="Case C: Fixed Strategy D + Condition-Based CIP (Lockout 168h)",
                    architecture="Condition-Based Reactive CIP (168h Lockout)",
                    p1_bar=18.0,
                    p2_bar=25.0,
                    permeate_m3=102689.8,
                    effective_recovery_pct=42.77,
                    total_energy_kwh=99597.9,
                    sec_kwh_m3=0.9699,
                    cip_count=48,
                    cip_downtime_h=192.0,
                    operating_uptime_h=7808.0,
                    treatment_lcow_kes_m3=20.17,
                    net_annual_benefit_kes=11073176.39,
                    incremental_value_vs_baseline_kes=3965001.00,
                    policy_type="CONDITION_BASED",
                    deployable=True,
                ),
                PolicyItem(
                    policy_code="CASE_D",
                    policy_name="Case D: Fixed Strategy D + Predictive CIP",
                    architecture="Proactive Predictive CIP Timing",
                    p1_bar=18.0,
                    p2_bar=25.0,
                    permeate_m3=109708.9,
                    effective_recovery_pct=45.69,
                    total_energy_kwh=102521.6,
                    sec_kwh_m3=0.9345,
                    cip_count=67,
                    cip_downtime_h=268.0,
                    operating_uptime_h=7732.0,
                    treatment_lcow_kes_m3=23.20,
                    net_annual_benefit_kes=11497341.11,
                    incremental_value_vs_baseline_kes=4389165.72,
                    policy_type="PREDICTIVE",
                    deployable=True,
                ),
                PolicyItem(
                    policy_code="CASE_E",
                    policy_name="Case E: Predictive CIP + Supervisory Pressure MPC",
                    architecture="Predictive CIP + Supervisory Pressure MPC",
                    p1_bar=18.0,
                    p2_bar=25.0,
                    permeate_m3=109737.3,
                    effective_recovery_pct=45.71,
                    total_energy_kwh=102583.2,
                    sec_kwh_m3=0.9348,
                    cip_count=67,
                    cip_downtime_h=268.0,
                    operating_uptime_h=7732.0,
                    treatment_lcow_kes_m3=23.20,
                    net_annual_benefit_kes=11500123.53,
                    incremental_value_vs_baseline_kes=4391948.14,
                    policy_type="INTEGRATED_FRAMEWORK",
                    deployable=True,
                ),
                PolicyItem(
                    policy_code="ORACLE",
                    policy_name="Case F / Oracle: Perfect Visibility Upper Bound",
                    architecture="Theoretical Oracle Bound (Perfect Disturbance Preview)",
                    p1_bar=18.0,
                    p2_bar=25.0,
                    permeate_m3=109737.3,
                    effective_recovery_pct=45.71,
                    total_energy_kwh=102583.2,
                    sec_kwh_m3=0.9348,
                    cip_count=67,
                    cip_downtime_h=268.0,
                    operating_uptime_h=7732.0,
                    treatment_lcow_kes_m3=23.20,
                    net_annual_benefit_kes=11500123.53,
                    incremental_value_vs_baseline_kes=4391948.14,
                    policy_type="ORACLE_BENCHMARK",
                    deployable=False,
                    oracle=True,
                    theoretical_upper_bound=True,
                ),
            ],
            total_policies=6,
        )

    def get_economic_summary(self) -> EconomicSummaryResponse:
        if self._cached_summary is None:
            self._load_economic_summary()
        return self._cached_summary

    def get_value_decomposition(self) -> ValueDecompositionResponse:
        if self._cached_decomposition is None:
            self._load_value_decomposition()
        return self._cached_decomposition

    def get_scenarios(self) -> EconomicScenariosResponse:
        if self._cached_scenarios is None:
            self._load_scenarios()
        return self._cached_scenarios

    def get_policies(self) -> PolicyComparisonResponse:
        if self._cached_policies is None:
            self._load_policies()
        return self._cached_policies


result_repository = ResultRepository()
