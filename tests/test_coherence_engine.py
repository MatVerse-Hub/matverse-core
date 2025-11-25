import numpy as np

from apps.evidence_api.coherence_engine import CoherenceEngine, LAMBDA_SOVEREIGN


def test_coherence_engine_coherent_vector():
    external = np.array([0.92, 0.15, 0.60, 0.88, 0.05], dtype=float)
    external = external / np.linalg.norm(external)
    breakdown, status = CoherenceEngine.evaluate(external, external)

    assert breakdown.fidelity == 1.0
    assert breakdown.entropy_penalty == 0.0
    assert breakdown.psi_index == 1.0
    assert status.startswith("COERENTE")


def test_coherence_engine_penalizes_divergence():
    external = np.array([0.92, 0.15, 0.60, 0.88, 0.05], dtype=float)
    external = external / np.linalg.norm(external)
    intent = np.array([-0.92, -0.15, -0.60, -0.88, -0.05], dtype=float)
    intent = intent / np.linalg.norm(intent)

    breakdown, _ = CoherenceEngine.evaluate(intent, external)

    assert breakdown.fidelity < 0.1
    assert breakdown.entropy_penalty > 0.5
    assert breakdown.psi_index <= breakdown.fidelity + LAMBDA_SOVEREIGN
