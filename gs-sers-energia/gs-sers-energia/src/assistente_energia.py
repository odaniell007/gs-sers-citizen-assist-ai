"""Módulo de ENERGIA do Citizen Assist AI (contribuição da disciplina SERS).

Uso interativo:   python src/assistente_energia.py
Uso integrado:    from assistente_energia import responder
                  texto = responder("vale a pena instalar energia solar?")

O assistente NÃO inventa números: toda resposta vem de calculos.py, que lê os
dados de dados/*.csv e dados/premissas.json. Toda resposta termina com
limitações e fontes, como pede o enunciado.
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calculos as c  # noqa: E402

RODAPE = (
    "\nLimitações: são estimativas, não garantias. Os valores mudam com a sua conta de luz "
    "e com os orçamentos reais."
    "\nFontes: ANEEL, Greener, Solfácil e MCTI."
)

NOTA_PERFIL = (
    "\nEstes números partem de uma conta de exemplo. Para os da sua casa, digite: "
    "consumo <kWh da sua conta> e tarifa <R$ por kWh da sua conta>."
)


def _norm(txt):
    txt = unicodedata.normalize("NFD", txt.lower())
    return "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")


def _brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _prazo(meses):
    if meses is None:
        return "não se paga em 10 anos"
    anos, resto = divmod(meses, 12)
    if anos == 0:
        return f"{meses} {'mês' if meses == 1 else 'meses'}"
    a = f"{anos} {'ano' if anos == 1 else 'anos'}"
    return f"{a} e {resto} {'mês' if resto == 1 else 'meses'}" if resto else a


class Perfil:
    """Dados do usuário. Padrão = conta de exemplo; o usuário pode trocar pelos dados da própria fatura."""

    def __init__(self):
        self.premissas = c.carregar_premissas()
        self._eq0 = c.carregar_equipamentos()
        self._md0 = c.carregar_medidas()
        self.consumo_kwh = self.premissas.get("consumo_real_kwh_mes", {}).get("valor")
        self.consumo_informado = False
        self._calibrar()

    def _calibrar(self):
        self.equipamentos, self.medidas = c.calibrar(self._eq0, self._md0, self.consumo_kwh)

    def definir_tarifa(self, valor):
        self.premissas["tarifa_kwh_com_tributos"]["valor"] = float(valor)

    def definir_consumo(self, kwh):
        self.consumo_kwh = float(kwh)
        self.consumo_informado = True
        self._calibrar()

    def definir_ligacao(self, tipo):
        if tipo not in ("monofasico", "bifasico", "trifasico"):
            raise ValueError("tipo de ligação inválido")
        self.premissas["tipo_ligacao"]["valor"] = tipo

    def resultado(self):
        return c.comparar(self.equipamentos, self.medidas, self.premissas, self.consumo_kwh)


# ---------------- respostas por intenção ----------------
def _consumo(perfil):
    cons = c.consumo_por_equipamento(perfil.equipamentos)
    total = sum(cons.values())
    tarifa = perfil.premissas["tarifa_kwh_com_tributos"]["valor"]
    nomes = {e["id"]: e["equipamento"] for e in perfil.equipamentos}
    top = sorted(cons.items(), key=lambda kv: kv[1], reverse=True)[:3]
    linhas = [f"- {nomes[i]}: {k:.0f} kWh/mês ({k / total:.0%})" for i, k in top]
    return (
        f"O consumo da conta de exemplo é de {total:.0f} kWh/mês, "
        f"cerca de {_brl(total * tarifa)} por mês na tarifa de {_brl(tarifa)}/kWh.\n"
        "Os 3 maiores consumos (distribuição estimada por aparelho):\n" + "\n".join(linhas) +
        "\nCálculo: energia (kWh) = potência (kW) × horas de uso."
    )


def _economizar(perfil):
    r = perfil.resultado()
    boas = [m for m in r["medidas"] if m["payback_meses"] is not None]
    linhas = [
        f"{n}. {m['descricao']}: ~{m['economia_kwh_mes']:.0f} kWh/mês "
        f"({_brl(m['economia_rs_mes'])}), custo {_brl(m['investimento_rs'])}."
        for n, m in enumerate(boas, 1)
    ]
    a = r["A_eficiencia"]
    return (
        "Comece por estas dicas:\n" + "\n".join(linhas) +
        f"\nJuntas: ~{a['economia_kwh_mes']:.0f} kWh/mês ({_brl(a['economia_rs_mes'])}) "
        f"com investimento de {_brl(a['investimento_rs'])}.\n"
        "Trocar a geladeira só pela economia de energia não compensa."
    )


def _solar(perfil):
    r = perfil.resultado()
    b = r["B_solar"]
    return (
        f"Energia solar fotovoltaica (conectada à rede): sistema de {f"{b['kwp']:.2f}".replace('.', ',')} kWp "
        f"({b['modulos']} módulos), gerando cerca de {b['geracao_kwh_mes']:.0f} kWh/mês.\n"
        f"- Investimento estimado: {_brl(b['investimento_rs'])}\n"
        f"- Economia estimada: {_brl(b['economia_rs_mes'])}/mês. A conta não zera: a distribuidora "
        f"cobra um mínimo de {b['disponibilidade_kwh']} kWh pela ligação, mesmo sem consumo.\n"
        f"- Retorno estimado: {_prazo(b['payback_meses'])}; ganho líquido em 10 anos: "
        f"{_brl(b['ganho_liquido_rs'])}\n"
        f"- CO₂ evitado: cerca de {b['co2_kg_ano']:.0f} kg/ano (a matriz elétrica brasileira já é "
        "majoritariamente renovável, então o ganho principal é financeiro).\n"
        "O valor é uma referência de mercado: peça 3 orçamentos e confirme se inclui projeto, "
        "instalação e a liberação na distribuidora. Parte do desconto se perde porque a "
        "distribuidora cobra pelo uso da rede (a chamada taxa Fio B); isso já está considerado."
    )


def _comparar(perfil):
    r = perfil.resultado()
    a, b, cc = r["A_eficiencia"], r["B_solar"], r["C_eficiencia_mais_solar"]
    linhas = [
        ("A) Só eficiência", a),
        ("B) Só solar", b),
        ("C) Eficiência + solar menor", cc),
    ]
    txt = "Comparação para a mesma casa, no mesmo período de 10 anos:\n"
    for nome, d in linhas:
        txt += (
            f"- {nome}: investe {_brl(d['investimento_rs'])}, economiza {_brl(d['economia_rs_mes'])}/mês, "
            f"retorno em {_prazo(d['payback_meses'])}, ganho líquido {_brl(d['ganho_liquido_rs'])}, "
            f"CO₂ evitado {d['co2_kg_ano']:.0f} kg/ano.\n"
        )
    txt += (
        f"Recomendação: começar pelas medidas de eficiência (retorno em {_prazo(a['payback_meses'])}) "
        f"e dimensionar o sistema solar depois, já com o consumo reduzido "
        f"({cc['modulos']} módulos em vez de {b['modulos']}). Assim o investimento é menor "
        "e o retorno, mais rápido. Se não houver telhado adequado ou dinheiro para investir "
        "agora, a alternativa A sozinha já reduz a conta."
    )
    return txt


def _co2(perfil):
    p = perfil.premissas
    r = perfil.resultado()
    return (
        f"Usamos o fator médio do sistema elétrico brasileiro: {p['fator_emissao_kg_co2_kwh']['valor'] * 1000:.1f} g de CO₂ por kWh "
        "(MCTI, média de 2023; varia a cada ano).\n"
        f"- Alternativa A evita ~{r['A_eficiencia']['co2_kg_ano']:.0f} kg de CO₂/ano\n"
        f"- Alternativa B evita ~{r['B_solar']['co2_kg_ano']:.0f} kg de CO₂/ano\n"
        f"- Alternativa C evita ~{r['C_eficiencia_mais_solar']['co2_kg_ano']:.0f} kg de CO₂/ano\n"
        "Como a rede brasileira já emite pouco, a economia de dinheiro pesa mais que a de carbono. "
        "Não contabilizamos as emissões da fabricação dos módulos."
    )


def _standby(perfil):
    cons = c.consumo_por_equipamento(perfil.equipamentos)
    total = sum(cons.values())
    tarifa = perfil.premissas["tarifa_kwh_com_tributos"]["valor"]
    sb = cons["standby"]
    pc = cons["computador"]
    reg = next(m for m in perfil.medidas if m["id"] == "standby")
    eco = c.economia_medida(reg, perfil.equipamentos)
    return (
        f"Pouco por aparelho, mas soma. Na casa-exemplo, a carga em espera (roteador, TV box, carregadores) "
        f"é estimada em {sb:.0f} kWh/mês, cerca de {_brl(sb * tarifa)} por mês ({sb / total:.0%} do consumo).\n"
        f"O computador, usado {perfil.equipamentos[[e['id'] for e in perfil.equipamentos].index('computador')]['horas_dia']:.0f} h/dia, "
        f"gasta ~{pc:.0f} kWh/mês; o que pesa é o tempo ligado, não a tomada.\n"
        f"Desligar o que fica em espera (régua com interruptor) economiza ~{eco:.0f} kWh/mês "
        f"({_brl(eco * tarifa)}) e custa cerca de {_brl(reg['investimento_rs'])}.\n"
        "Carregador sem aparelho conectado consome muito pouco; para saber o valor real, "
        "meça com um wattímetro de tomada."
    )


def _banho(perfil, pergunta=""):
    p = perfil.premissas
    tarifa = p["tarifa_kwh_com_tributos"]["valor"]
    pessoas = int(p["pessoas_na_casa"]["valor"])
    ch = next(e for e in perfil.equipamentos if e["id"] == "chuveiro")
    kwh_min = ch["potencia_w"] / 60 * ch["dias_mes"] / 1000  # kWh/mês por minuto a menos por dia
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*min", _norm(pergunta))
    if not m:
        return (f"Cada minuto a menos no banho, todos os dias, economiza ~{kwh_min:.2f} kWh/mês "
                f"({_brl(kwh_min * tarifa)}) por pessoa. Diga quantos minutos e eu calculo.")
    mins = float(m.group(1).replace(",", "."))
    um = mins * kwh_min
    return (
        f"Chuveiro de {ch['potencia_w']:.0f} W, {mins:g} min a menos por dia:\n"
        f"- Só você (1 banho): ~{um:.0f} kWh/mês, cerca de {_brl(um * tarifa)} a menos na conta.\n"
        f"- Todas as {pessoas} pessoas: ~{um * pessoas:.0f} kWh/mês, cerca de {_brl(um * pessoas * tarifa)}.\n"
        "O chuveiro é o maior consumo da casa-exemplo, então é a dica que mais rende."
    )


def _fontes(_perfil):
    return (
        "As referências ficam em docs/referencias.md. Resumo: tarifas e regras da ANEEL, preços de "
        "sistemas da Greener e Solfácil, fator de emissão do MCTI e Lei 14.300/2022. Cada dado em "
        "dados/premissas.json indica se é 'fonte' ou 'estimado'."
    )


INTENCOES = [
    (("referencia", "fonte", "limita", "garant"), _fontes),
    (("co2", "carbono", "ambient", "emiss", "poluic"), _co2),
    (("compar", "alternativ", "melhor", "recomend"), _comparar),
    (("solar", "vale a pena", "painel", "paineis", "fotovolt", "renovavel", "placa"), _solar),
    (("banho", "chuveiro", "ducha"), _banho),
    (("tomada", "carregador", "espera", "stand", "deixar ligado", "computador", "notebook"), _standby),
    (("economi", "reduzir", "dica", "diminuir", "baixar", "gastar menos"), _economizar),
    (("consumo", "gasto", "quanto", "vilao", "conta", "kwh"), _consumo),
]

AJUDA = (
    "Posso ajudar com energia em casa. Pergunte, por exemplo:\n"
    "- \"quanto eu consumo?\"\n- \"como economizar energia?\"\n"
    "- \"vale a pena energia solar?\"\n- \"compare as alternativas\"\n- \"quanto de CO2 evito?\"\n"
    "Comandos: tarifa <valor em R$/kWh> | consumo <kWh da fatura> | ligacao <monofasico|bifasico|trifasico> | sair"
)


def responder(pergunta, perfil=None):
    perfil = perfil or Perfil()
    q = _norm(pergunta)
    for chaves, funcao in INTENCOES:
        if any(k in q for k in chaves):
            resp = funcao(perfil, pergunta) if funcao is _banho else funcao(perfil)
            if not perfil.consumo_informado and funcao in (_consumo, _solar, _comparar):
                resp += NOTA_PERFIL
            return resp + RODAPE
    return AJUDA


def _comando(entrada, perfil):
    partes = entrada.strip().split()
    if len(partes) != 2:
        return None
    cmd, val = _norm(partes[0]), partes[1].replace(",", ".")
    try:
        if cmd == "tarifa":
            perfil.definir_tarifa(val)
            return f"Tarifa atualizada para {_brl(float(val))}/kWh."
        if cmd == "consumo":
            perfil.definir_consumo(val)
            return f"Consumo mensal atualizado para {float(val):.0f} kWh (usado no dimensionamento solar)."
        if cmd == "ligacao":
            perfil.definir_ligacao(_norm(val))
            return f"Tipo de ligação: {_norm(val)}."
    except ValueError:
        return "Valor inválido. Exemplo: tarifa 1.05"
    return None


def main():
    perfil = Perfil()
    print("Citizen Assist AI — módulo Energia\n" + AJUDA)
    while True:
        try:
            entrada = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if _norm(entrada) in ("sair", "exit", "q"):
            break
        if not entrada:
            continue
        resp = _comando(entrada, perfil) or responder(entrada, perfil)
        print("\nAssistente:", resp)


if __name__ == "__main__":
    main()
