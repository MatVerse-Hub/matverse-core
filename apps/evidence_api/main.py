"""FastAPI service exposing the Evidence endpoint for MatVerse."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .coherence_engine import (
    LAMBDA_SOVEREIGN,
    PSI_ETHICAL_THRESHOLD,
    CoherenceBreakdown,
    CoherenceEngine,
)

app = FastAPI(
    title="MatVerse-Core Evidence API",
    description=(
        "Endpoints de Prova Computacional Quântica usando a Métrica de Coerência "
        "Semântica Quântica Invariante (M-CSQI)."
    ),
)


class EvidenceRequest(BaseModel):
    """Entrada da intenção do usuário e seu vetor semântico."""

    intent: str = Field(..., description="Intenção declarada pelo usuário.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados opcionais da Evidence Note."
    )
    intent_vector: List[float] = Field(
        ..., description="Vetor semântico normalizado representando ρ_int."
    )


class EvidenceNote(BaseModel):
    """Estrutura de resposta para a Evidence Note registrada."""

    timestamp: float
    hash_sha256: str
    psi_index: float
    fidelity: float
    entropy_penalty: float
    lambda_sovereign: float
    status: str
    message: str


# --- Simulação do estado externo de coerência (ρ_ext) ---
EXTERNAL_COHERENCE_VECTOR = np.array([0.92, 0.15, 0.60, 0.88, 0.05], dtype=float)
EXTERNAL_COHERENCE_VECTOR = EXTERNAL_COHERENCE_VECTOR / np.linalg.norm(
    EXTERNAL_COHERENCE_VECTOR
)
VECTOR_DIMENSION = EXTERNAL_COHERENCE_VECTOR.size


def _normalize_vector(raw_vector: List[float]) -> np.ndarray:
    """Normalize the incoming intent vector and validate its dimensionality."""

    if len(raw_vector) != VECTOR_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=f"Dimensão do intent_vector incorreta. Esperado: {VECTOR_DIMENSION}",
        )

    vector = np.array(raw_vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise HTTPException(
            status_code=400, detail="O intent_vector não pode ser o vetor nulo."
        )
    return vector / norm


@app.post("/evidence", response_model=EvidenceNote)
async def create_evidence(request: EvidenceRequest) -> EvidenceNote:
    """Gera uma Evidence Note calculando o Ψ-Index em tempo real."""

    rho_int = _normalize_vector(request.intent_vector)
    breakdown, status = CoherenceEngine.evaluate(rho_int, EXTERNAL_COHERENCE_VECTOR)

    raw_data = f"{request.intent}{time.time()}{breakdown.psi_index}"
    hash_value = hashlib.sha256(raw_data.encode()).hexdigest()

    return EvidenceNote(
        timestamp=time.time(),
        hash_sha256=hash_value,
        psi_index=breakdown.psi_index,
        fidelity=breakdown.fidelity,
        entropy_penalty=breakdown.entropy_penalty,
        lambda_sovereign=LAMBDA_SOVEREIGN,
        status=status,
        message=(
            "Evidence Note registrada com a Métrica de Coerência Semântica "
            "Quântica Invariante."
        ),
    )


@app.get("/health")
async def healthcheck() -> Dict[str, Any]:
    """Retorna informações básicas sobre o serviço e a dimensão semântica."""

    return {
        "status": "ok",
        "lambda": LAMBDA_SOVEREIGN,
        "psi_threshold": PSI_ETHICAL_THRESHOLD,
        "vector_dimension": VECTOR_DIMENSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
