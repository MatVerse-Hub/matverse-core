# MatVerse Core – Evidence API (M-CSQI Engine)

> Kernel mínimo do MatVerse: um endpoint real que calcula Ψ em tempo real
> a partir de vetores de intenção e de realidade externa.

Este repositório entrega o **núcleo verificável** do ecossistema MatVerse/Web-X:

- Um **motor de coerência** (M-CSQI) que implementa, de forma prática, a equação:

  ```math
  \Psi = \mathcal{F}(\rho_{int}, \rho_{ext}) - \lambda \cdot S(\rho_{int} \parallel \rho_{ext})
  ```

- Uma **Evidence API** via FastAPI:
  - `POST /evidence` → gera uma *Evidence Note* com:
    - `psi_index` (Ψ),
    - `lambda_sovereign` (= 0.27),
    - `hash_sha256` do evento,
    - `status` do Ω-GATE (aprovado / penalizado).

Este é o ponto de prova: **menos narrativa, mais endpoint.**

---
## Estrutura do Projeto

```text
matverse-core/
├── .gitignore
├── README.md
├── requirements.txt
├── apps/
│   ├── __init__.py
│   └── evidence_api/
│       ├── __init__.py
│       ├── coherence_engine.py
│       └── main.py
└── tests/
    └── test_coherence_engine.py
```

- `apps/evidence_api/coherence_engine.py` – implementação do M-CSQI.
- `apps/evidence_api/main.py` – FastAPI com `/`, `/health` e `/evidence`.
- `tests/` – testes mínimos de sanidade do motor de coerência.

---
## Conceitos-Chave

### λ – Constante Civilizacional

No código, `LAMBDA_SOVEREIGN = 0.27` é o fator que penaliza a entropia
(`relative_entropy`) no cálculo de Ψ. Valores mais altos tornam o sistema
mais exigente com incoerência.

### Ψ – Índice de Coerência

O `psi_index` é o número em `[0, 1]` que resume a relação entre:

- a intenção enviada (`intent_vector`  →  ρ_int),
- o estado de referência do sistema (`ρ_ext` interno).

O Ω-GATE usa um limiar padrão `Ψ_min = 0.85`:

- `Ψ ≥ 0.85` → `COERENTE (Ω-GATE: Aprovado)`
- `Ψ < 0.85` → `INCOERENTE (Ω-GATE: Penalidade Ativada)`

---
## Como Rodar Localmente

Pré-requisitos:

- Python 3.10+
- pip disponível

```bash
# 1. Clonar o repositório
 git clone https://github.com/MatVerse-Hub/matverse-core.git
 cd matverse-core

# 2. Criar ambiente virtual (opcional, mas recomendado)
 python -m venv .venv
 source .venv/bin/activate  # Linux/macOS
 # .venv\Scripts\activate  # Windows

# 3. Instalar dependências
 pip install --upgrade pip
 pip install -r requirements.txt

# 4. Subir o serviço
 uvicorn apps.evidence_api.main:app --reload
```

A API ficará acessível em `http://localhost:8000`.
Você pode inspecionar a documentação automática em:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

---
## Endpoints

### `GET /`

Retorna informações básicas do serviço:

```json
{
  "service": "matverse-core-evidence-api",
  "version": "0.1.0",
  "lambda_sovereign": 0.27,
  "psi_threshold": 0.85,
  "vector_dimension": 5
}
```

### `GET /health`

```json
{"status": "ok", "omega_gate": "online"}
```

### `POST /evidence`

Request body:

```json
{
  "intent": "verificar coerência entre minha hipótese e o corpus MatVerse",
  "intent_vector": [0.90, 0.10, 0.55, 0.80, 0.02],
  "metadata": {
    "source": "local-dev",
    "tags": ["demo", "matverse-core"]
  }
}
```

Resposta (exemplo):

```json
{
  "timestamp": 1732526400.123,
  "hash_sha256": "a3b9...f91c",
  "psi_index": 0.8842,
  "lambda_sovereign": 0.27,
  "status": "COERENTE (Ω-GATE: Aprovado)",
  "message": "Evidence Note registrada com M-CSQI."
}
```

Erros comuns:

- **Dimensão errada do vetor**
  - Esperado: vetor com 5 posições (por causa do seed interno ρ_ext).
  - Se enviar outro tamanho → HTTP 400 com mensagem explicando a dimensão esperada.

- **Vetores vazios ou inválidos**
  - O motor lança `ValueError`; a API traduz para HTTP 400 com o motivo.

---
## Testes

Depois de instalar as dependências:

```bash
pytest
```

Os testes verificam que:

- Ψ sempre cai em `[0, 1]`;
- vetores idênticos produzem alta coerência (Ψ ≈ 1);
- vetores ortogonais produzem Ψ baixo;
- vetores vazios ou com dimensões diferentes disparam `ValueError`.

---
## Próximos Passos (Roadmap técnico)

- Substituir o `EXTERNAL_COHERENCE_VECTOR` por embeddings reais do corpus
  (os documentos .docx do MatVerse).
- Adicionar logging estruturado das Evidence Notes (para auditoria).
- Integrar com fontes externas de veracidade (fact-checkers, etc.).
- Versão 0.2.0: expor métricas em `/metrics` (Prometheus-friendly).

---
## Licença

Este repositório é um *núcleo técnico mínimo* do MatVerse. Use, estude,
critique e melhore – mas preserve a integridade do Ψ e de λ.
