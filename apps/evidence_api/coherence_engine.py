"""Utilities for computing MatVerse coherence metrics.

This module simulates the Metric of Invariant Quantum Semantic Coherence (M-CSQI)
using lightweight numerical operations. It exposes helpers for the Uhlmann fidelity,
a relative-entropy proxy, and a combined Ψ-Index that rewards semantic coherence and
penalizes divergence according to the sovereign constant λ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

# Civilizational constant defined by the protocol (penalty multiplier)
LAMBDA_SOVEREIGN: float = 0.27
# Ethical threshold for coherence approval (Ω-GATE)
PSI_ETHICAL_THRESHOLD: float = 0.85


@dataclass
class CoherenceBreakdown:
    """Container for the intermediate coherence calculations."""

    fidelity: float
    entropy_penalty: float
    psi_index: float


class CoherenceEngine:
    """Compute coherence measures between intent and external state vectors."""

    @staticmethod
    def uhlmann_fidelity(rho_int: np.ndarray, rho_ext: np.ndarray) -> float:
        """Approximate the Uhlmann fidelity between two density vectors.

        The formal fidelity is ``(Tr[sqrt(sqrt(ρ1) * ρ2 * sqrt(ρ1))])**2``. For a
        lightweight simulation we use cosine similarity, which is bounded between
        0 and 1 after clipping.
        """

        similarity = float(
            np.dot(rho_int, rho_ext)
            / (np.linalg.norm(rho_int) * np.linalg.norm(rho_ext))
        )
        return float(np.clip(similarity, 0.0, 1.0))

    @staticmethod
    def relative_entropy(rho_int: np.ndarray, rho_ext: np.ndarray) -> float:
        """Proxy for the relative entropy between two density vectors.

        The true quantity is ``Tr[ρ * (log ρ - log σ)]``. We approximate it with a
        smooth distance-derived penalty so callers can reason about divergence
        without heavy linear-algebra dependencies. The penalty is normalized to
        the range [0, 1).
        """

        distance = float(np.linalg.norm(rho_int - rho_ext))
        penalty_factor = 1.0 - float(np.exp(-0.5 * distance))
        return float(np.clip(penalty_factor, 0.0, 1.0))

    @classmethod
    def calculate_psi_index(
        cls, intent_vector: np.ndarray, external_vector: np.ndarray
    ) -> CoherenceBreakdown:
        """Compute the Ψ-Index via M-CSQI.

        Ψ = F(ρ_int, ρ_ext) - λ * S(ρ_int || ρ_ext)
        """

        fidelity = cls.uhlmann_fidelity(intent_vector, external_vector)
        entropy_penalty = cls.relative_entropy(intent_vector, external_vector)
        psi_index = fidelity - (LAMBDA_SOVEREIGN * entropy_penalty)
        psi_index = float(np.clip(psi_index, 0.0, 1.0))
        return CoherenceBreakdown(
            fidelity=fidelity, entropy_penalty=entropy_penalty, psi_index=psi_index
        )

    @classmethod
    def get_coherence_status(cls, psi_index: float) -> str:
        """Return a human-readable coherence classification."""

        if psi_index >= PSI_ETHICAL_THRESHOLD:
            return "COERENTE (Ω-GATE: Aprovado)"
        return "INCOERENTE (Ω-GATE: Penalidade Ativada)"

    @classmethod
    def evaluate(
        cls, intent_vector: np.ndarray, external_vector: np.ndarray
    ) -> Tuple[CoherenceBreakdown, str]:
        """Full coherence evaluation with status label."""

        breakdown = cls.calculate_psi_index(intent_vector, external_vector)
        status = cls.get_coherence_status(breakdown.psi_index)
        return breakdown, status
