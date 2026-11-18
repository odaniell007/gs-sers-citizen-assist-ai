# Testes com usuários

> **Preencher com testes reais.** O enunciado pede registro das situações testadas, dos comentários e dos ajustes. Não registre nome, endereço nem outros dados pessoais: use "Usuário 1", "Usuário 2"...

## Roteiro (5 a 10 minutos por pessoa)
1. Mostre o assistente e peça para a pessoa fazer 3 perguntas com as próprias palavras.
2. Pergunte: entendeu a resposta? O que ficou confuso? Confiaria nessa orientação? Faltou alguma informação?
3. Pergunte se entendeu as limitações (estimativa, não garantia).
4. Anote o ajuste feito no assistente depois do teste.

## Registro

| Usuário | Perfil (ex.: mora em casa/apto, idade aproximada) | Perguntas testadas | Comentários | Ajuste realizado |
|---|---|---|---|---|
| 1 | Estudante, 19 anos | "Deixar o PC e o carregador na tomada o dia inteiro pesa muito no valor final ou é pouca coisa?" | O assistente não respondeu | Criada a resposta sobre aparelhos em espera e carregadores (palavras: tomada, carregador, espera, PC) com base nos dados de standby |
| 2 | Estudante, 18 anos | "Se eu diminuir uns 5 minutos no meu banho todo dia, quanto isso alivia na conta?" / "quanto eu consumo?" | Entendeu que o chuveiro é o maior gasto. Confuso: a resposta falou de 2 min por pessoa e listou lâmpada e geladeira sem ele pedir; apareceu `dados/premissas.json` e texto técnico (ANEEL). Faltou responder o valor só para ele. Faria banho mais curto e a régua; geladeira, não. | Resposta nova que calcula com os minutos informados e mostra primeiro o valor de 1 pessoa; rodapé sem caminho de arquivo e sem siglas técnicas |
| 3 | Adulto, 53 anos, mora em casa, trabalha com finanças | "como economizar energia?" / "vale a pena energia solar?" | Entendeu bem retorno, investimento e que a solar não zera a conta. Confuso: apareceu `dados/premissas.json`; "mínimo de 50 kWh da ligação" e "Lei 14.300 (Fio B)" sem explicação. Faltou perguntar quantas pessoas moram e quanto paga de conta; faltou dizer se o valor inclui mão de obra, projeto e homologação. Faria LED e régua na hora; solar só após 3 orçamentos. | Rodapé simplificado; termos explicados no texto; aviso para informar consumo e tarifa da própria casa; resposta de solar orienta pedir 3 orçamentos e confirmar o que está incluso; lista de dicas encurtada |
| 4 | | | | |
| 5 | | | | |

## Resumo dos ajustes
Testamos com 3 pessoas. Principais ajustes: (1) o assistente passou a calcular a economia com os minutos de banho informados; (2) respostas sem caminho de arquivo e com termos técnicos explicados; (3) aviso de que os números são de uma casa-exemplo e como informar os dados reais; (4) resposta sobre aparelhos em espera e carregadores; (5) lista de dicas mais curta; (6) solar orienta pedir 3 orçamentos e conferir o que está incluso.
