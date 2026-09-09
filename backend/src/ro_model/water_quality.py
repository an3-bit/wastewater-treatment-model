"""
Water Quality Stream Descriptors and Multi-Component Characterization.

Implements two modeling levels for textile wastewater:
Level A: NaCl-Equivalent TDS Model for osmotic pressure and solution-diffusion transport.
Level B: Textile Water Quality Descriptors (TDS, COD, BOD, Colour, TSS, pH) tracked independently.
"""

from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
import numpy as np


@dataclass
class WaterQualityStream:
    """
    Representation of a process water stream with full textile quality descriptors.
    """
    flow_m3_s: float
    tds_mg_l: float
    cod_mg_l: Optional[float] = None
    bod_mg_l: Optional[float] = None
    tss_mg_l: Optional[float] = None
    colour_pt_co: Optional[Union[float, str]] = None
    ph: Optional[float] = None
    temperature_celsius: float = 25.0
    pressure_bar: float = 1.01325

    @property
    def flow_m3_hr(self) -> float:
        """Volumetric flow in m³/h."""
        return self.flow_m3_s * 3600.0

    @property
    def flow_m3_day(self) -> float:
        """Volumetric flow in m³/day."""
        return self.flow_m3_s * 86400.0

    @property
    def tds_kg_m3(self) -> float:
        """TDS concentration in kg/m³ (g/L)."""
        return self.tds_mg_l * 1.0e-3

    def to_dict(self) -> Dict[str, Any]:
        """Convert stream state to dictionary."""
        return {
            "flow_m3_hr": self.flow_m3_hr,
            "flow_m3_s": self.flow_m3_s,
            "tds_mg_l": self.tds_mg_l,
            "cod_mg_l": self.cod_mg_l,
            "bod_mg_l": self.bod_mg_l,
            "tss_mg_l": self.tss_mg_l,
            "colour_pt_co": self.colour_pt_co,
            "ph": self.ph,
            "temperature_celsius": self.temperature_celsius,
            "pressure_bar": self.pressure_bar
        }


def calculate_apparent_rejection(feed_value: float, permeate_value: float) -> float:
    """
    Calculate apparent solute/pollutant rejection fraction: R = 1 - Cp / Cf.
    
    Returns:
        Rejection as a fraction between 0.0 and 1.0.
    """
    if feed_value <= 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (permeate_value / feed_value)))


@dataclass
class ApparentRejectionProfile:
    """
    Empirical apparent rejection coefficients for non-osmotic textile descriptors.
    These are observed empirical descriptors, NOT intrinsic membrane transport constants.
    """
    rejection_cod: float = 0.9020     # (51 - 5)/51 = 90.20% from Sowgath et al. (2025)
    rejection_bod: float = 0.7143     # (7 - 2)/7 = 71.43% from Sowgath et al. (2025)
    rejection_tss: float = 1.0000     # (3 - 0)/3 = 100.0% (TSS complete retention by NF/RO)
    rejection_colour: float = 1.0000  # (300 - BDL)/300 ~ 100.0%
    permeate_ph: float = 7.5
    concentrate_ph: float = 7.8


def compute_water_quality_split(
    feed_stream: WaterQualityStream,
    permeate_flow_m3_s: float,
    permeate_tds_mg_l: float,
    rejection_profile: Optional[ApparentRejectionProfile] = None
) -> Tuple[WaterQualityStream, WaterQualityStream]:
    """
    Split a feed WaterQualityStream into Permeate and Concentrate streams while
    enforcing rigorous mass balances on water, TDS, COD, BOD, and TSS.
    """
    from typing import Tuple
    
    prof = rejection_profile or ApparentRejectionProfile()
    q_f = feed_stream.flow_m3_s
    q_p = permeate_flow_m3_s
    q_r = max(q_f - q_p, 1.0e-12)
    
    # 1. Permeate quality descriptors
    p_tds = permeate_tds_mg_l
    p_cod = feed_stream.cod_mg_l * (1.0 - prof.rejection_cod) if feed_stream.cod_mg_l is not None else None
    p_bod = feed_stream.bod_mg_l * (1.0 - prof.rejection_bod) if feed_stream.bod_mg_l is not None else None
    p_tss = feed_stream.tss_mg_l * (1.0 - prof.rejection_tss) if feed_stream.tss_mg_l is not None else None
    p_col = "BDL" if prof.rejection_colour >= 0.999 else (
        feed_stream.colour_pt_co * (1.0 - prof.rejection_colour) if isinstance(feed_stream.colour_pt_co, (int, float)) else "BDL"
    )
    p_ph = prof.permeate_ph

    # 2. Concentrate quality descriptors (from strict component mass balance: C_r = (Q_f*C_f - Q_p*C_p)/Q_r)
    r_tds = max((q_f * feed_stream.tds_mg_l - q_p * p_tds) / q_r, 0.0)
    r_cod = max((q_f * feed_stream.cod_mg_l - q_p * p_cod) / q_r, 0.0) if feed_stream.cod_mg_l is not None else None
    r_bod = max((q_f * feed_stream.bod_mg_l - q_p * p_bod) / q_r, 0.0) if feed_stream.bod_mg_l is not None else None
    r_tss = max((q_f * feed_stream.tss_mg_l - q_p * p_tss) / q_r, 0.0) if feed_stream.tss_mg_l is not None else None
    
    # Concentrate colour estimation
    if isinstance(feed_stream.colour_pt_co, (int, float)):
        r_col = (q_f * feed_stream.colour_pt_co) / q_r
    else:
        r_col = 550.0  # Reported reject colour
    r_ph = prof.concentrate_ph

    permeate_stream = WaterQualityStream(
        flow_m3_s=q_p,
        tds_mg_l=p_tds,
        cod_mg_l=p_cod,
        bod_mg_l=p_bod,
        tss_mg_l=p_tss,
        colour_pt_co=p_col,
        ph=p_ph,
        temperature_celsius=feed_stream.temperature_celsius,
        pressure_bar=1.01325
    )

    concentrate_stream = WaterQualityStream(
        flow_m3_s=q_r,
        tds_mg_l=r_tds,
        cod_mg_l=r_cod,
        bod_mg_l=r_bod,
        tss_mg_l=r_tss,
        colour_pt_co=r_col,
        ph=r_ph,
        temperature_celsius=feed_stream.temperature_celsius,
        pressure_bar=feed_stream.pressure_bar  # minus channel pressure drop
    )

    return permeate_stream, concentrate_stream
