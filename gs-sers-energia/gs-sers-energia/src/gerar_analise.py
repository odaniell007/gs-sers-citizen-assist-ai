"""Gera docs/analise_comparacao.md a partir dos dados (reprodutível)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calculos as c  # noqa: E402
from assistente_energia import _brl, _prazo  # noqa: E402


def main():
    p = c.carregar_premissas()
    eq, md = c.calibrar(c.carregar_equipamentos(), c.carregar_medidas(),
                        p["consumo_real_kwh_mes"]["valor"])
    r = c.comparar(eq, md, p)
    cons = c.consumo_por_equipamento(eq)
    tarifa = p["tarifa_kwh_com_tributos"]["valor"]
    L = ["# Análise de consumo e comparação de alternativas", "",
         "Arquivo gerado por `python src/gerar_analise.py`. Consumo total, tarifa e tipo de ligação vêm da fatura do grupo; "
         "a distribuição por aparelho, os preços e as demais premissas são **estimados** (ver `dados/premissas.json`).", "",
         "## 1. Consumo atual (conta de exemplo; distribuição por aparelho estimada)", "",
         "| Equipamento | Qtd | Potência (W) | h/dia | kWh/mês | % |", "|---|---|---|---|---|---|"]
    total = sum(cons.values())
    for e in eq:
        k = cons[e["id"]]
        L.append(f"| {e['equipamento']} | {e['quantidade']:.0f} | {e['potencia_w']:.0f} | {e['horas_dia']:.2f} | {k:.1f} | {k / total:.0%} |")
    L += [f"| **Total** | | | | **{total:.1f}** | |", "",
          f"Custo mensal estimado: {total:.1f} kWh × {_brl(tarifa)}/kWh = **{_brl(total * tarifa)}**.", "",
          "## 2. Alternativas (mesma necessidade: reduzir a conta de luz; mesmo período: 10 anos)", "",
          "| Alternativa | Investimento | Economia/mês | Retorno | Ganho líquido 10 anos | CO₂ evitado/ano |", "|---|---|---|---|---|---|"]
    for nome, k in (("A) Eficiência (LED + banho + standby)", "A_eficiencia"),
                    ("B) Solar fotovoltaica (sobre consumo atual)", "B_solar"),
                    ("C) Eficiência + solar menor", "C_eficiencia_mais_solar")):
        d = r[k]
        L.append(f"| {nome} | {_brl(d['investimento_rs'])} | {_brl(d['economia_rs_mes'])} | "
                 f"{_prazo(d['payback_meses'])} | {_brl(d['ganho_liquido_rs'])} | {d['co2_kg_ano']:.0f} kg |")
    L += ["", "## 3. Medidas de eficiência, uma a uma", "",
          "| Medida | Economia (kWh/mês) | Investimento | Retorno |", "|---|---|---|---|"]
    for m in r["medidas"]:
        L.append(f"| {m['descricao']} | {m['economia_kwh_mes']:.1f} | {_brl(m['investimento_rs'])} | {_prazo(m['payback_meses'])} |")
    L += ["", "## 4. Sensibilidade da alternativa B", "",
          "| Reajuste anual da tarifa | Fator de compensação | Retorno | Ganho líquido 10 anos |", "|---|---|---|---|"]
    for s in c.sensibilidade():
        L.append(f"| {s['reajuste']:.0%} | {s['fator_compensacao']} | {_prazo(s['payback_meses'])} | {_brl(s['ganho_liquido_rs'])} |")
    L += ["", "## 5. Impactos ambientais e limitações", "",
          f"- Fator de emissão usado: {p['fator_emissao_kg_co2_kwh']['valor'] * 1000:.1f} g CO₂/kWh (MCTI, 2023). "
          "A matriz brasileira já é majoritariamente renovável, então o CO₂ evitado é pequeno (dezenas a ~100 kg/ano por casa).",
          "- Não foram contabilizadas as emissões de fabricação dos módulos nem o descarte no fim da vida útil.",
          "- O sistema solar depende de telhado com boa orientação e pouca sombra; apartamentos e imóveis alugados podem não conseguir instalar.",
          "- Retorno e economia mudam com tarifa, bandeira tarifária, regras do Fio B e preço do orçamento real.",
          "- Estas são estimativas, não resultados garantidos."]
    out = Path(__file__).resolve().parent.parent / "docs" / "analise_comparacao.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Gerado: {out}")


if __name__ == "__main__":
    main()
