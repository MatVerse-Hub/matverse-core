"""Testes mínimos para o CoherenceEngine.

Garantem que:
- Ψ está sempre em [0, 1];
- Coerência máxima (ρ_int = ρ_ext) produz Ψ alto;
- Incoerência forte reduz Ψ.
"""

import numpy as np

from apps.evidence_api.coherence_engine import CoherenceEngine, LAMBDA_SOVEREIGN


def test_psi_range_between_zero_and_one() -> None:
    ext = np.array([1.0, 0.0, 0.0])
    intent = np.array([0.5, 0.5, 0.0])

    psi = CoherenceEngine.calculate_psi_index(intent, ext, LAMBDA_SOVEREIGN)

    assert 0.0 <= psi <= 1.0


def test_psi_is_high_for_identical_vectors() -> None:
    vec = np.array([0.3, 0.4, 0.5])

    psi = CoherenceEngine.calculate_psi_index(vec, vec, LAMBDA_SOVEREIGN)

    # Não precisa ser 1.0 exato, mas deve ser bem alto
    assert psi > 0.95


def test_psi_is_lower_for_orthogonal_vectors() -> None:
    ext = np.array([1.0, 0.0])
    intent = np.array([0.0, 1.0])

    psi = CoherenceEngine.calculate_psi_index(intent, ext, LAMBDA_SOVEREIGN)

    # Coerência quase zero + penalidade -> Ψ bem baixo
    assert psi < 0.2


def test_mismatched_dimensions_raise_value_error() -> None:
    ext = np.array([1.0, 0.0])
    intent = np.array([0.5, 0.5, 0.5])

    try:
        CoherenceEngine.calculate_psi_index(intent, ext, LAMBDA_SOVEREIGN)
    except ValueError as exc:  # pragma: no cover - simple guard
        assert "mesma dimensão" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Esperava ValueError para vetores de tamanhos diferentes")


def test_empty_vectors_raise_value_error() -> None:
    ext = np.array([])
    intent = np.array([])

    try:
        CoherenceEngine.calculate_psi_index(intent, ext, LAMBDA_SOVEREIGN)
    except ValueError as exc:  # pragma: no cover
        assert "não podem ser vazios" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Esperava ValueError para vetores vazios")
