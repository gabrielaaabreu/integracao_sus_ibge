# Integração SUS + IBGE - Municípios do Ceará

Visualização interativa de dados do SUS (atendimentos) e IBGE (dados socioeconômicos) para municípios do Ceará.

## Pré-requisitos

 Python 3.12+ 

## Como executar no Windows

1. Instalar `uv` via PowerShell  

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Clone o repositório

```bash
git clone https://github.com/gabrielaaabreu/integracao_sus_ibge.git
```

3. Vá para a pasta do projeto

```bash
cd integracao_sus_ibge
```

4. Instale as dependências
```bash
uv sync
```

5. Execute o projeto
```bash
uv run python -m streamlit run main.py
```