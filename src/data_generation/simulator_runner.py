"""
Simulation Runner Module for Stage 3 Dataset Generation.

Executes scenarios through the Stage 2 multi-stage mechanistic model
(Topology A, 3:2 vessel staging, 15 Toray TML20D-400 elements, 555 m²),
capturing full process outputs, element health descriptors, and handling
boundary failures gracefully.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.stage import ROStage
from ro_model.system import ROSystem, SystemResult
from ro_model.water_quality import WaterQualityStream, ApparentRejectionProfile
from data_generation.feasibility import (
    FailureCategory,
    classify_simulation_failure,
)
from data_generation.quality_control import (
    QualityFlag,
    verify_scenario_quality,
)


def create_baseline_system(
    num_vessels_stage1: int = 3,
    num_vessels_stage2: int = 2,
    elements_per_vessel: int = 3,
    aw: float = 9.446312125982804e-07,
    as_salt: float = 1.7827e-8,
    k_mass_transfer: float = 5.0e-5,
    dp_element_bar: float = 0.15,
    max_element_recovery: float = 0.30,
) -> ROSystem:
    """
    Build the standard Stage 2 model-derived 2-stage RO system.
    """
    aw_pa = aw * 1.0e-5 if aw > 1.0e-8 else aw
    props = MembraneElementProperties(
        name="Toray TML20D-400",
        membrane_area_m2=37.0,
        membrane_diameter_m=0.201,
        Aw_m_pa_s=aw_pa,
        As_m_s=as_salt,
        max_operating_pressure_pa=4.1e6,
    )
    cfg = SimulationConfig(
        mass_transfer_coefficient=k_mass_transfer,
        pressure_drop_pa=dp_element_bar * 1e5,
        max_element_recovery=max_element_recovery,
        pump_efficiency=0.80,
    )

    stage1 = ROStage(
        name="Stage_1",
        parallel_vessels=num_vessels_stage1,
        elements_per_vessel=elements_per_vessel,
        element_properties=props,
        config=cfg,
        element_pressure_drop_bar=dp_element_bar,
    )
    stage2 = ROStage(
        name="Stage_2",
        parallel_vessels=num_vessels_stage2,
        elements_per_vessel=elements_per_vessel,
        element_properties=props,
        config=cfg,
        element_pressure_drop_bar=dp_element_bar,
    )

    system = ROSystem(
        name="Stage3_Base_2Stage_RO",
        stages=[stage1, stage2],
        topology="concentrate_to_stage2",
        config=cfg,
    )

    return system


def run_single_simulation(
    feed_flow_m3h: float,
    feed_tds_mgL: float,
    feed_cod_mgL: float,
    feed_pH: float,
    temperature_C: float,
    stage1_pressure_bar: float,
    stage2_pressure_bar: float,
    system: Optional[ROSystem] = None,
) -> Dict[str, Any]:
    """
    Execute a single operating scenario and return structured performance dictionary.
    """
    sys = system or create_baseline_system()

    # Base input dict
    record: Dict[str, Any] = {
        "feed_flow_m3h": float(feed_flow_m3h),
        "feed_tds_mgL": float(feed_tds_mgL),
        "feed_cod_mgL": float(feed_cod_mgL),
        "feed_pH": float(feed_pH),
        "temperature_C": float(temperature_C),
        "stage1_pressure_bar": float(stage1_pressure_bar),
        "stage2_pressure_bar": float(stage2_pressure_bar),
        "feasible": 0,
        "failure_reason": FailureCategory.NONE.value,
        "failure_message": "",
        "quality_flag": QualityFlag.PASS.value,
        "overall_recovery_pct": np.nan,
        "permeate_flow_m3h": np.nan,
        "concentrate_flow_m3h": np.nan,
        "permeate_tds_mgL": np.nan,
        "concentrate_tds_mgL": np.nan,
        "overall_tds_rejection_pct": np.nan,
        "stage1_recovery_pct": np.nan,
        "stage2_recovery_pct": np.nan,
        "average_flux_LMH": np.nan,
        "minimum_flux_LMH": np.nan,
        "maximum_flux_LMH": np.nan,
        "maximum_element_recovery_pct": np.nan,
        "maximum_polarization_modulus": np.nan,
        "feed_osmotic_pressure_bar": np.nan,
        "final_concentrate_osmotic_pressure_bar": np.nan,
        "stage1_pump_power_kW": np.nan,
        "stage2_booster_power_kW": np.nan,
        "total_power_kW": np.nan,
        "SEC_kWh_m3": np.nan,
        "water_balance_error": np.nan,
        "solute_balance_error": np.nan,
        "flux_decline_stage1_pct": np.nan,
        "flux_decline_stage2_pct": np.nan,
        "max_element_concentrate_tds_mgL": np.nan,
        "max_element_osmotic_pressure_bar": np.nan,
    }

    # Check immediate pressure limit
    if stage1_pressure_bar > 41.0 or stage2_pressure_bar > 41.0:
        cat, msg = classify_simulation_failure(
            context={"pressure_limit_exceeded": True}
        )
        record["failure_reason"] = cat.value
        record["failure_message"] = msg
        record["quality_flag"] = QualityFlag.FAIL.value
        return record

    try:
        res: SystemResult = sys.solve(
            feed_flow_m3_hr=feed_flow_m3h,
            feed_tds_mg_l=feed_tds_mgL,
            stage_pressures_bar=[stage1_pressure_bar, stage2_pressure_bar],
            temperature_celsius=temperature_C,
        )

        # Extract macro-level outputs
        record["overall_recovery_pct"] = float(res.overall_water_recovery_percent)
        record["permeate_flow_m3h"] = float(res.permeate_flow_m3_hr)
        record["concentrate_flow_m3h"] = float(res.concentrate_flow_m3_hr)
        record["permeate_tds_mgL"] = float(res.permeate_tds_mg_l)
        record["concentrate_tds_mgL"] = float(res.concentrate_tds_mg_l)
        record["overall_tds_rejection_pct"] = float(res.overall_salt_rejection_percent)

        # Stage recoveries
        s1 = res.stage_results[0]
        s2 = res.stage_results[1]
        record["stage1_recovery_pct"] = float(s1.stage_water_recovery_percent)
        record["stage2_recovery_pct"] = float(s2.stage_water_recovery_percent)

        # Element-level metric aggregations across all stages
        all_element_results = []
        for stage_res in res.stage_results:
            if stage_res.vessel_result and stage_res.vessel_result.element_results:
                all_element_results.extend(stage_res.vessel_result.element_results)

        fluxes = [e.water_flux_lmh for e in all_element_results]
        elem_recoveries = [e.water_recovery_percent for e in all_element_results]
        pol_mods = [e.polarization_modulus for e in all_element_results]
        elem_cr = [e.concentrate_tds_mg_l for e in all_element_results]
        elem_pi_r = [e.concentrate_osmotic_pressure_bar for e in all_element_results]

        record["average_flux_LMH"] = float(res.average_system_flux_lmh)
        record["minimum_flux_LMH"] = float(np.min(fluxes))
        record["maximum_flux_LMH"] = float(np.max(fluxes))
        record["maximum_element_recovery_pct"] = float(np.max(elem_recoveries))
        record["maximum_polarization_modulus"] = float(np.max(pol_mods))

        # Osmotic pressures
        record["feed_osmotic_pressure_bar"] = float(
            all_element_results[0].feed_osmotic_pressure_bar
        )
        record["final_concentrate_osmotic_pressure_bar"] = float(
            all_element_results[-1].concentrate_osmotic_pressure_bar
        )

        # Energy & Power
        record["stage1_pump_power_kW"] = float(s1.electrical_power_kw)
        record["stage2_booster_power_kW"] = float(s2.electrical_power_kw)
        record["total_power_kW"] = float(res.total_electrical_power_kw)
        record["SEC_kWh_m3"] = float(res.system_sec_kwh_per_m3)

        # Balance residuals
        record["water_balance_error"] = float(res.water_mass_balance_error_m3_s * 3600.0)
        record["solute_balance_error"] = float(res.solute_mass_balance_error_kg_s * 3600.0)

        # Element health & flux decline descriptors
        s1_vessel_elems = s1.vessel_result.element_results
        s2_vessel_elems = s2.vessel_result.element_results

        s1_j_lead = s1_vessel_elems[0].water_flux_lmh
        s1_j_tail = s1_vessel_elems[-1].water_flux_lmh
        s2_j_lead = s2_vessel_elems[0].water_flux_lmh
        s2_j_tail = s2_vessel_elems[-1].water_flux_lmh

        record["flux_decline_stage1_pct"] = float(
            ((s1_j_lead - s1_j_tail) / s1_j_lead) * 100.0 if s1_j_lead > 0 else 0.0
        )
        record["flux_decline_stage2_pct"] = float(
            ((s2_j_lead - s2_j_tail) / s2_j_lead) * 100.0 if s2_j_lead > 0 else 0.0
        )
        record["max_element_concentrate_tds_mgL"] = float(np.max(elem_cr))
        record["max_element_osmotic_pressure_bar"] = float(np.max(elem_pi_r))

        # Check quality control
        qflag, qreasons = verify_scenario_quality(record)
        record["quality_flag"] = qflag.value

        if qflag == QualityFlag.FAIL:
            cat, msg = classify_simulation_failure(
                error_message="; ".join(qreasons)
            )
            record["feasible"] = 0
            record["failure_reason"] = cat.value
            record["failure_message"] = msg
        else:
            record["feasible"] = 1
            record["failure_reason"] = FailureCategory.NONE.value
            record["failure_message"] = ""

    except Exception as exc:
        cat, msg = classify_simulation_failure(exception=exc)
        record["feasible"] = 0
        record["failure_reason"] = cat.value
        record["failure_message"] = msg
        record["quality_flag"] = QualityFlag.FAIL.value

        # Fill output fields with NaN
        null_fields = [
            "overall_recovery_pct",
            "permeate_flow_m3h",
            "concentrate_flow_m3h",
            "permeate_tds_mgL",
            "concentrate_tds_mgL",
            "overall_tds_rejection_pct",
            "stage1_recovery_pct",
            "stage2_recovery_pct",
            "average_flux_LMH",
            "minimum_flux_LMH",
            "maximum_flux_LMH",
            "maximum_element_recovery_pct",
            "maximum_polarization_modulus",
            "feed_osmotic_pressure_bar",
            "final_concentrate_osmotic_pressure_bar",
            "stage1_pump_power_kW",
            "stage2_booster_power_kW",
            "total_power_kW",
            "SEC_kWh_m3",
            "water_balance_error",
            "solute_balance_error",
            "flux_decline_stage1_pct",
            "flux_decline_stage2_pct",
            "max_element_concentrate_tds_mgL",
            "max_element_osmotic_pressure_bar",
        ]
        for f in null_fields:
            record[f] = np.nan

    return record
