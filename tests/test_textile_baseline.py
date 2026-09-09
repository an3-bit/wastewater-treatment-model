"""
Integration Tests for Stage 2 Textile Wastewater Baseline Model.
"""

import pytest
import numpy as np
import yaml
from pathlib import Path

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.stage import ROStage
from ro_model.system import ROSystem
from ro_model.water_quality import WaterQualityStream, ApparentRejectionProfile


def test_textile_baseline_yaml_loading():
    """Verify loading parameters from config/textile_baseline.yaml."""
    cfg_path = Path("config/textile_baseline.yaml")
    assert cfg_path.exists()
    
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    assert cfg["water_quality_feed"]["tds_mg_l"] == 2041.0
    assert cfg["water_quality_feed"]["cod_mg_l"] == 51.0
    assert cfg["membrane_properties"]["membrane_area_m2"] == 37.0
    assert cfg["transport_parameters"]["Aw_physical_m_bar_s"] == 1.0232e-6


def test_textile_baseline_two_stage_simulation():
    """
    Run industrial textile baseline simulation under Nice Cotton MBR effluent conditions.
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    
    s1 = ROStage(name="Stage_1", parallel_vessels=4, elements_per_vessel=3, element_properties=props)
    s2 = ROStage(name="Stage_2", parallel_vessels=2, elements_per_vessel=3, element_properties=props)
    system = ROSystem(name="Textile_MBR_RO", stages=[s1, s2], topology="concentrate_to_stage2")

    feed_stream = WaterQualityStream(
        flow_m3_s=30.0 / 3600.0,
        tds_mg_l=2041.0,
        cod_mg_l=51.0,
        bod_mg_l=7.0,
        tss_mg_l=3.0,
        colour_pt_co=300.0,
        ph=8.0
    )

    res = system.solve(
        feed_flow_m3_hr=30.0,
        feed_tds_mg_l=2041.0,
        stage_pressures_bar=[18.0, 24.0],
        temperature_celsius=25.0,
        feed_quality_stream=feed_stream
    )

    assert res.converged is True
    assert res.overall_water_recovery_percent > 40.0
    assert res.overall_salt_rejection_percent > 99.0
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9
