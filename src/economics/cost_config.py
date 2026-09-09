"""
Cost Configuration and Economic Provenance Parser for Stage 8.

Loads and validates config/economics.yaml, preserving source types, reference years,
and support for partially specified/missing economic parameters.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class EconomicParameter:
    name: str
    value: Optional[float]
    unit: str
    source: str
    source_type: str  # SOURCE-BACKED, USER-SUPPLIED, SCENARIO ASSUMPTION
    reference_year: int
    notes: str
    is_available: bool = True

    @property
    def is_missing(self) -> bool:
        return self.value is None or not self.is_available


@dataclass
class EconomicConfig:
    # Operations
    operating_hours_per_year: float
    nominal_feed_flow_m3_h: float

    # Tariffs & Utilities
    water_purchase_cost_kes_m3: float
    electricity_rate_kes_kwh: float
    wastewater_discharge_cost_kes_m3: float

    # CIP & Maintenance
    cip_chemical_cost_per_event_kes: float
    cip_water_volume_m3: float
    cip_energy_kwh: float
    cip_labour_hours: float
    cip_labour_rate_kes_h: float
    cleaning_duration_hours: float
    cleaning_efficiency_nominal: float
    downtime_lost_revenue_rate_kes_h: float

    # Membrane Replacement
    membrane_element_purchase_cost_kes: float
    number_of_membrane_elements: int
    membrane_replacement_labour_kes: float
    membrane_replacement_interval_hours: float
    membrane_disposal_cost_kes: float

    # Digital Twin System
    digital_twin_implementation_capex_kes: float
    digital_twin_annual_opex_kes: float

    # Financial
    discount_rate: float
    project_lifetime_years: int

    # Raw Parameter Catalog
    raw_parameters: Dict[str, EconomicParameter]

    @classmethod
    def load_from_yaml(cls, yaml_path: Optional[Path] = None) -> "EconomicConfig":
        if yaml_path is None:
            # Default to config/economics.yaml relative to project root
            project_root = Path(__file__).resolve().parent.parent.parent
            yaml_path = project_root / "config" / "economics.yaml"

        if not yaml_path.exists():
            raise FileNotFoundError(f"Economics config file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        raw_params: Dict[str, EconomicParameter] = {}

        def parse_param(section: str, key: str, default_val: float) -> float:
            sec_data = data.get(section, {})
            p_data = sec_data.get(key, {})
            val = p_data.get("value")
            param = EconomicParameter(
                name=f"{section}.{key}",
                value=float(val) if val is not None else None,
                unit=p_data.get("unit", ""),
                source=p_data.get("source", "Unspecified"),
                source_type=p_data.get("source_type", "SCENARIO ASSUMPTION"),
                reference_year=int(p_data.get("reference_year", 2024)),
                notes=p_data.get("notes", ""),
                is_available=val is not None,
            )
            raw_params[param.name] = param
            return float(val) if val is not None else default_val

        return cls(
            operating_hours_per_year=parse_param("plant_operations", "operating_hours_per_year", 8000.0),
            nominal_feed_flow_m3_h=parse_param("plant_operations", "nominal_feed_flow_m3_h", 30.0),
            water_purchase_cost_kes_m3=parse_param("tariffs_and_utilities", "water_purchase_cost", 93.0),
            electricity_rate_kes_kwh=parse_param("tariffs_and_utilities", "electricity_energy_rate", 13.74),
            wastewater_discharge_cost_kes_m3=parse_param("tariffs_and_utilities", "wastewater_discharge_cost", 35.0),
            cip_chemical_cost_per_event_kes=parse_param("cleaning_and_maintenance", "cip_chemical_cost_per_event", 4500.0),
            cip_water_volume_m3=parse_param("cleaning_and_maintenance", "cip_water_volume_m3", 3.5),
            cip_energy_kwh=parse_param("cleaning_and_maintenance", "cip_energy_kwh", 12.0),
            cip_labour_hours=parse_param("cleaning_and_maintenance", "cip_labour_hours", 2.0),
            cip_labour_rate_kes_h=parse_param("cleaning_and_maintenance", "cip_labour_rate_kes_h", 650.0),
            cleaning_duration_hours=parse_param("cleaning_and_maintenance", "cleaning_duration_hours", 4.0),
            cleaning_efficiency_nominal=parse_param("cleaning_and_maintenance", "cleaning_efficiency_nominal", 0.90),
            downtime_lost_revenue_rate_kes_h=parse_param("cleaning_and_maintenance", "downtime_lost_revenue_rate_kes_h", 850.0),
            membrane_element_purchase_cost_kes=parse_param("membrane_capital_and_replacement", "membrane_element_purchase_cost", 45000.0),
            number_of_membrane_elements=int(parse_param("membrane_capital_and_replacement", "number_of_membrane_elements", 15.0)),
            membrane_replacement_labour_kes=parse_param("membrane_capital_and_replacement", "membrane_replacement_labour_kes", 15000.0),
            membrane_replacement_interval_hours=parse_param("membrane_capital_and_replacement", "membrane_replacement_interval_hours", 24000.0),
            membrane_disposal_cost_kes=parse_param("membrane_capital_and_replacement", "membrane_disposal_cost_kes", 1500.0),
            digital_twin_implementation_capex_kes=parse_param("digital_twin_system", "digital_twin_implementation_capex", 1200000.0),
            digital_twin_annual_opex_kes=parse_param("digital_twin_system", "digital_twin_annual_opex", 250000.0),
            discount_rate=parse_param("financial_discounting", "discount_rate", 0.08),
            project_lifetime_years=int(parse_param("financial_discounting", "project_lifetime_years", 5.0)),
            raw_parameters=raw_params,
        )


def load_economics_config(yaml_path: Optional[Path] = None) -> EconomicConfig:
    return EconomicConfig.load_from_yaml(yaml_path)
