# Citizen Assist AI — Módulo Energia (SERS)

Global Solution 2026.2 · Soluções em Energias Renováveis e Sustentáveis · Ciência da Computação (1CC)

> **Contribuição da disciplina SERS.** Se este conteúdo ficar num repositório compartilhado com outras disciplinas, mantenha tudo desta GS dentro da pasta `energia/` (ou deste repositório) e identifique-a no README principal.

## Integrantes

| Nome | RM |
|---|---|
| Daniel Vieira | 573326 |
| _[preencher]_ | _[preencher]_ |

## Público e problema

**Público:** famílias de baixa e média renda da cidade de São Paulo, em casa própria, que recebem a conta de luz e não sabem onde a energia está sendo gasta nem se vale a pena investir em energia solar.

**Necessidade energética:** reduzir a conta de luz da casa. O consumo (232 kWh/mês), a tarifa (R$ 0,5535/kWh, total da conta ÷ kWh) e a ligação (monofásica) vêm da fatura do grupo; a distribuição por aparelho (`dados/equipamentos.csv`) é **estimada** e ajustada para bater com o consumo da fatura. O assistente aceita os dados da fatura de qualquer usuário.

**Como o assistente contribui:** responde, em linguagem simples, perguntas como "quanto eu consumo?", "como economizar?", "vale a pena energia solar?" e "compare as alternativas". Cada resposta vem de cálculos reais (`src/calculos.py`) e termina com **limitações** e **fontes**.

## Funcionalidades de energia

1. **Diagnóstico de consumo:** E (kWh) = potência (kW) × horas de uso, por equipamento, com custo mensal e ranking dos maiores consumos.
2. **Alternativa A — eficiência:** LED, banho mais curto e régua anti-standby (e a troca de geladeira, avaliada à parte).
3. **Alternativa B — energia solar fotovoltaica (renovável):** dimensionamento em kWp e módulos, geração, investimento, economia e retorno.
4. **Alternativa C — A + B:** solar menor, dimensionada para o consumo já reduzido.
5. **Comparação no mesmo período (10 anos):** investimento, economia mensal, payback, ganho líquido e CO₂ evitado.
6. **Sensibilidade:** como o retorno da solar muda com reajuste da tarifa e com o fator de compensação.
7. **Personalização:** comandos `tarifa`, `consumo` e `ligacao` para usar os dados da fatura.

## Como executar

Requer Python 3.9+ e nenhuma biblioteca externa.

```bash
python src/assistente_energia.py     # assistente interativo (terminal)
python src/gerar_analise.py          # regenera docs/analise_comparacao.md
python tests/test_calculos.py        # testes automatizados
```

Integração com o Citizen Assist AI: `from assistente_energia import responder` e chame `responder("vale a pena energia solar?")`; a função devolve um texto pronto para o assistente exibir. Para usar os dados de outro usuário, passe um objeto `Perfil()` como segundo argumento.

## Estrutura

```
src/calculos.py              cálculos de energia, payback, CO2 e comparação
src/assistente_energia.py    módulo de conversa do Citizen Assist AI
src/gerar_analise.py         gera o relatório de comparação
dados/equipamentos.csv       consumo da casa-exemplo (estimado)
dados/medidas_eficiencia.csv medidas da alternativa A
dados/premissas.json         tarifa, solar, CO2... cada um com origem e tipo (fonte/estimado)
docs/analise_comparacao.md   tabelas de consumo, comparação e sensibilidade
docs/justificativas.md       justificativa das recomendações
docs/referencias.md          fontes
docs/testes_usuarios.md      registro dos testes com usuários
docs/roteiro_video.md        roteiro do vídeo de 3 minutos
tests/test_calculos.py       testes automatizados
```

## Resultado principal (conta de exemplo: 232 kWh/mês, R$ 128,41, 10 anos)

| Alternativa | Investimento | Economia/mês | Retorno | Ganho líquido |
|---|---|---|---|---|
| A) Eficiência | R$ 180 | R$ 24 | 8 meses | R$ 3.405 |
| B) Solar (1,65 kWp) | R$ 4.686 | R$ 89 | 4 anos e 8 meses | R$ 6.889 |
| C) A + solar (1,65 kWp) | R$ 4.866 | R$ 103 | 4 anos e 2 meses | R$ 8.891 |

Detalhes e premissas em `docs/analise_comparacao.md` e `docs/justificativas.md`.

## Limitações

- A distribuição por aparelho e o preço dos itens são **estimados** e marcados como tal; consumo e tarifa vêm da fatura do grupo. Os valores reais mudam com a fatura, a bandeira tarifária, o orçamento e as regras do Fio B.
- A economia e o retorno são estimativas, não resultados garantidos.
- A solar depende de telhado com boa orientação; apartamentos e imóveis alugados podem não conseguir instalar.
- O CO₂ evitado é pequeno porque a matriz elétrica brasileira já é majoritariamente renovável; as emissões da fabricação dos módulos não foram contabilizadas.

## Uso de IA generativa

A IA foi usada como apoio para estruturar o projeto e o código. O grupo é responsável por conferir dados, cálculos, referências e recomendações; as fontes estão em `docs/referencias.md` e as premissas, em `dados/premissas.json`.
