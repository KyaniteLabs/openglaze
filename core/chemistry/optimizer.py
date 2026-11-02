"""Recipe optimizer — compute recipe tweaks to hit target properties.

The goal is to eliminate guesswork and reduce the number of physical test
firings. Instead of a potter firing 3-4 test tiles to find the right silica
addition, the optimizer computes it.

Targets:
    - target_cte: float          → exact CTE match (e.g., 6.5)
    - reduce_cte / increase_cte  → direction-only
    - more_matte / more_glossy   → surface adjustment
    - reduce_alkali              → lower KNaO for durability
    - reduce_running             → higher SiO2:Al2O3 or lower B2O3

Strategy:
    Grid-search material percentage adjustments (±5/10/15%).
    Rank by: (1) achieves target, (2) minimal change from original,
    (3) recipe stays balanced (sums ~100%).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .parser import parse_recipe_string
from .umf import calculate_umf, UMFResult
from .materials import get_material


@dataclass
class RecipeSuggestion:
    """A single optimized recipe suggestion."""

    recipe: str
    change_description: str
    predicted_umf: Dict
    predicted_cte: float
    predicted_surface: str
    score: float  # 0-100, higher = closer to target
    distance_from_target: float


@dataclass
class OptimizationResult:
    """Result of recipe optimization."""

    success: bool
    original_recipe: str
    target: str
    original_cte: Optional[float]
    original_surface: Optional[str]
    suggestions: List[RecipeSuggestion]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "original_recipe": self.original_recipe,
            "target": self.target,
            "original_cte": self.original_cte,
            "original_surface": self.original_surface,
            "suggestions": [
                {
                    "recipe": s.recipe,
                    "change_description": s.change_description,
                    "predicted_cte": s.predicted_cte,
                    "predicted_surface": s.predicted_surface,
                    "score": s.score,
                    "distance_from_target": s.distance_from_target,
                }
                for s in self.suggestions
            ],
            "error": self.error,
        }


class RecipeOptimizer:
    """Optimize glaze recipes to hit target properties with minimal changes."""

    # Common tweaks that potters use in practice
    STANDARD_ADJUSTMENTS = [-15, -10, -5, 5, 10, 15]
    LARGE_ADJUSTMENTS = [-30, -20, 20, 30]  # For surface changes needing big moves

    # Known substitution pairs: (from, to, description)
    SUBSTITUTIONS = [
        (
            "nepheline syenite",
            "custer feldspar",
            "Replace high-alkali nepheline with lower-alkali feldspar",
        ),
        (
            "custer feldspar",
            "nepheline syenite",
            "Replace feldspar with nepheline for more flux",
        ),
        (
            "whiting",
            "wollastonite",
            "Replace whiting with wollastonite (adds silica, less LOI)",
        ),
        ("epk", "ball clay", "Replace kaolin with ball clay (more flux, less alumina)"),
        (
            "silica",
            "epk",
            "Replace silica with kaolin (adds alumina, lowers CTE, more matte)",
        ),
        (
            "epk",
            "silica",
            "Replace kaolin with silica (raises SiO2:Al2O3, more glossy)",
        ),
    ]

    def optimize(
        self,
        recipe: str,
        target: str,
        target_value: Optional[float] = None,
        max_suggestions: int = 5,
    ) -> OptimizationResult:
        """Optimize a recipe toward a target property.

        Args:
            recipe: Original recipe string
            target: One of 'target_cte', 'reduce_cte', 'increase_cte',
                    'more_matte', 'more_glossy', 'reduce_alkali', 'reduce_running'
            target_value: Required for 'target_cte', optional hint for others
            max_suggestions: Number of suggestions to return

        Returns:
            OptimizationResult with ranked suggestions
        """
        early, context = self._check_original(recipe, target, target_value)
        if early is not None:
            return early
        original_materials, original_umf, original_cte, original_surface = context

        evaluator = self._build_evaluator(
            target, target_value, original_cte, original_surface, original_umf
        )

        is_surface_target = target in ("more_matte", "more_glossy")
        adjustments = self.STANDARD_ADJUSTMENTS + (
            self.LARGE_ADJUSTMENTS if is_surface_target else []
        )

        candidates: List[Tuple[str, str, UMFResult, float]] = []
        candidates += self._adjustment_candidates(
            original_materials, adjustments, evaluator, original_umf.cone
        )
        candidates += self._substitution_candidates(
            original_materials, evaluator, original_umf.cone
        )
        candidates += self._addition_candidates(
            original_materials, evaluator, original_umf.cone
        )

        suggestions = self._select_suggestions(
            candidates, target, original_cte, max_suggestions
        )

        return OptimizationResult(
            success=True,
            original_recipe=recipe,
            target=target,
            original_cte=original_cte,
            original_surface=original_surface,
            suggestions=suggestions,
        )

    def _check_original(
        self, recipe: str, target: str, target_value: Optional[float]
    ) -> Tuple[Optional[OptimizationResult], tuple]:
        """Parse and vet the original recipe; returns (early-exit result, context)."""
        parse_result = parse_recipe_string(recipe)
        if not parse_result.success:
            return (
                OptimizationResult(
                    success=False,
                    original_recipe=recipe,
                    target=target,
                    original_cte=None,
                    original_surface=None,
                    suggestions=[],
                    error=f"Could not parse recipe: {parse_result.errors}",
                ),
                (None, None, None, None),
            )

        original_umf = calculate_umf(recipe)
        if not original_umf.success:
            return (
                OptimizationResult(
                    success=False,
                    original_recipe=recipe,
                    target=target,
                    original_cte=None,
                    original_surface=None,
                    suggestions=[],
                    error=f"UMF calculation failed: {original_umf.error}",
                ),
                (None, None, None, None),
            )

        original_materials = dict(parse_result.materials)
        original_cte = original_umf.thermal_expansion
        original_surface = original_umf.surface_prediction
        context = (original_materials, original_umf, original_cte, original_surface)

        # Guard: surface targets require Al2O3 in the recipe
        sio2_al2o3 = original_umf.ratios.get("sio2_al2o3", 0.0)
        if target in ("more_matte", "more_glossy", "reduce_running") and sio2_al2o3 == 0.0:
            return (
                OptimizationResult(
                    success=True,
                    original_recipe=recipe,
                    target=target,
                    original_cte=original_cte,
                    original_surface=original_surface,
                    suggestions=[],
                    error="Recipe contains no alumina (Al2O3) — surface and running-risk optimization requires a glaze with structural alumina. Add kaolin, feldspar, or ball clay.",
                ),
                context,
            )

        # Guard: already at target CTE
        if (
            target == "target_cte"
            and target_value is not None
            and original_cte is not None
            and abs(original_cte - target_value) < 0.1
        ):
            return (
                OptimizationResult(
                    success=True,
                    original_recipe=recipe,
                    target=target,
                    original_cte=original_cte,
                    original_surface=original_surface,
                    suggestions=[],
                    error=f"Recipe CTE ({original_cte:.2f}) is already within 0.1 of target ({target_value:.2f}). No adjustment needed.",
                ),
                context,
            )

        return None, context

    def _evaluated_candidate(
        self,
        new_materials: Dict[str, float],
        cone,
        evaluator,
        desc: str,
    ) -> Optional[Tuple[str, Dict[str, float], str, UMFResult, float]]:
        """Normalize a materials dict to 100%, score it, and package a candidate.

        Returns (recipe, normalized_materials, desc, umf, score) or None.
        """
        total = sum(new_materials.values())
        if total == 0:
            return None
        new_materials = {k: round(v / total * 100, 2) for k, v in new_materials.items()}

        candidate_recipe = self._materials_to_recipe(new_materials)
        candidate_umf = calculate_umf(candidate_recipe, cone=cone)
        if not candidate_umf.success:
            return None
        score, _distance = evaluator(candidate_umf)
        return (candidate_recipe, new_materials, desc, candidate_umf, score)

    def _adjustment_candidates(
        self, original_materials: Dict[str, float], adjustments, evaluator, cone
    ) -> List[Tuple[str, str, UMFResult, float]]:
        """Candidates from ±percentage tweaks to each single material."""
        candidates: List[Tuple[str, str, UMFResult, float]] = []
        for mat_name, amount in original_materials.items():
            material = get_material(mat_name)
            if not material:
                continue

            for delta in adjustments:
                new_amount = amount + delta
                if new_amount < 1:
                    continue

                new_materials = dict(original_materials)
                new_materials[mat_name] = new_amount

                candidate = self._evaluated_candidate(
                    new_materials, cone, evaluator, ""
                )
                if candidate is not None:
                    recipe, norm_materials, _desc, umf, score = candidate
                    desc = f"{material.name} {amount:.1f} → {norm_materials[mat_name]:.1f}%"
                    candidates.append((recipe, desc, umf, score))
        return candidates

    def _substitution_candidates(
        self, original_materials: Dict[str, float], evaluator, cone
    ) -> List[Tuple[str, str, UMFResult, float]]:
        """Candidates from partial swaps of known substitution pairs."""
        candidates: List[Tuple[str, str, UMFResult, float]] = []
        for from_mat, to_mat, sub_desc in self.SUBSTITUTIONS:
            if from_mat not in original_materials:
                continue

            from_amount = original_materials[from_mat]
            to_material = get_material(to_mat)
            if not to_material:
                continue

            for ratio in [0.25, 0.5, 0.75, 1.0]:
                swap_amount = from_amount * ratio
                new_materials = dict(original_materials)
                new_materials[from_mat] = from_amount - swap_amount
                # If to_mat already present, add to it; otherwise create it
                new_materials[to_mat] = new_materials.get(to_mat, 0) + swap_amount

                # Remove near-zero materials
                new_materials = {k: v for k, v in new_materials.items() if v >= 0.5}

                pct = int(ratio * 100)
                candidate = self._evaluated_candidate(
                    new_materials, cone, evaluator, f"{sub_desc} ({pct}% swap)"
                )
                if candidate is not None:
                    recipe, _norm, desc, umf, score = candidate
                    candidates.append((recipe, desc, umf, score))
        return candidates

    def _addition_candidates(
        self, original_materials: Dict[str, float], evaluator, cone
    ) -> List[Tuple[str, str, UMFResult, float]]:
        """Candidates from adding a common material that is missing."""
        candidates: List[Tuple[str, str, UMFResult, float]] = []
        common_additions = {
            "silica": "Add silica",
            "epk": "Add kaolin",
            "whiting": "Add whiting",
            "custer feldspar": "Add feldspar",
        }
        for mat_key, add_desc in common_additions.items():
            if mat_key in original_materials:
                continue
            material = get_material(mat_key)
            if not material:
                continue

            for add_pct in [5, 10, 15]:
                # Reduce all existing materials proportionally
                scale = (100 - add_pct) / 100
                new_materials = {k: v * scale for k, v in original_materials.items()}
                new_materials[mat_key] = float(add_pct)
                new_materials = {k: round(v, 2) for k, v in new_materials.items()}

                candidate = self._evaluated_candidate(
                    new_materials, cone, evaluator, f"{add_desc} {add_pct}%"
                )
                if candidate is not None:
                    recipe, _norm, desc, umf, score = candidate
                    candidates.append((recipe, desc, umf, score))
        return candidates

    def _select_suggestions(
        self,
        candidates: List[Tuple[str, str, UMFResult, float]],
        target: str,
        original_cte: Optional[float],
        max_suggestions: int,
    ) -> List[RecipeSuggestion]:
        """Rank, deduplicate, and cap the candidate list."""
        candidates.sort(key=lambda x: x[3], reverse=True)

        seen_recipes = set()
        suggestions = []
        for rec, desc, umf, score in candidates:
            # Skip candidates that don't improve toward target
            if score <= 0:
                continue

            # Deduplicate by rounding recipe to nearest 0.5%
            key = self._recipe_key(rec)
            if key in seen_recipes:
                continue
            seen_recipes.add(key)

            # Skip if change is too small (< 0.2 CTE change for CTE targets)
            if target.startswith("target_cte") and original_cte is not None:
                if abs(umf.thermal_expansion - original_cte) < 0.2:
                    continue

            if len(suggestions) >= max_suggestions:
                break

            suggestions.append(
                RecipeSuggestion(
                    recipe=rec,
                    change_description=desc,
                    predicted_umf=umf.umf_formula,
                    predicted_cte=umf.thermal_expansion,
                    predicted_surface=umf.surface_prediction,
                    score=round(score, 1),
                    distance_from_target=round(score, 3),  # reused field
                )
            )
        return suggestions

    def _build_evaluator(
        self,
        target: str,
        target_value: Optional[float],
        original_cte: Optional[float],
        original_surface: str,
        original_umf: UMFResult,
    ):
        """Build a scoring function for a given target."""
        if target in ("target_cte", "reduce_cte", "increase_cte"):
            return self._cte_evaluator(target, target_value, original_cte)
        if target in ("more_matte", "more_glossy"):
            return self._surface_evaluator(target, original_umf)
        if target in ("reduce_alkali", "reduce_running"):
            return self._alkali_running_evaluator(target, original_umf)

        def evaluator(umf: UMFResult) -> Tuple[float, float]:
            return 0.0, 999.0

        return evaluator

    @staticmethod
    def _cte_evaluator(
        target: str, target_value: Optional[float], original_cte: Optional[float]
    ):
        """Scoring for exact/directional CTE targets."""
        if target == "target_cte" and target_value is not None:

            def evaluator(umf: UMFResult) -> Tuple[float, float]:
                if umf.thermal_expansion is None:
                    return 0.0, 999.0
                distance = abs(umf.thermal_expansion - target_value)
                # Score: 100 at exact match, falls off with distance
                score = max(0, 100 - distance * 20)
                return score, distance

            return evaluator

        direction = -1 if target == "reduce_cte" else 1

        def evaluator(umf: UMFResult) -> Tuple[float, float]:
            if umf.thermal_expansion is None or original_cte is None:
                return 0.0, 999.0
            move = direction * (umf.thermal_expansion - original_cte)
            if move <= 0:
                return 0.0, 999.0
            # Score by movement amount, capped
            score = min(100, move * 25)
            return score, -move

        return evaluator

    @staticmethod
    def _surface_evaluator(target: str, original_umf: UMFResult):
        """Scoring for matte/glossy surface targets (cone-aware thresholds)."""
        sio2_al2o3 = original_umf.ratios.get("sio2_al2o3", 5.0)
        cone = original_umf.cone or 10
        if target == "more_matte":
            if cone <= 3:
                boundary = 3.0
            elif cone <= 6:
                boundary = 3.5
            else:
                boundary = 4.0

            def evaluator(umf: UMFResult) -> Tuple[float, float]:
                new_ratio = umf.ratios.get("sio2_al2o3", 5.0)
                if new_ratio >= sio2_al2o3:
                    return 0.0, 999.0
                reduction = sio2_al2o3 - new_ratio
                score = min(100, reduction * 20)
                # Huge bonus for crossing into matte territory
                if new_ratio < boundary:
                    score += 50
                return score, -reduction

            return evaluator

        if cone <= 3:
            boundary = 4.0
        elif cone <= 6:
            boundary = 4.5
        else:
            boundary = 5.0

        def evaluator(umf: UMFResult) -> Tuple[float, float]:
            new_ratio = umf.ratios.get("sio2_al2o3", 5.0)
            if new_ratio <= sio2_al2o3:
                return 0.0, 999.0
            increase = new_ratio - sio2_al2o3
            score = min(100, increase * 20)
            # Bonus for crossing into glossy territory
            if new_ratio > boundary:
                score += 50
            return score, -increase

        return evaluator

    @staticmethod
    def _alkali_running_evaluator(target: str, original_umf: UMFResult):
        """Scoring for reduce_alkali and reduce_running targets."""
        original_ratio = original_umf.ratios.get("sio2_al2o3", 5.0)
        original_knao = original_umf.umf_formula.get("K2O", 0) + original_umf.umf_formula.get(
            "Na2O", 0
        )
        original_b2o3 = original_umf.umf_formula.get("B2O3", 0)

        if target == "reduce_alkali":

            def evaluator(umf: UMFResult) -> Tuple[float, float]:
                new_knao = umf.umf_formula.get("K2O", 0) + umf.umf_formula.get(
                    "Na2O", 0
                )
                if new_knao >= original_knao:
                    return 0.0, 999.0
                reduction = original_knao - new_knao
                score = min(100, reduction * 50)
                return score, -reduction

            return evaluator

        def evaluator(umf: UMFResult) -> Tuple[float, float]:
            new_ratio = umf.ratios.get("sio2_al2o3", 5.0)
            new_b2o3 = umf.umf_formula.get("B2O3", 0)
            score = 0.0
            if new_ratio > original_ratio:
                score += (new_ratio - original_ratio) * 15
            if new_b2o3 < original_b2o3:
                score += (original_b2o3 - new_b2o3) * 30
            if score <= 0:
                return 0.0, 999.0
            return min(100, score), -score

        return evaluator

    @staticmethod
    def _materials_to_recipe(materials: Dict[str, float]) -> str:
        """Convert a materials dict to a recipe string."""
        parts = []
        for name, amount in materials.items():
            material = get_material(name)
            display_name = material.name if material else name.title()
            parts.append(f"{display_name} {amount:.2f}")
        return ", ".join(parts)

    @staticmethod
    def _recipe_key(recipe: str) -> str:
        """Generate a deduplication key for a recipe."""
        parsed = parse_recipe_string(recipe)
        if not parsed.success:
            return recipe
        items = []
        for name, amount in sorted(parsed.materials.items()):
            items.append(f"{name}:{round(amount * 2) / 2:.1f}")
        return "|".join(items)


def optimize_recipe(
    recipe: str,
    target: str,
    target_value: Optional[float] = None,
    max_suggestions: int = 5,
) -> OptimizationResult:
    """Convenience function to optimize a recipe."""
    optimizer = RecipeOptimizer()
    return optimizer.optimize(recipe, target, target_value, max_suggestions)
