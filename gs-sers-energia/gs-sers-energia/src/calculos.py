"""Cálculos de energia, comparação de alternativas e impacto ambiental.

Todas as funções são puras (sem entrada do usuário) para facilitar testes.
Unidades: potência em W, energia em kWh, dinheiro em R$, CO2 em kg.
"""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def carregar_premissas(caminho=None):
    with open(caminho or BASE / "dados" / "premissas.json", encoding="utf-8") as f:
        return json.load(f)


def _ler_csv(nome):
    with open(BASE / "dados" / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def carregar_equipamentos():
    itens = _ler_csv("equipamentos.csv")
    for i in itens:
        for k in ("quantidade", "potencia_w", "horas_dia", "dias_mes"):
            i[k] = float(i[k])
    return itens


def carregar_medidas():
    itens = _ler_csv("medidas_eficiencia.csv")
    for i in itens:
        for k in ("potencia_nova_w", "horas_nova", "investimento_rs"):
            i[k] = float(i[k])
    return itens


# ---------- Energia e potência ----------
def kwh_mes(potencia_w, horas_dia, dias_mes=30, quantidade=1):
    """E (kWh) = P (kW) x tempo (h). Aqui: P(W) x h/dia x dias x qtd / 1000."""
    return potencia_w * horas_dia * dias_mes * quantidade / 1000


def consumo_por_equipamento(equipamentos):
    return {
        e["id"]: kwh_mes(e["potencia_w"], e["horas_dia"], e["dias_mes"], e["quantidade"])
        for e in equipamentos
    }


def consumo_total(equipamentos):
    return sum(consumo_por_equipamento(equipamentos).values())


def custo_mensal(kwh, tarifa):
    return kwh * tarifa


def calibrar(equipamentos, medidas, consumo_real):
    """Ajusta as horas de uso de forma proporcional para o total bater com o consumo da fatura."""
    total = consumo_total(equipamentos)
    if not consumo_real or total == 0:
        return equipamentos, medidas
    f = consumo_real / total
    eq = [{**e, "horas_dia": e["horas_dia"] * f} for e in equipamentos]
    md = [{**m, "horas_nova": m["horas_nova"] * f} for m in medidas]
    return eq, md


# ---------- Alternativa A: eficiência ----------
def economia_medida(medida, equipamentos):
    """Economia mensal (kWh) = consumo atual do equipamento - consumo após a medida."""
    eq = next(e for e in equipamentos if e["id"] == medida["equipamento_id"])
    atual = kwh_mes(eq["potencia_w"], eq["horas_dia"], eq["dias_mes"], eq["quantidade"])
    novo = kwh_mes(medida["potencia_nova_w"], medida["horas_nova"], eq["dias_mes"], eq["quantidade"])
    return max(atual - novo, 0.0)


# ---------- Alternativa B: solar fotovoltaica ----------
def dimensionar_fv(consumo_kwh, premissas):
    """Dimensiona o sistema para cobrir o consumo acima do custo de disponibilidade."""
    disp = premissas["custo_disponibilidade_kwh"][premissas["tipo_ligacao"]["valor"]]
    alvo = max(consumo_kwh - disp, 0.0)
    ger_por_kwp = premissas["irradiacao_hsp"]["valor"] * 30 * premissas["taxa_desempenho"]["valor"]
    kwp_necessario = alvo / ger_por_kwp if ger_por_kwp else 0.0
    wp_modulo = premissas["potencia_modulo_wp"]["valor"]
    # arredonda para o número inteiro de módulos mais próximo (mínimo 1 se há consumo a cobrir)
    modulos = max(1, round(kwp_necessario * 1000 / wp_modulo)) if alvo > 0 else 0
    kwp = modulos * wp_modulo / 1000
    geracao = kwp * ger_por_kwp
    investimento = kwp * 1000 * premissas["custo_fv_rs_por_wp"]["valor"]
    return {
        "disponibilidade_kwh": disp, "alvo_kwh": alvo, "modulos": modulos,
        "kwp": kwp, "geracao_kwh_mes": geracao, "investimento_rs": investimento,
    }


def economia_fv_mensal(consumo_kwh, fv, premissas):
    """Energia compensada nunca passa do consumo acima da disponibilidade."""
    kwh_comp = min(fv["geracao_kwh_mes"], max(consumo_kwh - fv["disponibilidade_kwh"], 0.0))
    return kwh_comp, kwh_comp * premissas["tarifa_kwh_com_tributos"]["valor"] * premissas["fator_compensacao"]["valor"]


# ---------- Fluxo de caixa comum (mesmo período para todas as alternativas) ----------
def fluxo_caixa(investimento, economia_mensal, premissas, solar=False,
                reajuste=None, anos=None):
    """Retorna payback (meses, None se não ocorre no horizonte) e ganho líquido no horizonte."""
    reajuste = premissas["reajuste_tarifa_anual"]["valor"] if reajuste is None else reajuste
    anos = anos or premissas["horizonte_anos"]["valor"]
    degr = premissas["degradacao_fv_anual"]["valor"] if solar else 0.0
    om = premissas["om_fv_rs_por_ano"]["valor"] / 12 if solar else 0.0
    acumulado, payback = -investimento, None
    for m in range(anos * 12):
        ano = m // 12
        ganho = economia_mensal * (1 + reajuste) ** ano * (1 - degr) ** ano - om
        acumulado += ganho
        if payback is None and acumulado >= 0:
            payback = m + 1
    return {"payback_meses": payback, "ganho_liquido_rs": acumulado}


# ---------- Impacto ambiental ----------
def co2_evitado_kg_ano(kwh_mes_evitado, premissas):
    return kwh_mes_evitado * 12 * premissas["fator_emissao_kg_co2_kwh"]["valor"]


# ---------- Comparação completa ----------
def medidas_rapidas(medidas, equipamentos, ids=("led", "banho", "standby")):
    sel = [m for m in medidas if m["id"] in ids]
    kwh = sum(economia_medida(m, equipamentos) for m in sel)
    inv = sum(m["investimento_rs"] for m in sel)
    return {"medidas": [m["id"] for m in sel], "economia_kwh_mes": kwh, "investimento_rs": inv}


def comparar(equipamentos=None, medidas=None, premissas=None, consumo_kwh=None):
    equipamentos = equipamentos or carregar_equipamentos()
    medidas = medidas or carregar_medidas()
    p = premissas or carregar_premissas()
    tarifa = p["tarifa_kwh_com_tributos"]["valor"]
    if consumo_kwh is None:
        consumo_kwh = p.get("consumo_real_kwh_mes", {}).get("valor")
    if consumo_kwh is not None:
        equipamentos, medidas = calibrar(equipamentos, medidas, consumo_kwh)
    base = consumo_kwh if consumo_kwh is not None else consumo_total(equipamentos)

    res = {"base": {"consumo_kwh": base, "custo_mensal_rs": custo_mensal(base, tarifa)}}

    # A) Eficiência
    a = medidas_rapidas(medidas, equipamentos)
    econ_a = a["economia_kwh_mes"] * tarifa
    fa = fluxo_caixa(a["investimento_rs"], econ_a, p)
    res["A_eficiencia"] = {**a, "economia_rs_mes": econ_a, **fa,
                           "co2_kg_ano": co2_evitado_kg_ano(a["economia_kwh_mes"], p)}

    # B) Solar sobre o consumo atual
    fv_b = dimensionar_fv(base, p)
    kwh_b, econ_b = economia_fv_mensal(base, fv_b, p)
    fb = fluxo_caixa(fv_b["investimento_rs"], econ_b, p, solar=True)
    res["B_solar"] = {**fv_b, "kwh_compensados": kwh_b, "economia_rs_mes": econ_b, **fb,
                      "co2_kg_ano": co2_evitado_kg_ano(kwh_b, p)}

    # C) Eficiência + solar menor (dimensionada para o consumo já reduzido)
    base_c = base - a["economia_kwh_mes"]
    fv_c = dimensionar_fv(base_c, p)
    kwh_c, econ_c_solar = economia_fv_mensal(base_c, fv_c, p)
    inv_c = a["investimento_rs"] + fv_c["investimento_rs"]
    reaj = p["reajuste_tarifa_anual"]["valor"]
    degr = p["degradacao_fv_anual"]["valor"]
    om = p["om_fv_rs_por_ano"]["valor"] / 12
    acum, pb = -inv_c, None
    for m in range(p["horizonte_anos"]["valor"] * 12):
        ano = m // 12
        acum += econ_a * (1 + reaj) ** ano + econ_c_solar * (1 + reaj) ** ano * (1 - degr) ** ano - om
        if pb is None and acum >= 0:
            pb = m + 1
    res["C_eficiencia_mais_solar"] = {
        "medidas": a["medidas"], "modulos": fv_c["modulos"], "kwp": fv_c["kwp"],
        "geracao_kwh_mes": fv_c["geracao_kwh_mes"], "consumo_apos_medidas_kwh": base_c,
        "investimento_rs": inv_c, "economia_rs_mes": econ_a + econ_c_solar,
        "payback_meses": pb, "ganho_liquido_rs": acum,
        "co2_kg_ano": co2_evitado_kg_ano(a["economia_kwh_mes"] + kwh_c, p),
    }

    # Medidas individuais (inclui a geladeira, avaliada à parte)
    indiv = []
    for m in medidas:
        kwh = economia_medida(m, equipamentos)
        inv = m["investimento_rs"]
        f = fluxo_caixa(inv, kwh * tarifa, p)
        indiv.append({"id": m["id"], "descricao": m["descricao"], "economia_kwh_mes": kwh,
                      "economia_rs_mes": kwh * tarifa, "investimento_rs": inv, **f})
    res["medidas"] = sorted(indiv, key=lambda x: (x["payback_meses"] is None, x["payback_meses"] or 0))
    return res


def sensibilidade(reajustes=(0.0, 0.05, 0.08), fatores=(0.8, 0.9, 1.0)):
    """Mostra como o resultado da alternativa B muda com premissas incertas."""
    linhas = []
    eq = carregar_equipamentos()
    base = carregar_premissas().get("consumo_real_kwh_mes", {}).get("valor") or consumo_total(eq)
    for r in reajustes:
        for fc in fatores:
            p = carregar_premissas()
            p["fator_compensacao"]["valor"] = fc
            fv = dimensionar_fv(base, p)
            _, econ = economia_fv_mensal(base, fv, p)
            f = fluxo_caixa(fv["investimento_rs"], econ, p, solar=True, reajuste=r)
            linhas.append({"reajuste": r, "fator_compensacao": fc, **f})
    return linhas
