"""
Stage 4: Machine Learning Surrogate Models Package.

Exports:
- PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS, PRIMARY_TARGETS, SECONDARY_TARGETS
- train_linear_regression, train_random_forest, train_xgboost, train_ann_mlp
- calculate_regression_metrics
- predict_model_targets, evaluate_model_on_dataset, evaluate_baseline_point
- Stage4Surrogate, benchmark_surrogate_speed
- compute_tree_shap_explanations, generate_shap_plots
- perform_single_variable_sweeps, check_physics_monotonicity, evaluate_mass_balance_reconstruction
"""

from ml.preprocessing import (
    PreprocessingPipeline,
    FEATURE_COLUMNS,
    ALL_TARGETS,
    PRIMARY_TARGETS,
    SECONDARY_TARGETS,
)
from ml.metrics import calculate_regression_metrics
from ml.train import (
    train_linear_regression,
    train_random_forest,
    train_xgboost,
    train_ann_mlp,
)
from ml.evaluate import (
    predict_model_targets,
    evaluate_model_on_dataset,
    evaluate_baseline_point,
)
from ml.inference import (
    Stage4Surrogate,
    benchmark_surrogate_speed,
)
from ml.interpretability import (
    compute_tree_shap_explanations,
    generate_shap_plots,
)
from ml.physics_checks import (
    perform_single_variable_sweeps,
    check_physics_monotonicity,
    evaluate_mass_balance_reconstruction,
    BASELINE_POINT,
)
from ml.domain_guard import (
    OptimizationDomainGuard,
    DomainBounds,
    DomainProximityStatus,
)
from ml.verification import (
    verify_candidate_with_mechanistic_model,
)

__all__ = [
    "PreprocessingPipeline",
    "FEATURE_COLUMNS",
    "ALL_TARGETS",
    "PRIMARY_TARGETS",
    "SECONDARY_TARGETS",
    "calculate_regression_metrics",
    "train_linear_regression",
    "train_random_forest",
    "train_xgboost",
    "train_ann_mlp",
    "predict_model_targets",
    "evaluate_model_on_dataset",
    "evaluate_baseline_point",
    "Stage4Surrogate",
    "benchmark_surrogate_speed",
    "compute_tree_shap_explanations",
    "generate_shap_plots",
    "perform_single_variable_sweeps",
    "check_physics_monotonicity",
    "evaluate_mass_balance_reconstruction",
    "BASELINE_POINT",
    "OptimizationDomainGuard",
    "DomainBounds",
    "DomainProximityStatus",
    "verify_candidate_with_mechanistic_model",
]
