"""Glaze defect risk assessment based on UMF analysis.

Identifies risk factors for common firing defects from chemical composition.
These are heuristic risk flags, not guarantees — actual defects depend on
firing schedule, cooling rate, application thickness, and clay body.

Always fire test tiles before production use.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .umf import UMFResult


@dataclass
class DefectRisk:
    """Risk assessment for a single potential defect."""

    defect: str
    risk: str  # 'low', 'medium', 'high'
    cause: str
    mitigation: str


@dataclass
class DefectAnalysis:
    """Complete defect risk assessment for a glaze recipe."""

    success: bool
    defects: List[DefectRisk] = field(default_factory=list)
    overall_risk: str = "unknown"
    error: Optional[str] = None
    caveat: str = (
        "Risk assessment only. Actual defects depend on firing schedule, "
        "cooling rate, application thickness, and clay body. Always fire test tiles."
    )

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "defects": [
                {
                    "defect": d.defect,
                    "risk": d.risk,
                    "cause": d.cause,
                    "mitigation": d.mitigation,
                }
                for d in self.defects
            ],
            "overall_risk": self.overall_risk,
            "error": self.error,
            "caveat": self.caveat,
        }


class DefectPredictor:
    """Assess glaze defect risk factors from UMF analysis."""

    def analyze(
        self, umf_result: UMFResult, clay_body_cte: Optional[float] = None
    ) -> DefectAnalysis:
        """Analyze a glaze for defect risk factors.

        Args:
            umf_result: UMF analysis result
            clay_body_cte: Optional CTE of the clay body (for fit prediction)

        Returns:
            DefectAnalysis with identified risk factors and mitigations.
            These are heuristic flags, not predictions. Always fire test tiles.
        """
        if not umf_result.success or not umf_result.umf_formula:
            return DefectAnalysis(success=False, error="Invalid UMF result")

        umf = umf_result.umf_formula
        ratios = umf_result.ratios
        cte = umf_result.thermal_expansion
        cone = umf_result.cone or 10

        # Order of the checks defines the order of the reported defect list.
        defects: List[DefectRisk] = []
        defects += self._crazing_risks(cte, clay_body_cte)
        defects += self._shivering_risks(cte, clay_body_cte)
        defects += self._running_risks(ratios, umf, cone)
        defects += self._crawling_risks(umf)
        defects += self._surface_and_stiffness_risks(ratios, umf, cone)
        defects += self._pinholing_and_color_risks(umf, cone)

        return DefectAnalysis(
            success=True,
            defects=defects,
            overall_risk=self._overall_risk(defects),
        )

    @staticmethod
    def _crazing_risks(cte, clay_body_cte) -> List[DefectRisk]:
        """Crazing risk: glaze CTE too high for the body."""
        if cte is None:
            return []
        if clay_body_cte is not None:
            delta = cte - clay_body_cte
            if delta > 1.5:
                return [
                    DefectRisk(
                        defect="crazing",
                        risk="high",
                        cause=(
                            f"Glaze CTE ({cte}) much higher than clay body ({clay_body_cte}). Glaze shrinks less "
                            f"than body on cooling, putting glaze in tension."
                        ),
                        mitigation=(
                            "Reduce alkali fluxes (soda ash, nepheline syenite). Add 5-10% silica. Replace some "
                            "feldspar with clay. Or switch to a higher-CTE clay body."
                        ),
                    )
                ]
            if delta > 0.5:
                return [
                    DefectRisk(
                        defect="crazing",
                        risk="medium",
                        cause=(
                            f"Glaze CTE ({cte}) higher than clay body ({clay_body_cte}). Potential crazing on "
                            f"cooling."
                        ),
                        mitigation=(
                            "Test on your clay body. If crazing occurs, add 3-5% silica or reduce nepheline "
                            "syenite by 5%."
                        ),
                    )
                ]
            return []

        # No body CTE provided — use general thresholds
        if cte > 7.5:
            return [
                DefectRisk(
                    defect="crazing",
                    risk="high",
                    cause=(
                        f"Very high CTE ({cte} ×10⁻⁶/°C). High alkali content makes glaze expand more than most "
                        f"clay bodies."
                    ),
                    mitigation=(
                        "Reduce alkali fluxes. Add 5-10% silica. Test on your specific clay body before production."
                    ),
                )
            ]
        if cte > 6.5:
            return [
                DefectRisk(
                    defect="crazing",
                    risk="medium",
                    cause=(
                        f"Above-average CTE ({cte} ×10⁻⁶/°C). May craze on low-expansion bodies like porcelain or "
                        f"some stonewares."
                    ),
                    mitigation="Test on your clay body. Consider adding 3-5% silica if crazing appears.",
                )
            ]
        return []

    @staticmethod
    def _shivering_risks(cte, clay_body_cte) -> List[DefectRisk]:
        """Shivering risk: glaze CTE too low for the body."""
        if cte is None or clay_body_cte is None:
            return []
        delta = clay_body_cte - cte
        if delta > 1.5:
            return [
                DefectRisk(
                    defect="shivering",
                    risk="high",
                    cause=(
                        f"Glaze CTE ({cte}) much lower than clay body ({clay_body_cte}). Glaze shrinks more than "
                        f"body, putting glaze in compression."
                    ),
                    mitigation=(
                        "Add 2-5% nepheline syenite or 1-2% soda ash to increase CTE. Reduce silica by 5%. Or "
                        "switch to a lower-CTE clay body."
                    ),
                )
            ]
        if delta > 0.5:
            return [
                DefectRisk(
                    defect="shivering",
                    risk="medium",
                    cause=f"Glaze CTE ({cte}) lower than clay body ({clay_body_cte}). Potential shivering on cooling.",
                    mitigation="Test on your clay body. If shivering occurs, add 2% nepheline syenite.",
                )
            ]
        return []

    @staticmethod
    def _running_risks(ratios, umf, cone) -> List[DefectRisk]:
        """Running / too-fluid risk from SiO2:Al2O3 and boron."""
        sio2_al2o3 = ratios.get("sio2_al2o3", 5.0)
        b2o3 = umf.get("B2O3", 0)
        if sio2_al2o3 < 3.0 and b2o3 > 0.2:
            return [
                DefectRisk(
                    defect="running",
                    risk="high",
                    cause=(
                        f"Very low SiO₂:Al₂O₃ ({sio2_al2o3:.2f}) combined with high B₂O₃ ({b2o3:.2f}). Glaze will "
                        f"be extremely fluid at cone {cone}."
                    ),
                    mitigation=(
                        "Add 10-15% silica or reduce boron source (frit, Gerstley borate). Apply very thinly. Use "
                        "catch plates."
                    ),
                )
            ]
        if sio2_al2o3 < 3.5:
            return [
                DefectRisk(
                    defect="running",
                    risk="medium",
                    cause=(
                        f"Low SiO₂:Al₂O₃ ({sio2_al2o3:.2f}). Glaze may run at cone {cone}, especially on "
                        f"horizontal surfaces."
                    ),
                    mitigation=(
                        "Add 5-10% silica or reduce flux content. Test on a vertical tile. Apply thinly on flat "
                        "surfaces."
                    ),
                )
            ]
        if b2o3 > 0.35:
            return [
                DefectRisk(
                    defect="running",
                    risk="medium",
                    cause=f"High B₂O₃ ({b2o3:.2f}) makes glaze very fluid at cone {cone}.",
                    mitigation=(
                        "Reduce boron source by 5-10%. Apply thinly (2 coats max). Use kiln wash and catch plates "
                        "for testing."
                    ),
                )
            ]
        return []

    @staticmethod
    def _crawling_risks(umf) -> List[DefectRisk]:
        """Crawling risk from high surface tension (MgO/ZnO)."""
        mgo = umf.get("MgO", 0)
        zno = umf.get("ZnO", 0)
        if mgo > 0.4 and zno > 0.1:
            return [
                DefectRisk(
                    defect="crawling",
                    risk="high",
                    cause=(
                        f"High MgO ({mgo:.2f}) + ZnO ({zno:.2f}) creates very high surface tension. Glaze may pull "
                        f"away from edges and thin spots."
                    ),
                    mitigation=(
                        "Reduce dolomite or talc by 5%. Ensure bisque is clean (no dust/oils). Apply base glaze "
                        "thickly (3-4 coats)."
                    ),
                )
            ]
        if mgo > 0.4:
            return [
                DefectRisk(
                    defect="crawling",
                    risk="medium",
                    cause=f"High MgO ({mgo:.2f}) increases surface tension, which can cause crawling at thin spots.",
                    mitigation=(
                        "Apply glaze thickly (3-4 coats). Ensure bisque is clean. Consider reducing dolomite by "
                        "3-5%."
                    ),
                )
            ]
        return []

    @staticmethod
    def _surface_and_stiffness_risks(ratios, umf, cone) -> List[DefectRisk]:
        """Matte-surface and underfired/stiff appearance risks."""
        risks: List[DefectRisk] = []
        sio2_al2o3 = ratios.get("sio2_al2o3", 5.0)
        if sio2_al2o3 < 4.0 and cone >= 8:
            risks.append(
                DefectRisk(
                    defect="matte_surface",
                    risk="low",
                    cause=f"Low SiO₂:Al₂O₃ ({sio2_al2o3:.2f}) at cone {cone} produces a matte or satin surface.",
                    mitigation="If glossy is desired: add 10-15% silica or reduce clay/kaolin by 5-10%.",
                )
            )

        sio2 = umf.get("SiO2", 0)
        al2o3 = umf.get("Al2O3", 0)
        if sio2 > 6.5 and al2o3 > 0.5:
            risks.append(
                DefectRisk(
                    defect="underfired_stiff",
                    risk="medium",
                    cause=(
                        f"Very high SiO₂ ({sio2:.2f}) and Al₂O₃ ({al2o3:.2f}). Glaze may be stiff or underfired at "
                        f"cone {cone}."
                    ),
                    mitigation=(
                        "Add 3-5% flux (whiting, feldspar) or fire to a higher cone. If intentional for a stiff "
                        "glaze, ensure long soak at peak."
                    ),
                )
            )
        elif sio2 > 6.0:
            risks.append(
                DefectRisk(
                    defect="underfired_stiff",
                    risk="low",
                    cause=f"High SiO₂ ({sio2:.2f}) may make glaze stiff at cone {cone}.",
                    mitigation=(
                        "If glaze appears underfired: add 2-3% whiting or feldspar. Or extend soak time at peak "
                        "temperature."
                    ),
                )
            )
        return risks

    @staticmethod
    def _pinholing_and_color_risks(umf, cone) -> List[DefectRisk]:
        """Pinholing (carbonate gases) and color-muddiness (Fe/Cu) risks."""
        risks: List[DefectRisk] = []
        cao = umf.get("CaO", 0)
        if cao > 0.7 and cone <= 6:
            risks.append(
                DefectRisk(
                    defect="pinholing",
                    risk="medium",
                    cause=(
                        f"High CaO ({cao:.2f}) suggests significant carbonate content (whiting, dolomite). CO₂ "
                        f"release at mid-range temperatures can cause pinholes."
                    ),
                    mitigation=(
                        "Fire bisque to cone 04 (not 06) to burn out more organics. Slow firing through "
                        "1000-1500°F. Add 15-30 min hold at peak. Ensure glaze is not too thin."
                    ),
                )
            )

        fe2o3 = umf.get("Fe2O3", 0)
        cuo = umf.get("CuO", 0)
        if fe2o3 > 0.05 and cuo > 0.02:
            risks.append(
                DefectRisk(
                    defect="color_muddiness",
                    risk="medium",
                    cause=(
                        f"Iron ({fe2o3:.3f}) and copper ({cuo:.3f}) together often produce brown/muddy colors "
                        f"instead of clean greens or reds."
                    ),
                    mitigation=(
                        "For clean copper green: keep iron below 1% in recipe. For copper red: ensure iron-free "
                        "base and heavy reduction."
                    ),
                )
            )
        return risks

    @staticmethod
    def _overall_risk(defects: List[DefectRisk]) -> str:
        """Highest risk level across all flagged defects."""
        risk_scores = {"low": 1, "medium": 2, "high": 3}
        if not defects:
            return "low"
        max_score = max(risk_scores.get(d.risk, 1) for d in defects)
        return {3: "high", 2: "medium", 1: "low"}[max_score]


def assess_defect_risk(
    recipe: str, cone: Optional[int] = None, clay_body_cte: Optional[float] = None
) -> DefectAnalysis:
    """Assess defect risk factors for a recipe string.

    Convenience function that calculates UMF and then analyzes for risk factors.
    These are heuristic flags, not predictions. Always fire test tiles.
    """
    from .umf import calculate_umf

    umf_result = calculate_umf(recipe, cone=cone)
    if not umf_result.success:
        return DefectAnalysis(success=False, error=umf_result.error)
    predictor = DefectPredictor()
    return predictor.analyze(umf_result, clay_body_cte=clay_body_cte)


# Backward compatibility alias
predict_defects = assess_defect_risk
