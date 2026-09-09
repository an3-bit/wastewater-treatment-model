"""
NSGA-II Multi-Objective Optimization Runner and Multi-Seed Convergence Engine.

Implements:
1. Standardized NSGA-II execution with pymoo (population=100, generations=200, ~20,000 evals).
2. Multi-seed convergence analysis (5 independent seeds) tracking Hypervolume trajectories.
3. Constraint violation filtering and non-dominated sorting.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from pathlib import Path
import time
import numpy as np
import pandas as pd

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.optimize import minimize
from pymoo.indicators.hv import Hypervolume
from pymoo.core.callback import Callback

from optimization.problem import ROOperatingOptimizationProblem
from optimization.pareto import find_non_dominated_front


class HypervolumeTrackingCallback(Callback):
    """Callback to track Hypervolume at each generation during NSGA-II execution."""
    def __init__(self, ref_point: np.ndarray):
        super().__init__()
        self.ref_point = ref_point
        self.hv_indicator = Hypervolume(ref_point=ref_point)
        self.generations = []
        self.hypervolumes = []
        self.n_feasible = []

    def notify(self, algorithm):
        gen = algorithm.n_gen
        pop = algorithm.pop
        feas_arr = pop.get("feasible")
        if feas_arr is not None:
            feas_idx = np.squeeze(feas_arr)
            F = pop.get("F")
            if F is not None and np.any(feas_idx):
                F_feas = F[feas_idx]
                if F_feas.ndim == 1:
                    F_feas = F_feas.reshape(1, -1)
                is_valid = np.all(F_feas <= self.ref_point, axis=1)
                if np.any(is_valid):
                    val = float(self.hv_indicator(F_feas[is_valid]))
                else:
                    val = 0.0
                n_feas = int(np.sum(feas_idx))
            else:
                val = 0.0
                n_feas = 0
        else:
            val = 0.0
            n_feas = 0

        self.generations.append(gen)
        self.hypervolumes.append(float(val))
        self.n_feasible.append(int(n_feas))


def run_nsga2(
    problem: ROOperatingOptimizationProblem,
    pop_size: int = 100,
    n_gen: int = 200,
    seed: int = 42,
    crossover_prob: float = 0.9,
    crossover_eta: float = 15.0,
    mutation_eta: float = 20.0,
    ref_point: np.ndarray = np.array([0.0, 2.0, 35.0]),
) -> Dict[str, Any]:
    """
    Execute a single NSGA-II optimization run.
    """
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=crossover_prob, eta=crossover_eta),
        mutation=PM(eta=mutation_eta),
        eliminate_duplicates=True,
    )

    cb = HypervolumeTrackingCallback(ref_point=ref_point)

    t0 = time.perf_counter()
    res = minimize(
        problem,
        algorithm,
        ("n_gen", n_gen),
        seed=seed,
        callback=cb,
        verbose=False,
    )
    t_elapsed = time.perf_counter() - t0

    # Extract all feasible solutions from final population
    if res.X is not None and len(res.X) > 0:
        p1_opt = res.X[:, 0]
        p2_opt = res.X[:, 1]
        df_opt_full = problem.evaluate_full_state(p1_opt, p2_opt)
        df_pareto = find_non_dominated_front(df_opt_full)
    else:
        df_pareto = pd.DataFrame()

    final_hv = cb.hypervolumes[-1] if cb.hypervolumes else 0.0

    return {
        "seed": seed,
        "elapsed_seconds": t_elapsed,
        "n_evaluations": int(pop_size * (n_gen + 1)),
        "final_hypervolume": final_hv,
        "hypervolume_history": cb.hypervolumes,
        "generations": cb.generations,
        "n_feasible_history": cb.n_feasible,
        "pareto_front": df_pareto,
        "algorithm_settings": {
            "pop_size": pop_size,
            "n_gen": n_gen,
            "crossover_prob": crossover_prob,
            "crossover_eta": crossover_eta,
            "mutation_eta": mutation_eta,
            "ref_point": ref_point.tolist(),
        },
    }


def run_multi_seed_study(
    problem_factory: Callable[[], ROOperatingOptimizationProblem],
    seeds: List[int] = (42, 101, 2024, 777, 999),
    pop_size: int = 100,
    n_gen: int = 200,
    ref_point: np.ndarray = np.array([0.0, 2.0, 35.0]),
) -> Dict[str, Any]:
    """
    Execute multi-seed NSGA-II convergence study across independent random seeds.
    """
    seed_results = []
    all_pareto_dfs = []

    for s in seeds:
        prob = problem_factory()
        res_s = run_nsga2(
            problem=prob,
            pop_size=pop_size,
            n_gen=n_gen,
            seed=s,
            ref_point=ref_point,
        )
        seed_results.append(res_s)
        df_p = res_s["pareto_front"].copy()
        df_p["seed"] = s
        all_pareto_dfs.append(df_p)

    # Combine all Pareto points across seeds and find the global non-dominated front
    df_combined = pd.concat(all_pareto_dfs, ignore_index=True)
    df_global_pareto = find_non_dominated_front(df_combined)

    # Summary statistics for final Hypervolume
    final_hvs = [r["final_hypervolume"] for r in seed_results]
    elapsed_times = [r["elapsed_seconds"] for r in seed_results]

    conv_summary = {
        "seeds": seeds,
        "mean_final_hv": float(np.mean(final_hvs)),
        "std_final_hv": float(np.std(final_hvs)),
        "min_final_hv": float(np.min(final_hvs)),
        "max_final_hv": float(np.max(final_hvs)),
        "mean_elapsed_seconds": float(np.mean(elapsed_times)),
        "total_pareto_solutions_global": len(df_global_pareto),
    }

    return {
        "convergence_summary": conv_summary,
        "seed_results": seed_results,
        "global_pareto_front": df_global_pareto,
    }
