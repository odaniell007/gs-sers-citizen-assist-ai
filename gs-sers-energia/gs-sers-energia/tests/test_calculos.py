"""Testes automatizados. Rodar: python tests/test_calculos.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import calculos as c  # noqa: E402
from assistente_energia import responder, Perfil  # noqa: E402


def test_kwh_mes():
    # 5500 W x 0,6 h x 30 dias = 99 kWh
    assert abs(c.kwh_mes(5500, 0.6, 30) - 99.0) < 1e-9


def test_consumo_total_casa_exemplo():
    assert abs(c.consumo_total(c.carregar_equipamentos()) - 281.4) < 1e-6


def test_economia_led():
    eq, med = c.carregar_equipamentos(), c.carregar_medidas()
    led = next(m for m in med if m["id"] == "led")
    assert abs(c.economia_medida(led, eq) - 16.5) < 1e-6


def test_fv_nao_ultrapassa_consumo():
    p = c.carregar_premissas()
    fv = c.dimensionar_fv(281.4, p)
    kwh, _ = c.economia_fv_mensal(281.4, fv, p)
    assert kwh <= 281.4 - fv["disponibilidade_kwh"] + 1e-9


def test_consumo_abaixo_da_disponibilidade_nao_gera_sistema():
    p = c.carregar_premissas()
    assert c.dimensionar_fv(25, p)["modulos"] == 0


def test_payback_sem_economia_nao_ocorre():
    p = c.carregar_premissas()
    assert c.fluxo_caixa(1000, 0, p)["payback_meses"] is None


def test_combinada_nao_usa_mais_modulos_e_rende_pelo_menos_o_mesmo():
    r = c.comparar()
    assert r["C_eficiencia_mais_solar"]["modulos"] <= r["B_solar"]["modulos"]
    assert r["C_eficiencia_mais_solar"]["ganho_liquido_rs"] >= r["B_solar"]["ganho_liquido_rs"]


def test_assistente_respostas_tem_limitacoes_e_fontes():
    for pergunta in ("quanto eu consumo?", "como economizar?", "vale a pena energia solar?",
                     "compare as alternativas", "quanto de CO2 evito?"):
        r = responder(pergunta, Perfil())
        assert "Limitações" in r and "Fontes" in r, pergunta


def test_assistente_pergunta_desconhecida_mostra_ajuda():
    assert "Posso ajudar" in responder("bom dia", Perfil())


def test_vale_a_pena_solar_vai_para_intencao_solar():
    assert "Energia solar fotovoltaica" in responder("vale a pena energia solar?", Perfil())


def test_pergunta_pc_e_carregador_na_tomada():
    r = responder("Deixar o PC e o carregador na tomada o dia inteiro pesa muito no valor final ou é pouca coisa?", Perfil())
    assert "espera" in r and "Limitações" in r


def test_banho_usa_os_minutos_da_pergunta():
    r = responder("Se eu diminuir uns 5 minutos no meu banho todo dia, quanto isso alivia na conta?", Perfil())
    assert "5 min" in r and "14 kWh" in r  # 5500 W x 5/60 h x 30 = 13,75 kWh


def test_perfil_padrao_bate_com_o_consumo_da_fatura():
    pf = Perfil()
    assert abs(c.consumo_total(pf.equipamentos) - 232) < 1e-6


def test_tarifa_do_usuario_muda_a_resposta():
    p1, p2 = Perfil(), Perfil()
    p2.definir_tarifa(2.0)
    assert responder("compare", p1) != responder("compare", p2)


if __name__ == "__main__":
    falhas = 0
    for nome, fn in list(globals().items()):
        if nome.startswith("test_"):
            try:
                fn()
                print("OK  ", nome)
            except AssertionError as e:
                falhas += 1
                print("FALHA", nome, e)
    sys.exit(1 if falhas else 0)
