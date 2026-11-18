# Análise de consumo e comparação de alternativas

Arquivo gerado por `python src/gerar_analise.py`. Consumo total, tarifa e tipo de ligação vêm da fatura do grupo; a distribuição por aparelho, os preços e as demais premissas são **estimados** (ver `dados/premissas.json`).

## 1. Consumo atual (conta de exemplo; distribuição por aparelho estimada)

| Equipamento | Qtd | Potência (W) | h/dia | kWh/mês | % |
|---|---|---|---|---|---|
| Chuveiro elétrico | 1 | 5500 | 0.49 | 81.6 | 35% |
| Geladeira antiga (frost free) | 1 | 70 | 19.79 | 41.6 | 18% |
| Lâmpadas fluorescentes compactas | 10 | 20 | 4.12 | 24.7 | 11% |
| Televisão | 1 | 120 | 4.12 | 14.8 | 6% |
| Ventilador | 2 | 60 | 4.95 | 17.8 | 8% |
| Máquina de lavar roupas | 1 | 500 | 0.41 | 6.2 | 3% |
| Computador de mesa | 1 | 150 | 3.30 | 14.8 | 6% |
| Ferro de passar | 1 | 1000 | 0.12 | 3.7 | 2% |
| Micro-ondas | 1 | 1200 | 0.25 | 8.9 | 4% |
| Aparelhos em espera (roteador, TV box, carregadores) | 1 | 30 | 19.79 | 17.8 | 8% |
| **Total** | | | | **232.0** | |

Custo mensal estimado: 232.0 kWh × R$ 0,55/kWh = **R$ 128,41**.

## 2. Alternativas (mesma necessidade: reduzir a conta de luz; mesmo período: 10 anos)

| Alternativa | Investimento | Economia/mês | Retorno | Ganho líquido 10 anos | CO₂ evitado/ano |
|---|---|---|---|---|---|
| A) Eficiência (LED + banho + standby) | R$ 180,00 | R$ 23,75 | 8 meses | R$ 3.405,02 | 20 kg |
| B) Solar fotovoltaica (sobre consumo atual) | R$ 4.686,00 | R$ 88,77 | 4 anos e 8 meses | R$ 6.888,73 | 82 kg |
| C) Eficiência + solar menor | R$ 4.866,00 | R$ 103,00 | 4 anos e 2 meses | R$ 8.891,43 | 93 kg |

## 3. Medidas de eficiência, uma a uma

| Medida | Economia (kWh/mês) | Investimento | Retorno |
|---|---|---|---|
| Reduzir o tempo de banho em cerca de 2 minutos por pessoa | 20.4 | R$ 0,00 | 1 mês |
| Régua com interruptor para desligar aparelhos em espera | 8.9 | R$ 60,00 | 1 ano e 1 mês |
| Trocar 10 lâmpadas fluorescentes por LED de 9 W | 13.6 | R$ 120,00 | 1 ano e 4 meses |
| Trocar a geladeira antiga por uma com selo Procel A | 14.8 | R$ 3.000,00 | não se paga em 10 anos |

## 4. Sensibilidade da alternativa B

| Reajuste anual da tarifa | Fator de compensação | Retorno | Ganho líquido 10 anos |
|---|---|---|---|
| 0% | 0.8 | 6 anos | R$ 3.072,60 |
| 0% | 0.9 | 5 anos e 3 meses | R$ 4.229,93 |
| 0% | 1.0 | 4 anos e 7 meses | R$ 5.387,25 |
| 5% | 0.8 | 5 anos e 4 meses | R$ 5.435,98 |
| 5% | 0.9 | 4 anos e 8 meses | R$ 6.888,73 |
| 5% | 1.0 | 4 anos e 3 meses | R$ 8.341,47 |
| 8% | 0.8 | 5 anos | R$ 7.184,29 |
| 8% | 0.9 | 4 anos e 5 meses | R$ 8.855,58 |
| 8% | 1.0 | 4 anos | R$ 10.526,87 |

## 5. Impactos ambientais e limitações

- Fator de emissão usado: 38.5 g CO₂/kWh (MCTI, 2023). A matriz brasileira já é majoritariamente renovável, então o CO₂ evitado é pequeno (dezenas a ~100 kg/ano por casa).
- Não foram contabilizadas as emissões de fabricação dos módulos nem o descarte no fim da vida útil.
- O sistema solar depende de telhado com boa orientação e pouca sombra; apartamentos e imóveis alugados podem não conseguir instalar.
- Retorno e economia mudam com tarifa, bandeira tarifária, regras do Fio B e preço do orçamento real.
- Estas são estimativas, não resultados garantidos.
