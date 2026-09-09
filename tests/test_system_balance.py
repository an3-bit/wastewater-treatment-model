"""
Unit and Integration Tests for Multi-Stage ROSystem (Plant Network).
"""

import pytest
import numpy as np

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.stage import ROStage
from ro_model.system import ROSystem, SystemResult
from ro_model.water_quality import WaterQualityStream, ApparentRejectionProfile


def test_two_stage_concentrate_staging_balance():
    """
    Verify 2-Stage Industrial RO System with concentrate staging (2:1 stage ratio):
    - Stage 1: 4 parallel vessels (3 elements each = 12 elements)
    - Stage 2: 2 parallel vessels (3 elements each = 6 elements)
    - Global mass and solute conservation closure (< 1e-9 residual)
    - Combined permeate and reject relationships
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    
    stage1 = ROStage(
        name="Stage_1",
        parallel_vessels=4,
        elements_per_vessel=3,
        element_properties=props,
        element_pressure_drop_bar=0.15
    )
    stage2 = ROStage(
        name="Stage_2",
        parallel_vessels=2,
        elements_per_vessel=3,
        element_properties=props,
        element_pressure_drop_bar=0.15
    )

    system = ROSystem(
        name="Industrial_2Stage_RO",
        stages=[stage1, stage2],
        topology="concentrate_to_stage2"
    )

    feed_q_hr = 30.0
    feed_tds = 2041.0
    pressures = [18.0, 26.0]  # Stage 1: 18 bar, Stage 2: 26 bar booster

    feed_qual = WaterQualityStream(
        flow_m3_s=feed_q_hr / 3600.0,
        tds_mg_l=feed_tds,
        cod_mg_l=51.0,
        bod_mg_l=7.0,
        tss_mg_l=3.0,
        colour_pt_co=300.0,
        ph=8.0
    )

    res = system.solve(
        feed_flow_m3_hr=feed_q_hr,
        feed_tds_mg_l=feed_tds,
        stage_pressures_bar=pressures,
        temperature_celsius=25.0,
        feed_quality_stream=feed_qual
    )

    assert res.converged is True
    assert res.num_stages == 2
    assert res.total_elements == 18
    assert res.total_membrane_area_m2 == 18 * 37.0

    s1, s2 = res.stage_results

    # 1. Inter-stage stream connectivity
    assert np.isclose(s1.concentrate_flow_m3_hr, s2.feed_flow_m3_hr)
    assert np.isclose(s1.concentrate_tds_mg_l, s2.feed_tds_mg_l)

    # 2. Overall flow summations
    assert np.isclose(res.permeate_flow_m3_hr, s1.permeate_flow_m3_hr + s2.permeate_flow_m3_hr)
    assert np.isclose(res.concentrate_flow_m3_hr, s2.concentrate_flow_m3_hr)

    # 3. Mass and solute residuals across entire plant
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9
    assert np.isclose(res.water_mass_balance_error_percent, 0.0, atol=1e-6)
    assert np.isclose(res.solute_mass_balance_error_percent, 0.0, atol=1e-6)

    # 4. Global performance metrics
    expected_wr = (res.permeate_flow_m3_hr / feed_q_hr) * 100.0
    assert np.isclose(res.overall_water_recovery_percent, expected_wr)

    expected_sr = (1.0 - res.permeate_tds_mg_l / feed_tds) * 100.0
    assert np.isclose(res.overall_salt_rejection_percent, expected_sr)

    # 5. Energy
    assert res.total_electrical_power_kw > 0.0
    assert res.system_sec_kwh_per_m3 > 0.0

    # 6. Water Quality tracking
    assert res.permeate_quality is not None
    assert res.concentrate_quality is not None
    assert res.permeate_quality.cod_mg_l < feed_qual.cod_mg_l
    assert res.concentrate_quality.cod_mg_l > feed_qual.cod_mg_l


def test_permeate_staging_balance():
    """Verify 2-pass permeate staging topology mass conservation."""
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    s1 = ROStage(name="Pass_1", parallel_vessels=3, elements_per_vessel=3, element_properties=props)
    s2 = ROStage(name="Pass_2", parallel_vessels=1, elements_per_vessel=3, element_properties=props)

    sys_2pass = ROSystem(name="Two_Pass_RO", stages=[s1, s2], topology="permeate_to_stage2")
    res = sys_2pass.solve(
        feed_flow_m3_hr=20.0,
        feed_tds_mg_l=2000.0,
        stage_pressures_bar=[15.0, 12.0]
    )

    assert res.converged is True
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9


def test_max_pressure_safeguard_in_system():
    """Verify safety exception when any stage exceeds 41 bar max limit."""
    props = MembraneElementProperties(max_operating_pressure_pa=4.1e6)
    s1 = ROStage(name="S1", parallel_vessels=2, elements_per_vessel=3, element_properties=props)
    s2 = ROStage(name="S2", parallel_vessels=1, elements_per_vessel=3, element_properties=props)

    sys_inst = ROSystem(stages=[s1, s2])
    with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
        sys_inst.solve(
            feed_flow_m3_hr=20.0,
            feed_tds_mg_l=2000.0,
            stage_pressures_bar=[20.0, 42.0]  # Stage 2 > 41 bar
        )
