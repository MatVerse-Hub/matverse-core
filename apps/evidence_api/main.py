"""FastAPI – Evidence API do MatVerse Core.

Este serviço expõe o endpoint principal:

    POST /evidence

que recebe uma intenção (texto + vetor) e devolve uma Evidence Note com:
    - hash SHA-256 do payload (PoSE/PoLE light);
    - Ψ calculado em tempo real via M-CSQI;
    - λ soberano (0.27);
    - status qualitativo do Ω-GATE.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .coherence_engine import (
    CoherenceEngine,
    LAMBDA_SOVEREIGN,
    PSI_ETHICAL_THRESHOLD,
)


app = FastAPI(
    title="MatVerse Core – Evidence API",
    description=(
        "M-CSQI engine: calcula Ψ em tempo real a partir de vetores "
        "de intenção e de realidade externa."
    ),
    version="0.1.0",
)


# -----------------
# Modelos Pydantic
# -----------------


class EvidenceRequest(BaseModel):
    """Payload básico de uma intenção a ser avaliada.

    *intent*: texto livre (para logging futuro / embeddings reais).
    *intent_vector*: vetor numérico representando ρ_int.
    """

    intent: str = Field(..., min_length=1, description="Texto bruto da intenção")
    intent_vector: List[float] = Field(
        ...,
        description="Vetor numérico representando o estado semântico da intenção.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados opcionais (origem, tags, etc.)",
    )


class EvidenceNote(BaseModel):
    """Registro mínimo de uma Evidence Note."""

    timestamp: float
    hash_sha256: str
    psi_index: float
    lambda_sovereign: float
    status: str
    message: str


# -----------------
# Estado Simbólico: ρ_ext
# -----------------

# Vetor de referência externo (ρ_ext). Em produção, isso deve ser derivado
# de embeddings dos seus DOCX / corpus. Aqui deixamos um seed estável.
_EXTERNAL_COHERENCE_VECTOR = np.array([0.92, 0.15, 0.60, 0.88, 0.05], dtype=float)
_EXTERNAL_COHERENCE_VECTOR /= np.linalg.norm(_EXTERNAL_COHERENCE_VECTOR)
_VECTOR_DIMENSION = int(_EXTERNAL_COHERENCE_VECTOR.size)


# -----------------
# Endpoints
# -----------------


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "matverse-core-evidence-api",
        "version": app.version,
        "lambda_sovereign": LAMBDA_SOVEREIGN,
        "psi_threshold": PSI_ETHICAL_THRESHOLD,
        "vector_dimension": _VECTOR_DIMENSION,
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "omega_gate": "online"}


@app.post("/evidence", response_model=EvidenceNote)
async def create_evidence(request: EvidenceRequest) -> EvidenceNote:
    """Cria uma Evidence Note com Ψ calculado via M-CSQI.

    Valida o tamanho do vetor, calcula Ψ e gera um hash estável do evento.
    """

    if len(request.intent_vector) != _VECTOR_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Dimensão inválida para intent_vector. "
                f"Esperado: `{_VECTOR_DIMENSION}`, recebido: `{len(request.intent_vector)}`."
            ),
        )

    rho_int = np.asarray(request.intent_vector, dtype=float)

    psi_value = CoherenceEngine.calculate_psi_index(
        rho_int,
        _EXTERNAL_COHERENCE_VECTOR,
        lambda_sovereign=LAMBDA_SOVEREIGN,
    )
    status = CoherenceEngine.get_coherence_status(psi_value, PSI_ETHICAL_THRESHOLD)

    now = time.time()
    raw = f"{request.intent}|{request.metadata}|{psi_value:.6f}|{now:.6f}"
    hash_value = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return EvidenceNote(
        timestamp=now,
        hash_sha256=hash_value,
        psi_index=psi_value,
        lambda_sovereign=LAMBDA_SOVEREIGN,
        status=status,
        message="Evidence Note registrada com M-CSQI.",
    )


if __name__ == "__main__":  # execução direta local
    import uvicorn

    print("--- MatVerse Core – Evidence API ---")
    print(f"λ (LAMBDA_SOVEREIGN): {LAMBDA_SOVEREIGN}")
    print(f"Ψ_threshold: {PSI_ETHICAL_THRESHOLD}")
    print(f"Dimensão vetorial: {_VECTOR_DIMENSION}")

    uvicorn.run("apps.evidence_api.main:app", host="0.0.0.0", port=8000, reload=True)
