# Justificativas das recomendações

Conta de exemplo: 232 kWh/mês, R$ 128,41, ligação monofásica (mínimo de 30 kWh).

## Por que começar pela eficiência (A)
- Retorno de poucos meses e risco baixo: banho mais curto não custa nada; régua e LED se pagam em 13 a 16 meses.
- O chuveiro elétrico é o maior consumidor (35%), então o hábito de banho pesa mais do que qualquer troca de lâmpada.
- Reduz o consumo antes de decidir sobre a solar.

## Por que a solar (B) entra como fonte renovável
- É a alternativa renovável com maior economia mensal (R$ 89, quase 70% da conta).
- Custo: o investimento inicial (R$ 4.686 para 1,65 kWp) é a principal barreira. Como a conta é baixa (R$ 128), o retorno é mais longo (4 anos e 8 meses), embora ainda positivo em 10 anos (ganho líquido de R$ 6.889).
- Viabilidade: exige telhado próprio, orientação e sombreamento adequados, projeto e homologação na distribuidora; mudanças na tarifa e nas regras do Fio B alteram o retorno (ver sensibilidade em `analise_comparacao.md`).
- Ambiental: gera energia renovável, mas o CO₂ evitado é pequeno (~82 kg/ano) porque a rede brasileira já tem fator baixo.

## Por que a combinação (C) é a recomendação
- Usa o mesmo sistema solar de B, mas soma a economia das medidas de eficiência: R$ 103 por mês contra R$ 89, por R$ 180 a mais. O retorno cai de 4 anos e 8 meses para 4 anos e 2 meses.

## O que não recomendamos (só pela economia)
- Trocar a geladeira antiga: economiza ~15 kWh/mês (R$ 8,21), e o investimento de R$ 3.000 não se paga em 10 anos. Só faz sentido se ela precisar ser trocada de qualquer forma.

## Quando a recomendação muda
- Com contas pequenas como esta, a solar demora mais para se pagar. Se o orçamento real for mais caro que o estimado, ou o usuário não tiver telhado próprio, ficam as medidas da alternativa A.
- Se a tarifa ou o preço do kWp forem diferentes, o módulo recalcula com `tarifa <valor>` ou editando `dados/premissas.json`.
