"""
Membrane Cleaning Event Architecture for Dynamic RO Operations.

Models chemical cleaning in place (CIP) events that restore membrane permeability
according to the configurable cleaning efficiency:
  R_f,new = (1 - eta_clean) * R_f,old
"""

from typing import List, Optional
from fouling.model import (
    ElementFoulingState,
    FoulingParameters,
    resistance_to_permeability,
)


def apply_cleaning_event(
    element_states: List[ElementFoulingState],
    cleaning_efficiency: float = 0.90,
    parameters: Optional[FoulingParameters] = None,
) -> List[ElementFoulingState]:
    """
    Apply a chemical cleaning event to all membrane elements.
    
    Parameters:
    - element_states: List of current 15 ElementFoulingState objects.
    - cleaning_efficiency: eta_clean in [0.0, 1.0] (fraction of Rf removed).
    - parameters: Optional FoulingParameters instance.
    
    Returns:
    - restored_states: Updated List[ElementFoulingState] with reduced Rf.
    """
    eta = max(0.0, min(1.0, float(cleaning_efficiency)))
    params = parameters or FoulingParameters.create_default()
    r_m = params.r_m_m_inv
    temp = params.temperature_celsius

    restored = []
    for st in element_states:
        old_rf = st.r_f_m_inv
        new_rf = (1.0 - eta) * old_rf
        new_r_total = r_m + new_rf
        
        new_aw = resistance_to_permeability(new_r_total, temp)
        new_perm_ratio = r_m / new_r_total
        new_decline_pct = (1.0 - new_perm_ratio) * 100.0

        new_st = ElementFoulingState(
            stage_index=st.stage_index,
            element_index=st.element_index,
            global_element_id=st.global_element_id,
            r_f_m_inv=new_rf,
            r_total_m_inv=new_r_total,
            aw_eff_m_pa_s=new_aw,
            permeability_ratio=new_perm_ratio,
            permeability_decline_pct=new_decline_pct,
            specific_cumulative_volume_m3_m2=st.specific_cumulative_volume_m3_m2,
            specific_cumulative_volume_l_m2=st.specific_cumulative_volume_l_m2,
            local_flux_lmh=st.local_flux_lmh,
            local_polarization_modulus=st.local_polarization_modulus,
            local_feed_tds_mg_l=st.local_feed_tds_mg_l,
            local_concentrate_tds_mg_l=st.local_concentrate_tds_mg_l,
            local_surface_tds_mg_l=st.local_surface_tds_mg_l,
            local_recovery_pct=st.local_recovery_pct,
        )
        restored.append(new_st)

    return restored
