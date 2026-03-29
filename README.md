# Tennis Trading Platform

Plataforma de trading esportivo para operações em jogos de tênis.

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

## Funcionalidades

- **Gestão de Banca**: Acompanhe sua banca, ROI e ajuste quando necessário
- **Registro de Operações**: Lance entradas com data, jogadores, mercado, odds, stake
- **Fechamento de Trades**: Registre saídas e calcule P/L automaticamente
- **Estatísticas**: Win rate, yield, P/L por método e mercado
- **Análise de Métodos**: Compare performance entre diferentes estratégias

## Estrutura

```
tennis_trader/
├── app.py              # Interface Streamlit
├── requirements.txt    # Dependências
├── data/               # Banco SQLite
└── src/
    ├── __init__.py
    └── database.py     # Lógica de banco de dados
```
