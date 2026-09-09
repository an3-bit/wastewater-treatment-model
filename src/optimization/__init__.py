"""
Optimization Package for Stage 5 Multi-Objective Reverse Osmosis Operating Optimization.
"""

from optimization.problem import ROOperatingOptimizationProblem
from optimization.constraints import (
    CandidateConstraintReport,
    check_candidate_constraints,
)
from optimization.pareto import (
    AUTHORITATIVE_BASELINE,
    find_non_dominated_front,
    select_knee_solution,
    select_representative_solutions,
    evaluate_baseline_dominance,
    select_distributed_pareto_candidates,
)
from optimization.nsga2_runner import (
    run_nsga2,
    run_multi_seed_study,
    HypervolumeTrackingCallback,
)
from optimization.verification import (
    verify_pareto_candidates_batch,
    analyze_surrogate_exploitation,
)
from optimization.operating_map import (
    generate_operating_grid,
    plot_operational_decision_map,
)

__all__ = [
    "ROOperatingOptimizationProblem",
    "CandidateConstraintReport",
    "check_candidate_constraints",
    "AUTHORITATIVE_BASELINE",
    "find_non_dominated_front",
    "select_knee_solution",
    "select_representative_solutions",
    "evaluate_baseline_dominance",
    "select_distributed_pareto_candidates",
    "run_nsga2",
    "run_multi_seed_study",
    "HypervolumeTrackingCallback",
    "verify_pareto_candidates_batch",
    "analyze_surrogate_exploitation",
    "generate_operating_grid",
    "plot_operational_decision_map",
]
