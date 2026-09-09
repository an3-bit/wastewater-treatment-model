"""
Stage 3 Data Generation Package.

Provides Latin Hypercube Sampling, simulation batch execution,
failure classification, quality control, and dataset export tools.
"""

from data_generation.sampling import (
    LatinHypercubeSampler,
    generate_ood_samples,
    OperatingDomainBounds,
    OODDomainBounds,
    FEATURE_ROLES,
    NON_CAUSAL_FEATURES,
)
from data_generation.feasibility import (
    FailureCategory,
    classify_simulation_failure,
)
from data_generation.quality_control import (
    QualityFlag,
    verify_scenario_quality,
)
from data_generation.simulator_runner import (
    create_baseline_system,
    run_single_simulation,
)
from data_generation.dataset import (
    generate_batch_dataset,
    assign_dataset_splits,
    save_stage3_datasets,
)
from data_generation.curation import (
    OperatingClassification,
    OODClassification,
    classify_scenario,
    compute_safeguard_sensitivities,
    compute_recovery_bands,
    curate_stage3_datasets,
)

__all__ = [
    "LatinHypercubeSampler",
    "generate_ood_samples",
    "OperatingDomainBounds",
    "OODDomainBounds",
    "FEATURE_ROLES",
    "NON_CAUSAL_FEATURES",
    "FailureCategory",
    "classify_simulation_failure",
    "QualityFlag",
    "verify_scenario_quality",
    "create_baseline_system",
    "run_single_simulation",
    "generate_batch_dataset",
    "assign_dataset_splits",
    "save_stage3_datasets",
    "OperatingClassification",
    "OODClassification",
    "classify_scenario",
    "compute_safeguard_sensitivities",
    "compute_recovery_bands",
    "curate_stage3_datasets",
]
