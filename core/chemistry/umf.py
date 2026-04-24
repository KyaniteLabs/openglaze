"""Unity Molecular Formula (UMF) calculation engine.

Converts ceramic glaze recipes into their Seger/Unity formula representation,
normalized to flux total = 1.0. Provides surface prediction and limit checking.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .materials import (
    get_material,
    OXIDE_MOLECULAR_WEIGHTS,
    FLUX_OXIDES,
)
from .parser import parse_recipe_string
from .data_loader import load_surface_thresholds, load_umf_targets

logger = logging.getLogger(__name__)


# Target formulas (guidelines, not absolute limits)
# Default: cone 10 ranges. Loaded from ceramics-foundation if available.
# Digitalfire notes these are "targets" not "limits" — many successful glazes
# fall outside these ranges. Use as starting points, not rules.
_LIMIT_FORMULAS_DEFAULT: Dict[str, tuple] = {
    'K2O': (0.0, 0.5),
    'Na2O': (0.0, 0.5),
    'KNaO': (0.1, 0.5),  # combined
    'CaO': (0.2, 0.8),
    'MgO': (0.0, 0.4),
    'BaO': (0.0, 0.3),
    'ZnO': (0.0, 0.3),
    'Al2O3': (0.2, 0.6),
    'SiO2': (2.5, 6.0),
    'B2O3': (0.0, 0.3),
}


def get_limit_formulas(cone: int = 10) -> Dict[str, tuple]:
    """Get UMF limit formulas for a specific cone.

    Loads cone-specific ranges from ceramics-foundation if available,
    otherwise falls back to default cone 10 ranges.
    """
    umf_data = load_umf_targets()
    if umf_data and 'ranges' in umf_data:
        cone_key = f'cone_{cone}'
        if cone_key in umf_data['ranges']:
            cone_ranges = umf_data['ranges'][cone_key]
            formulas = {}
            for oxide, bounds in cone_ranges.items():
                if isinstance(bounds, dict) and 'min' in bounds and 'max' in bounds:
                    formulas[oxide] = (bounds['min'], bounds['max'])
            if formulas:
                return formulas
    return dict(_LIMIT_FORMULAS_DEFAULT)


# Legacy name for backward compatibility
LIMIT_FORMULAS = _LIMIT_FORMULAS_DEFAULT


@dataclass
class UMFResult:
    """Result of a UMF calculation."""
    success: bool
    recipe_parsed: bool = False
    umf_formula: Optional[Dict[str, float]] = None
    raw_moles: Optional[Dict[str, float]] = None
    ratios: Dict[str, float] = field(default_factory=dict)
    surface_prediction: Optional[str] = None
    limit_warnings: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        result = {
            'success': self.success,
            'recipe_parsed': self.recipe_parsed,
            'umf_formula': self.umf_formula,
            'ratios': self.ratios,
            'surface_prediction': self.surface_prediction,
            'limit_warnings': self.limit_warnings,
            'warnings': self.warnings,
            'error': self.error,
        }
        return result

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return bool(self.limit_warnings) or bool(self.warnings)


class UMFAnalyzer:
    """Calculate Unity Molecular Formula from glaze recipes."""

    def calculate(self, recipe_string: str) -> UMFResult:
        """Calculate UMF from a recipe string.

        Args:
            recipe_string: Recipe like "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12"

        Returns:
            UMFResult with formula, ratios, surface prediction, and limit warnings.
        """
        # Step 1: Parse the recipe
        parse_result = parse_recipe_string(recipe_string)

        if not parse_result.success:
            return UMFResult(
                success=False,
                recipe_parsed=False,
                error=f'Could not parse recipe: {"; ".join(parse_result.errors)}',
                warnings=parse_result.errors,
            )

        # Step 2: Calculate oxide moles from materials
        try:
            moles = self._calculate_moles(parse_result.materials)
        except Exception as e:
            return UMFResult(
                success=False,
                recipe_parsed=True,
                error=f'Mole calculation failed: {e}',
            )

        if not moles:
            return UMFResult(
                success=False,
                recipe_parsed=True,
                error='No oxide moles could be calculated',
            )

        # Step 3: Normalize to flux sum = 1.0
        umf = self._normalize_to_fluxes(moles)
        if umf is None:
            return UMFResult(
                success=False,
                recipe_parsed=True,
                error='No flux oxides found — cannot normalize to UMF',
            )

        # Step 4: Calculate useful ratios
        ratios = self._calculate_ratios(umf)

        # Step 5: Predict surface character
        surface = self._predict_surface(ratios)

        # Step 6: Check against limit formulas
        warnings = self._check_limits(umf)

        extra_warnings = []
        if parse_result.normalized:
            extra_warnings.append('Recipe percentages were normalized to sum to 100')

        return UMFResult(
            success=True,
            recipe_parsed=True,
            umf_formula=umf,
            raw_moles=moles,
            ratios=ratios,
            surface_prediction=surface,
            limit_warnings=warnings,
            warnings=extra_warnings,
        )

    def _calculate_moles(self, materials: Dict[str, float]) -> Dict[str, float]:
        """Convert materials to oxide molar amounts.

        For each material: apply LOI, compute oxide mass contribution,
        divide by molecular weight to get moles.
        """
        moles: Dict[str, float] = {}

        for material_name, amount in materials.items():
            material = get_material(material_name)
            if material is None:
                logger.warning(f'Material not found during mole calc: {material_name}')
                continue

            # Effective amount after LOI
            effective_amount = amount * (1.0 - material.loi / 100.0)

            for oxide, percentage in material.oxides.items():
                if oxide not in OXIDE_MOLECULAR_WEIGHTS:
                    logger.debug(f'No molecular weight for oxide: {oxide}')
                    continue

                oxide_mass = effective_amount * (percentage / 100.0)
                oxide_moles = oxide_mass / OXIDE_MOLECULAR_WEIGHTS[oxide]

                moles[oxide] = moles.get(oxide, 0.0) + oxide_moles

        return moles

    def _normalize_to_fluxes(self, moles: Dict[str, float]) -> Optional[Dict[str, float]]:
        """Normalize oxide moles so flux total = 1.0.

        Returns None if no flux oxides are present.
        """
        flux_total = 0.0
        for oxide in FLUX_OXIDES:
            flux_total += moles.get(oxide, 0.0)

        if flux_total == 0:
            return None

        normalized = {}
        for oxide, value in moles.items():
            normalized[oxide] = round(value / flux_total, 4)

        return normalized

    def _calculate_ratios(self, umf: Dict[str, float]) -> Dict[str, float]:
        """Calculate useful ratios from the UMF formula."""
        ratios = {}

        sio2 = umf.get('SiO2', 0)
        al2o3 = umf.get('Al2O3', 0)
        cao = umf.get('CaO', 0)
        k2o = umf.get('K2O', 0)
        na2o = umf.get('Na2O', 0)
        mgo = umf.get('MgO', 0)

        # SiO2:Al2O3 ratio (the most important in glaze chemistry)
        if al2o3 > 0:
            ratios['sio2_al2o3'] = round(sio2 / al2o3, 2)
        else:
            ratios['sio2_al2o3'] = 0.0

        # Flux:Al2O3 ratio
        if al2o3 > 0:
            ratios['flux_al2o3'] = round(1.0 / al2o3, 2)  # flux sum is always 1.0
        else:
            ratios['flux_al2o3'] = 0.0

        # KNaO:CaO ratio
        knao = k2o + na2o
        if cao > 0:
            ratios['knao_cao'] = round(knao / cao, 2)
        else:
            ratios['knao_cao'] = 0.0 if knao == 0 else 99.0

        # Total flux diversity
        flux_count = sum(1 for ox in FLUX_OXIDES if umf.get(ox, 0) > 0.01)
        ratios['flux_diversity'] = flux_count

        # Alumina:Silica ratio (inverse, useful for mattness)
        if sio2 > 0:
            ratios['al2o3_sio2'] = round(al2o3 / sio2, 3)

        return ratios

    def _predict_surface(self, ratios: Dict[str, float]) -> str:
        """Predict surface character from UMF ratios.

        Based on Stull chart (1912) as implemented on Glazy.org:
        - Matte: SiO2:Al2O3 < 4
        - Semi-matte (satin): SiO2:Al2O3 ~4-5
        - Glossy: SiO2:Al2O3 > 5
        - High CaO promotes glossy surfaces
        - High MgO can promote matte surfaces
        - High B2O3 promotes fluid, glossy surfaces

        Thresholds loaded from ceramics-foundation/data/surface-prediction.json if available.
        """
        sio2_al2o3 = ratios.get('sio2_al2o3', 0)

        # Load thresholds from external data, fall back to Stull defaults
        thresholds = load_surface_thresholds()
        if thresholds:
            t_glossy = thresholds.get('glossy', 5)
            t_satin = thresholds.get('satin', 4)
        else:
            t_glossy, t_satin = 5, 4

        if sio2_al2o3 >= t_glossy:
            return 'glossy'
        elif sio2_al2o3 >= t_satin:
            return 'satin'
        elif sio2_al2o3 > 0:
            return 'matte'
        else:
            return 'dry_underfired'

    def _check_limits(self, umf: Dict[str, float]) -> List[str]:
        """Check UMF values against target formula guidelines.

        Note: these are guidelines based on common stoneware ranges, not absolute
        limits. Many successful glazes fall outside these ranges.
        """
        warnings = []

        # Check individual oxides
        for oxide, (lo, hi) in LIMIT_FORMULAS.items():
            if oxide == 'KNaO':
                # Combined alkali check
                value = umf.get('K2O', 0) + umf.get('Na2O', 0)
            else:
                value = umf.get(oxide, 0)

            if value > 0 and value < lo:
                warnings.append(f'{oxide} ({value:.2f}) is below typical range ({lo}-{hi}) — guideline only')
            elif value > hi:
                warnings.append(f'{oxide} ({value:.2f}) exceeds typical range ({lo}-{hi}) — guideline only')

        # Additional practical checks
        sio2 = umf.get('SiO2', 0)
        if sio2 > 6.0:
            warnings.append(f'Very high SiO2 ({sio2:.2f}) — glaze may be stiff or underfired at normal temperatures')

        al2o3 = umf.get('Al2O3', 0)
        if al2o3 > 0.6:
            warnings.append(f'High Al2O3 ({al2o3:.2f}) — glaze may be matte or underfired')

        b2o3 = umf.get('B2O3', 0)
        if b2o3 > 0.3:
            warnings.append(f'High B2O3 ({b2o3:.2f}) — glaze may be very fluid at cone 10')

        return warnings


# Module-level convenience function
_analyzer = UMFAnalyzer()


def calculate_umf(recipe: str) -> UMFResult:
    """Calculate UMF from a recipe string using the default analyzer."""
    return _analyzer.calculate(recipe)
