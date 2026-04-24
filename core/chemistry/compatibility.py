"""Layering compatibility analysis for ceramic glaze combinations.

Analyzes whether two glazes are compatible when layered, checking for
thermal expansion mismatch, fluidity interactions, and problematic
oxide combinations.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .umf import UMFResult, calculate_umf
from .materials import THERMAL_EXPANSION_COEFFICIENTS, FLUX_OXIDES
from .data_loader import load_layering_rules

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityResult:
    """Result of compatibility analysis between two glazes."""
    success: bool
    compatible: bool = False
    score: float = 0.0  # 0-1, higher = more compatible
    risk_factors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommended_order: Optional[str] = None
    thermal_expansion_risk: str = 'unknown'
    fluidity_interaction: str = 'unknown'
    oxide_interactions: List[str] = field(default_factory=list)
    base_umf: Optional[UMFResult] = None
    top_umf: Optional[UMFResult] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            'success': self.success,
            'compatible': self.compatible,
            'score': self.score,
            'risk_factors': self.risk_factors,
            'warnings': self.warnings,
            'recommended_order': self.recommended_order,
            'thermal_expansion_risk': self.thermal_expansion_risk,
            'fluidity_interaction': self.fluidity_interaction,
            'oxide_interactions': self.oxide_interactions,
            'base_umf': self.base_umf.to_dict() if self.base_umf else None,
            'top_umf': self.top_umf.to_dict() if self.top_umf else None,
        }


# Shino glaze names (for the hard shino-over-non-shino rule)
_SHINO_NAMES_DEFAULT = {'shino', 'luster shino', "malcom's shino", 'malcoms shino'}

# Load canonical layering rules from ceramics-foundation if available
_LAYERING_RULES = load_layering_rules()
if _LAYERING_RULES and 'shino_crawl_risk' in _LAYERING_RULES:
    _SHINO_NAMES = set(_LAYERING_RULES['shino_crawl_risk']['shino_names'])
else:
    _SHINO_NAMES = _SHINO_NAMES_DEFAULT


class CompatibilityAnalyzer:
    """Analyze layering compatibility between two glazes."""

    def analyze(self, base_recipe: Optional[str], top_recipe: Optional[str],
                base_name: str = '', top_name: str = '') -> CompatibilityResult:
        """Analyze compatibility between base and top glaze recipes.

        Args:
            base_recipe: Recipe string for the base glaze (applied first).
            top_recipe: Recipe string for the top glaze (applied last).
            base_name: Name of the base glaze.
            top_name: Name of the top glaze.

        Returns:
            CompatibilityResult with score, risk factors, and recommendations.
        """
        base_name_lower = base_name.lower().strip()
        top_name_lower = top_name.lower().strip()

        # Hard rules first — these override everything
        shino_result = self._shino_check(top_name_lower, base_name_lower)
        if shino_result:
            return CompatibilityResult(
                success=True,
                compatible=False,
                score=0.0,
                risk_factors=[shino_result],
                warnings=['High crawl risk — Shino over non-Shino frequently crawls due to different thermal expansion.'],
                recommended_order=f'{base_name} over {top_name}' if self._is_shino(base_name_lower) else None,
                thermal_expansion_risk='high',
                fluidity_interaction='crawl_likely',
                oxide_interactions=[],
            )

        # Calculate UMF for both glazes
        base_umf = calculate_umf(base_recipe) if base_recipe else None
        top_umf = calculate_umf(top_recipe) if top_recipe else None

        risk_factors = []
        warnings = []
        oxide_interactions = []

        # If either recipe can't be parsed, return limited result
        if base_umf is None or not base_umf.success:
            if top_umf is None or not top_umf.success:
                return CompatibilityResult(
                    success=False,
                    compatible=None,
                    score=0.5,
                    warnings=['Neither glaze has a parseable recipe — limited analysis'],
                    base_umf=base_umf,
                    top_umf=top_umf,
                )
            warnings.append(f'Base glaze recipe not parseable — limited analysis')

        if top_umf is None or not top_umf.success:
            warnings.append(f'Top glaze recipe not parseable — limited analysis')

        # Only do full analysis if both UMFs are available
        if base_umf and base_umf.success and top_umf and top_umf.success:
            # Thermal expansion check
            thermal_risk, thermal_mismatch = self._thermal_expansion_check(base_umf, top_umf)
            if thermal_risk == 'high':
                risk_factors.append(f'High thermal expansion mismatch ({thermal_mismatch:+.2f})')
            elif thermal_risk == 'medium':
                warnings.append(f'Moderate thermal expansion mismatch ({thermal_mismatch:+.2f})')

            # Fluidity interaction check
            fluidity = self._fluidity_check(base_umf, top_umf)
            if 'crawl' in fluidity.lower():
                risk_factors.append(f'Fluidity mismatch: {fluidity}')
            elif 'stiff' in fluidity.lower():
                warnings.append(f'Fluidity interaction: {fluidity}')

            # Oxide interaction check
            oxide_interactions = self._oxide_interactions(base_umf, top_umf, base_name_lower, top_name_lower)
            for interaction in oxide_interactions:
                if any(word in interaction.lower() for word in ['fail', 'kill', 'suppress', 'destroy', 'critical']):
                    risk_factors.append(interaction)
                elif any(word in interaction.lower() for word in ['may', 'could', 'risk']):
                    warnings.append(interaction)

        # Calculate overall score
        score = self._calculate_score(
            risk_factors, warnings,
            self._thermal_expansion_check(base_umf, top_umf)[0] if base_umf and base_umf.success and top_umf and top_umf.success else 'unknown'
        )

        return CompatibilityResult(
            success=True,
            compatible=score >= 0.4,
            score=round(score, 2),
            risk_factors=risk_factors,
            warnings=warnings,
            recommended_order=None,
            thermal_expansion_risk=self._thermal_expansion_check(base_umf, top_umf)[0] if base_umf and base_umf.success and top_umf and top_umf.success else 'unknown',
            fluidity_interaction=self._fluidity_check(base_umf, top_umf) if base_umf and base_umf.success and top_umf and top_umf.success else 'unknown',
            oxide_interactions=oxide_interactions,
            base_umf=base_umf,
            top_umf=top_umf,
        )

    def _is_shino(self, name: str) -> bool:
        """Check if a glaze name indicates a shino."""
        name_clean = name.lower().strip()
        return name_clean in _SHINO_NAMES or 'shino' in name_clean

    def _shino_check(self, top_name: str, base_name: str) -> Optional[str]:
        """Shino over non-shino has high crawl risk due to different thermal expansion."""
        if self._is_shino(top_name) and not self._is_shino(base_name):
            return f'SHINO OVER NON-SHINO: {top_name} over {base_name} has high crawl risk. Consider reversing the layer order or applying very thin.'
        return None

    def _thermal_expansion_check(self, base_umf: UMFResult, top_umf: UMFResult) -> tuple:
        """Flux-based thermal expansion model.

        Only considers flux oxides for expansion since UMF normalizes to flux=1.0.
        Colorants (Fe2O3, CuO, CoO, etc.) are NOT fluxes and would distort the
        comparison if included. Thresholds are widened for cone 10 reduction where
        thermal tolerance is higher than oxidation firing.
        Returns (risk_level, mismatch_value) where mismatch is top - base.
        """
        def calc_flux_expansion(umf: UMFResult) -> float:
            if not umf.umf_formula:
                return 0.0
            expansion = 0.0
            for oxide, amount in umf.umf_formula.items():
                if oxide not in FLUX_OXIDES:
                    continue
                coeff = THERMAL_EXPANSION_COEFFICIENTS.get(oxide, 0.0)
                expansion += coeff * amount
            return expansion

        base_exp = calc_flux_expansion(base_umf)
        top_exp = calc_flux_expansion(top_umf)
        mismatch = top_exp - base_exp

        # Load thresholds from canonical layering rules, fall back to defaults
        if _LAYERING_RULES and 'thermal_expansion_mismatch' in _LAYERING_RULES:
            risk_levels = _LAYERING_RULES['thermal_expansion_mismatch']['risk_levels']
            low_threshold = 0.20
            high_threshold = 0.45
        else:
            low_threshold, high_threshold = 0.20, 0.45

        # Cone 10 reduction thresholds (wider than oxidation)
        if abs(mismatch) < low_threshold:
            return 'low', mismatch
        elif abs(mismatch) < high_threshold:
            return 'medium', mismatch
        else:
            return 'high', mismatch

    def _fluidity_check(self, base_umf: UMFResult, top_umf: UMFResult) -> str:
        """Compare SiO2:Al2O3 ratios to determine stiff/fluid interaction.

        - Fluid over stiff = crawling risk
        - Stiff over fluid = running risk
        - Similar = good interaction
        """
        base_ratio = base_umf.ratios.get('sio2_al2o3', 3.0)
        top_ratio = top_umf.ratios.get('sio2_al2o3', 3.0)

        if top_ratio > base_ratio + 2:
            return f'Top glaze is much stiffer (SiO2:Al2O3 {top_ratio:.1f}) over more fluid base ({base_ratio:.1f}) — potential crawling where top is thin'
        elif top_ratio < base_ratio - 2:
            return f'Top glaze is much more fluid (SiO2:Al2O3 {top_ratio:.1f}) over stiffer base ({base_ratio:.1f}) — top may run off edges'
        elif abs(top_ratio - base_ratio) < 1:
            return f'Similar fluidity (base {base_ratio:.1f}, top {top_ratio:.1f}) — good interaction expected'
        else:
            return f'Moderate fluidity difference (base {base_ratio:.1f}, top {top_ratio:.1f}) — acceptable'

    def _oxide_interactions(self, base_umf: UMFResult, top_umf: UMFResult,
                            base_name: str, top_name: str) -> List[str]:
        """Check for problematic oxide interactions between layers."""
        interactions = []
        base_oxides = base_umf.umf_formula or {}
        top_oxides = top_umf.umf_formula or {}

        base_fe = base_oxides.get('Fe2O3', 0)
        top_fe = top_oxides.get('Fe2O3', 0)
        base_cu = base_oxides.get('CuO', 0)
        top_cu = top_oxides.get('CuO', 0)
        base_co = base_oxides.get('CoO', 0)
        top_co = top_oxides.get('CoO', 0)
        base_mn = base_oxides.get('MnO', 0)
        top_mn = top_oxides.get('MnO', 0)
        base_zn = base_oxides.get('ZnO', 0)
        top_zn = top_oxides.get('ZnO', 0)
        base_sn = base_oxides.get('SnO2', 0)
        top_sn = top_oxides.get('SnO2', 0)
        base_cr = base_oxides.get('Cr2O3', 0)
        top_cr = top_oxides.get('Cr2O3', 0)

        # Iron suppresses copper red
        if base_fe > 0.05 and top_cu > 0.01:
            interactions.append('Iron in base layer suppresses copper red development in top layer')
        if top_fe > 0.05 and base_cu > 0.01:
            interactions.append('Iron in top layer may muddy copper colors in base layer')

        # Zinc kills chrome-tin pink
        if (base_sn > 0.02 or top_sn > 0.02) and (base_cr > 0.001 or top_cr > 0.001):
            if base_zn > 0.02 or top_zn > 0.02:
                interactions.append('Zinc present with chrome-tin pink — zinc destroys pink color development')

        # High iron stacking (too dark)
        combined_fe = base_fe + top_fe
        if combined_fe > 0.15:
            interactions.append(f'Very high combined iron ({combined_fe:.3f}) — result may be too dark/black')
        if combined_fe > 0.4:
            interactions.append(f'CRITICAL: Combined iron ({combined_fe:.3f}) exceeds practical layering threshold — expect muddy/uninteresting result')

        # Cobalt + manganese interaction
        if (base_co > 0.005 or top_co > 0.005) and (base_mn > 0.005 or top_mn > 0.005):
            interactions.append('Cobalt + manganese combination — can produce interesting purple/brown but unpredictable')

        # Chrome contamination risk
        if (base_cr > 0.001 or top_cr > 0.001):
            interactions.append('Chromium present — can migrate and discolor surrounding glazes in the kiln')

        return interactions

    def _calculate_score(self, risk_factors: List[str], warnings: List[str],
                         thermal_risk: str) -> float:
        """Calculate compatibility score from 0-1.

        Higher = more compatible. Uses weighted risk assessment.
        """
        score = 1.0

        # Risk factors are serious — each one reduces score significantly
        score -= len(risk_factors) * 0.3

        # Warnings are moderate
        score -= len(warnings) * 0.1

        # Thermal risk
        if thermal_risk == 'high':
            score -= 0.2
        elif thermal_risk == 'medium':
            score -= 0.1

        return max(0.0, min(1.0, score))
