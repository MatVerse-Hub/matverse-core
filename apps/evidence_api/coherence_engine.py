"""Coherence Engine – implementação prática da M-CSQI.

Modelo utilizado:
    Ψ = F(ρ_int, ρ_ext) - λ · S(ρ_int || ρ_ext)

onde:
    F  ~ similaridade (coerência)   → usamos similaridade de cosseno.
    S  ~ penalidade entrópica       → usamos distância euclidiana normalizada.
    λ  = 0.27 (Constante Civilizacional, fixa).

Este módulo **não depende** de FastAPI: é puro Python + NumPy.
"""

from __future__ import annotations

import numpy as np

# Constante Civilizacional (Multiplicador de Landau-Entropia)
LAMBDA_SOVEREIGN: float = 0.27

# Limiar ético default para aprovação pelo Ω-GATE
PSI_ETHICAL_THRESHOLD: float = 0.85


class CoherenceEngine:
    """Motor de Coerência Semântica Quântica Invariante (M-CSQI).

    Na prática:
    - recebe dois vetores np.ndarray normalizados (ρ_int e ρ_ext);
    - calcula F (coerência) via similaridade de cosseno;
    - calcula S (penalidade entrópica) via distância euclidiana normalizada;
    - combina tudo em um Ψ ∈ [0, 1].
    """

    @staticmethod
    def _normalize(vec: np.ndarray) -> np.ndarray:
        vec = np.asarray(vec, dtype=float)
        norm = float(np.linalg.norm(vec))
        if norm == 0.0:
            # Evita divisão por zero: vetor nulo vira vetor uniforme
            return np.ones_like(vec) / np.sqrt(vec.size or 1)
        return vec / norm

    @staticmethod
    def uhlmann_fidelity(rho_int: np.ndarray, rho_ext: np.ndarray) -> float:
        """Aproximação prática da Fidelidade de Uhlmann.

        Formalmente:
            F(ρ1, ρ2) = (Tr[sqrt(sqrt(ρ1) ρ2 sqrt(ρ1))])²

        Aqui usamos similaridade de cosseno entre vetores normalizados como
        aproximação computacional simples e estável.
        """
        rho_int_n = CoherenceEngine._normalize(rho_int)
        rho_ext_n = CoherenceEngine._normalize(rho_ext)

        dot = float(np.dot(rho_int_n, rho_ext_n))
        # Clip para [0, 1] garantindo interpretação probabilística
        return float(np.clip(dot, 0.0, 1.0))

    @staticmethod
    def relative_entropy(rho_int: np.ndarray, rho_ext: np.ndarray) -> float:
        """Penalidade entrópica S(ρ_int || ρ_ext).

        Em vez da fórmula exata de entropia relativa, usamos uma métrica
        geométrica controlada:

            distance = ||ρ_int - ρ_ext||_2
            penalty  = 1 - exp(-0.5 · distance)

        Isso mantém S ∈ [0, 1) e cresce com a incoerência.
        """
        rho_int_n = CoherenceEngine._normalize(rho_int)
        rho_ext_n = CoherenceEngine._normalize(rho_ext)

        distance = float(np.linalg.norm(rho_int_n - rho_ext_n))
        penalty = 1.0 - float(np.exp(-0.5 * distance))
        # Garantia numérica
        return float(np.clip(penalty, 0.0, 1.0))

    @classmethod
    def calculate_psi_index(
        cls,
        intent_vector: np.ndarray,
        external_vector: np.ndarray,
        lambda_sovereign: float = LAMBDA_SOVEREIGN,
    ) -> float:
        """Calcula o Ψ-Index conforme M-CSQI.

        Ψ = F(ρ_int, ρ_ext) - λ · S(ρ_int || ρ_ext)
        """
        intent_arr = np.asarray(intent_vector, dtype=float)
        external_arr = np.asarray(external_vector, dtype=float)

        if intent_arr.size == 0 or external_arr.size == 0:
            raise ValueError("Os vetores ρ_int e ρ_ext não podem ser vazios.")
        if intent_arr.shape != external_arr.shape:
            raise ValueError(
                "Os vetores ρ_int e ρ_ext precisam ter a mesma dimensão "
                f"(recebido {intent_arr.shape} vs {external_arr.shape})."
            )

        fidelity = cls.uhlmann_fidelity(intent_arr, external_arr)
        entropy_penalty = cls.relative_entropy(intent_arr, external_arr)

        psi = fidelity - (lambda_sovereign * entropy_penalty)
        return float(np.clip(psi, 0.0, 1.0))

    @classmethod
    def get_coherence_status(
        cls,
        psi_index: float,
        threshold: float = PSI_ETHICAL_THRESHOLD,
    ) -> str:
        """Retorna o status qualitativo do Ω-GATE para um dado Ψ."""
        if psi_index >= threshold:
            return "COERENTE (Ω-GATE: Aprovado)"
        return "INCOERENTE (Ω-GATE: Penalidade Ativada)"


if __name__ == "__main__":  # debug rápido
    ext = np.array([0.92, 0.15, 0.60, 0.88, 0.05])
    intent = ext.copy()
    psi = CoherenceEngine.calculate_psi_index(intent, ext)
    print(f"Ψ(ext, ext) = {psi:.4f}")
