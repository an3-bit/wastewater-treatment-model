"""
Stage 6 Calibration Script: Fouling Kinetics Calibration against Literature Anchor.
"""

from pathlib import Path
import pandas as pd
import json

from fouling.calibration import calibrate_fouling_rate_constant


def run_calibration():
    print("=" * 80)
    print("STAGE 6: MEMBRANE FOULING KINETICS CALIBRATION")
    print("=" * 80)

    report = calibrate_fouling_rate_constant(
        target_decline_pct=15.0,
        target_cum_volume_l_m2=625.0,
        benchmark_recovery_pct=60.0,
        benchmark_avg_flux_lmh=32.4,
        benchmark_avg_beta=1.25,
        benchmark_feed_tds_mg_l=2041.0,
        temperature_celsius=25.0,
    )

    print(f"\n[Calibration Results]")
    print(f"  Target Permeability Decline: {report.target_permeability_decline_pct:.2f}%")
    print(f"  Achieved Permeability Decline: {report.achieved_permeability_decline_pct:.4f}%")
    print(f"  Target Specific Permeate Exposure: {report.target_cumulative_volume_l_m2:.1f} L/m2")
    print(f"  Calibrated r_spec: {report.calibrated_r_spec:.4e} m^-1 / (m^3/m^2)")
    print(f"  Intrinsic Clean Resistance (R_m): {report.r_m_clean_m_inv:.4e} m^-1")
    print(f"  Target Accumulated Fouling Resistance (R_f): {report.r_f_accumulated_m_inv:.4e} m^-1")
    print(f"  Absolute Residual Error: {report.residual_abs_error_pct:.6e}%")
    print(f"  Optimizer Method: {report.optimizer_method}")
    print(f"  Identifiability Classification: {report.identifiability_status}")

    # Save summary table
    out_dir = Path("results/stage6/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    df_calib = pd.DataFrame([{
        "parameter": "specific_fouling_resistance (r_spec)",
        "calibrated_value": report.calibrated_r_spec,
        "unit": "m^-1 / (m^3/m^2)",
        "target_decline_pct": report.target_permeability_decline_pct,
        "achieved_decline_pct": report.achieved_permeability_decline_pct,
        "target_exposure_L_m2": report.target_cumulative_volume_l_m2,
        "clean_resistance_R_m": report.r_m_clean_m_inv,
        "accumulated_R_f": report.r_f_accumulated_m_inv,
        "residual_pct": report.residual_abs_error_pct,
        "identifiability": report.identifiability_status,
    }])
    df_calib.to_csv(out_dir / "calibration_summary.csv", index=False)
    print(f"\nSaved calibration summary to: {out_dir / 'calibration_summary.csv'}")


if __name__ == "__main__":
    run_calibration()
