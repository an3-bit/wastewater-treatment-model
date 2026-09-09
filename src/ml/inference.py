"""
Inference and Deployment Module for Stage 4 Machine-Learning Surrogates.

Provides:
1. Unified Stage4Surrogate wrapper class for fast vectorized multi-target predictions.
2. Serialization and deserialization utilities for models, scalers, and metadata.
3. Speed benchmarking utilities comparing surrogate inference vs mechanistic simulation.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json
import time
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd
import joblib

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS, PRIMARY_TARGETS, SECONDARY_TARGETS
from data_generation.simulator_runner import run_single_simulation, create_baseline_system


@dataclass
class Stage4Surrogate:
    """
    Unified container for a trained Stage 4 surrogate model family.
    Supports Linear Regression, Random Forest, XGBoost, and ANN / MLP.
    """
    model_name: str
    models: Dict[str, Any]
    pipeline: Optional[PreprocessingPipeline] = None
    is_neural_net: bool = False
    feature_names: List[str] = field(default_factory=lambda: list(FEATURE_COLUMNS))
    target_names: List[str] = field(default_factory=lambda: list(ALL_TARGETS))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def predict(
        self,
        inputs: Union[pd.DataFrame, Dict[str, Union[float, List[float]]], np.ndarray],
    ) -> pd.DataFrame:
        """
        Generate physical-scale predictions for all targets.
        Accepts DataFrame, dictionary of floats/lists, or 2D NumPy array.
        """
        if isinstance(inputs, dict):
            # Check if values are scalar
            first_val = next(iter(inputs.values()))
            if not isinstance(first_val, (list, np.ndarray, pd.Series)):
                df_in = pd.DataFrame([{k: inputs[k] for k in self.feature_names}])
            else:
                df_in = pd.DataFrame({k: inputs[k] for k in self.feature_names})
        elif isinstance(inputs, np.ndarray):
            df_in = pd.DataFrame(inputs, columns=self.feature_names)
        elif isinstance(inputs, pd.DataFrame):
            df_in = inputs[self.feature_names]
        else:
            raise TypeError(f"Unsupported input type: {type(inputs)}")

        preds = {}
        if self.is_neural_net:
            if self.pipeline is None:
                raise ValueError("PreprocessingPipeline is required for neural network predictions.")
            X_scaled = self.pipeline.transform_features(df_in)
            for tgt in self.target_names:
                p_scaled = self.models[tgt].predict(X_scaled)
                preds[tgt] = self.pipeline.inverse_transform_target(p_scaled, tgt)
        else:
            X = df_in[self.feature_names].to_numpy(dtype=float)
            for tgt in self.target_names:
                preds[tgt] = self.models[tgt].predict(X)

        return pd.DataFrame(preds, index=df_in.index)

    def predict_physics_reconstructed(
        self,
        inputs: Union[pd.DataFrame, Dict[str, Union[float, List[float]]], np.ndarray],
    ) -> pd.DataFrame:
        """
        Generate predictions using PHYSICS_RECONSTRUCTED mode:
        1. Predict recovery (R), permeate TDS (Cp), flux, SEC, max elem rec, max polarization.
        2. Reconstruct permeate flow Qp = (R/100)*Qf, reject flow Qr = Qf - Qp.
        3. Reconstruct concentrate TDS Cr_conserved = (Qf*Cf - Qp*Cp) / Qr (guaranteeing exact solute balance).
        4. Include direct ANN concentrate TDS as diagnostic_concentrate_tds_mgL and compute discrepancy %.
        """
        if isinstance(inputs, dict):
            first_val = next(iter(inputs.values()))
            if not isinstance(first_val, (list, np.ndarray, pd.Series)):
                df_in = pd.DataFrame([{k: inputs[k] for k in self.feature_names}])
            else:
                df_in = pd.DataFrame({k: inputs[k] for k in self.feature_names})
        elif isinstance(inputs, np.ndarray):
            df_in = pd.DataFrame(inputs, columns=self.feature_names)
        elif isinstance(inputs, pd.DataFrame):
            df_in = inputs[self.feature_names].copy()
        else:
            raise TypeError(f"Unsupported input type: {type(inputs)}")

        direct_df = self.predict(df_in)

        qf = df_in["feed_flow_m3h"].to_numpy(dtype=float)
        cf = df_in["feed_tds_mgL"].to_numpy(dtype=float)
        r_pct = direct_df["overall_recovery_pct"].to_numpy(dtype=float)
        cp = direct_df["permeate_tds_mgL"].to_numpy(dtype=float)
        cr_direct = direct_df["concentrate_tds_mgL"].to_numpy(dtype=float)

        # Conservation calculations
        r_frac = np.clip(r_pct / 100.0, 0.01, 0.999)
        qp = qf * r_frac
        qr = np.maximum(qf - qp, 1e-6)

        # Reconstructed concentrate TDS: Cr = (Qf*Cf - Qp*Cp) / Qr
        cr_conserved = np.maximum((qf * cf - qp * cp) / qr, 0.0)

        # Discrepancy between direct prediction and conservation reconstruction
        discrepancy_pct = np.abs(cr_direct - cr_conserved) / np.maximum(cr_conserved, 1.0) * 100.0

        recon_df = direct_df.copy()
        recon_df["permeate_flow_m3h"] = qp
        recon_df["concentrate_flow_m3h"] = qr
        recon_df["concentrate_tds_mgL"] = cr_conserved
        recon_df["diagnostic_concentrate_tds_mgL"] = cr_direct
        recon_df["concentrate_tds_discrepancy_pct"] = discrepancy_pct
        recon_df["solute_balance_error_kg_s"] = 0.0  # Exactly closed by construction

        return recon_df

    def save(self, output_dir: Union[str, Path]) -> Path:
        """
        Save all model binaries, pipeline scalers, and metadata to directory.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Save model binaries
        model_sub = out_path / self.model_name.lower().replace(" ", "_")
        model_sub.mkdir(parents=True, exist_ok=True)
        for tgt, m in self.models.items():
            joblib.dump(m, model_sub / f"{tgt}.joblib")

        # 2. Save pipeline if present
        if self.pipeline is not None:
            joblib.dump(self.pipeline, out_path / "preprocessing_pipeline.joblib")

        # 3. Save feature and target order
        with open(out_path / "feature_order.json", "w", encoding="utf-8") as f:
            json.dump(self.feature_names, f, indent=2)

        with open(out_path / "target_order.json", "w", encoding="utf-8") as f:
            json.dump(self.target_names, f, indent=2)

        # 4. Save metadata
        meta = dict(self.metadata)
        meta.update({
            "model_name": self.model_name,
            "is_neural_net": self.is_neural_net,
            "feature_names": self.feature_names,
            "target_names": self.target_names,
        })
        with open(out_path / "model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return out_path

    @classmethod
    def load(
        cls,
        model_dir: Union[str, Path],
        model_name: str,
        is_neural_net: bool = False,
    ) -> "Stage4Surrogate":
        """
        Load surrogate models and preprocessing pipeline from directory.
        """
        m_dir = Path(model_dir)
        model_sub = m_dir / model_name.lower().replace(" ", "_")

        with open(m_dir / "feature_order.json", "r", encoding="utf-8") as f:
            features = json.load(f)

        with open(m_dir / "target_order.json", "r", encoding="utf-8") as f:
            targets = json.load(f)

        meta_path = m_dir / "model_metadata.json"
        metadata = {}
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        pipeline = None
        pipe_path = m_dir / "preprocessing_pipeline.joblib"
        if pipe_path.exists():
            pipeline = joblib.load(pipe_path)

        models = {}
        for tgt in targets:
            tgt_file = model_sub / f"{tgt}.joblib"
            if tgt_file.exists():
                models[tgt] = joblib.load(tgt_file)
            else:
                raise FileNotFoundError(f"Missing model artifact: {tgt_file}")

        return cls(
            model_name=model_name,
            models=models,
            pipeline=pipeline,
            is_neural_net=is_neural_net,
            feature_names=features,
            target_names=targets,
            metadata=metadata,
        )


def benchmark_surrogate_speed(
    surrogate: Stage4Surrogate,
    df_eval_sample: pd.DataFrame,
    n_evaluations: int = 10000,
    n_mechanistic_evals: int = 50,
) -> Dict[str, Any]:
    """
    Benchmark surrogate evaluation speed against the mechanistic simulator.
    Measures evaluations/sec and calculates speedup factor.
    """
    system = create_baseline_system()
    sample_rows = df_eval_sample[FEATURE_COLUMNS].iloc[:n_mechanistic_evals].to_dict(orient="records")

    # 1. Benchmark mechanistic simulator on a subset
    t0_mech = time.perf_counter()
    for row in sample_rows:
        _ = run_single_simulation(
            feed_flow_m3h=row["feed_flow_m3h"],
            feed_tds_mgL=row["feed_tds_mgL"],
            feed_cod_mgL=row.get("feed_cod_mgL", 51.0),
            feed_pH=row.get("feed_pH", 8.0),
            temperature_C=row["temperature_C"],
            stage1_pressure_bar=row["stage1_pressure_bar"],
            stage2_pressure_bar=row["stage2_pressure_bar"],
            system=system,
        )
    t1_mech = time.perf_counter()
    mech_total_time = t1_mech - t0_mech
    mech_time_per_eval = mech_total_time / len(sample_rows)
    mech_evals_per_sec = len(sample_rows) / mech_total_time

    # 2. Replicate inputs to reach n_evaluations for surrogate vectorized inference
    n_reps = int(np.ceil(n_evaluations / len(df_eval_sample)))
    df_large = pd.concat([df_eval_sample[FEATURE_COLUMNS]] * n_reps, ignore_index=True).iloc[:n_evaluations]

    # Warmup
    _ = surrogate.predict(df_large.iloc[:100])

    # Surrogate inference benchmark
    t0_surr = time.perf_counter()
    _ = surrogate.predict(df_large)
    t1_surr = time.perf_counter()
    surr_total_time = t1_surr - t0_surr
    surr_time_per_eval = surr_total_time / n_evaluations
    surr_evals_per_sec = n_evaluations / surr_total_time

    speedup_factor = mech_time_per_eval / surr_time_per_eval

    return {
        "surrogate_model": surrogate.model_name,
        "n_evaluations": n_evaluations,
        "surrogate_total_seconds": surr_total_time,
        "surrogate_evals_per_sec": surr_evals_per_sec,
        "surrogate_ms_per_eval": surr_time_per_eval * 1000.0,
        "mechanistic_time_per_eval_ms": mech_time_per_eval * 1000.0,
        "mechanistic_evals_per_sec": mech_evals_per_sec,
        "speedup_factor": speedup_factor,
    }
