# MatVerse Core Monorepo

Sistema monorepo para o Web-X MatVerse com o serviço Evidence API exposto via FastAPI.

## Estrutura

```
apps/
  evidence_api/
    coherence_engine.py   # Motor de M-CSQI (fidelidade, entropia e Ψ-Index)
    main.py               # Serviço FastAPI com endpoints /evidence e /health
requirements.txt          # Dependências compartilhadas do monorepo
```

## Configuração

1. Crie e ative um ambiente virtual.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Execução local

```bash
uvicorn apps.evidence_api.main:app --reload
```

- **/health**: retorna status, λ e dimensão semântica.
- **/evidence** (`POST`): calcula o Ψ-Index usando a Métrica de Coerência Semântica
  Quântica Invariante (M-CSQI). Corpo de exemplo:
  ```json
  {
    "intent": "Prova de coerência",
    "metadata": {"source": "demo"},
    "intent_vector": [0.92, 0.15, 0.60, 0.88, 0.05]
  }
  ```

A resposta inclui `psi_index`, `fidelity`, `entropy_penalty`, hash imutável e o
status Ω-GATE (aprovado/penalizado).

## Testes

Execute os testes automatizados com:

```bash
pytest
```
