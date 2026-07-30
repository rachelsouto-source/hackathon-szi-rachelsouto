"""
Smoke test do núcleo v2 — roda sem rede, sem Drive e sem ANTHROPIC_API_KEY.

Cobre o que é determinístico: Cartógrafo (varredura, pastas vazias, delta), invariantes
do Livro, regras R1/R6.a/R6.b/R10/marinha, changelog entre rodadas e renderização.

    python app/_smoketest_v2.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["AUDITOR_DADOS_DIR"] = tempfile.mkdtemp(prefix="auditor-smoke-")

from auditor import cartografo, estado, regras, relatorio  # noqa: E402
from auditor.livro import (Afirmacao, Evidencia, Livro, PerfilCaso,  # noqa: E402
                           diff_livros)

FALHAS: list[str] = []


def ok(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        FALHAS.append(msg)


# --------------------------------------------------------------------------- #
# Drive falso — reproduz a estrutura real, incluindo a pasta que o v1 não via
# --------------------------------------------------------------------------- #

class DriveFalso:
    def __init__(self, arvore):
        self.arvore = arvore
        self.baixados = []

    def list_files(self, fid):
        return self.arvore.get(fid, [])

    def download_file_by_id(self, fid, mime=""):
        self.baixados.append(fid)
        return b"%PDF-1.4 conteudo", "application/pdf"


def _pasta(i, n):
    return {"id": i, "name": n, "mimeType": "application/vnd.google-apps.folder",
            "webViewLink": f"https://drive/{i}"}


def _arq(i, n, mime="application/pdf", mod="2026-07-23T10:00:00Z", size=2048):
    return {"id": i, "name": n, "mimeType": mime, "webViewLink": f"https://drive/{i}",
            "modifiedTime": mod, "size": str(size)}


ARVORE = {
    "raiz": [_pasta("p02", "02 - Projetos"), _pasta("p05", "05 - Jurídico")],
    "p02": [_pasta("topo", "03 - Levantamento Topográfico"),
            _pasta("amb", "04 - Estudo Ambiental"),
            _pasta("sond", "08 - Sondagem"),
            _pasta("old", "00 - OLD")],
    # A pasta que a whitelist do v1 tornava invisível — origem do caso São Miguel:
    "topo": [_arq("f-prancha", "MCZ_PC_ORIGAMI-SEAZONE.pdf"),
             _pasta("confronto", "06 Confronto SPU")],
    "confronto": [_arq("f-dxf", "CONFRONTO_SPU_x_MCZ.dxf", "application/dxf"),
                  _arq("f-shp", "LPM_trecho.shp", "application/octet-stream"),
                  _arq("f-rel", "relatorio_confronto.pdf")],
    "amb": [],                                    # pasta de template, vazia (R6.a)
    "sond": [],                                   # idem
    "old": [],
    "p05": [_arq("f-mat", "Matricula.pdf"),
            _arq("f-cnd", "CND SPU.pdf"),
            _arq("f-foto", "fachada.jpg", "image/jpeg"),
            _arq("f-tmp", "~$rascunho.docx",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document")],
}


# --------------------------------------------------------------------------- #

def teste_cartografo():
    print("\n[1] Cartógrafo — varredura exaustiva")
    drive = DriveFalso(ARVORE)
    inv = cartografo.varrer("raiz", drive)

    nomes = {a["nome"] for a in inv["arquivos"]}
    ok("relatorio_confronto.pdf" in nomes,
       "enxerga a pasta '06 Confronto SPU' (invisível para a whitelist do v1)")
    ok("CONFRONTO_SPU_x_MCZ.dxf" in nomes, "inclui o DXF no inventário")
    ok(inv["total_arquivos"] == 8, f"8 arquivos varridos (achou {inv['total_arquivos']})")

    dxf = next(a for a in inv["arquivos"] if a["nome"].endswith(".dxf"))
    ok(dxf["situacao"] == "requer_ferramenta", "DXF marcado como 'requer_ferramenta'")
    tmp = next(a for a in inv["arquivos"] if a["nome"].startswith("~$"))
    ok(tmp["situacao"] == "nao_aplicavel", "temporário marcado como não aplicável")
    foto = next(a for a in inv["arquivos"] if a["nome"].endswith(".jpg"))
    ok(foto["situacao"] == "nao_aplicavel", "imagem marcada como não aplicável")

    mat = next(a for a in inv["arquivos"] if a["nome"] == "Matricula.pdf")
    ok(mat["disciplina"] == "jurídico-cartorial", "matrícula classificada como jurídica")
    pr = next(a for a in inv["arquivos"] if a["nome"].startswith("MCZ_PC"))
    ok(pr["disciplina"] == "topografia", "prancha classificada como topografia")

    vaz = set(inv["pastas_vazias"])
    ok(any("Estudo Ambiental" in v for v in vaz), "detecta pasta ambiental VAZIA (R6.a)")
    ok(any("Sondagem" in v for v in vaz), "detecta pasta sondagem VAZIA (R6.a)")
    return inv


def teste_delta(inv):
    print("\n[2] Delta entre rodadas")
    emp = "TESTE"
    d1 = cartografo.calcular_delta(emp, inv)
    ok(d1["primeira_varredura"], "primeira varredura identificada")
    estado.gravar_manifest(emp, cartografo.manifest_de(inv))

    d2 = cartografo.calcular_delta(emp, inv)
    ok(not d2["houve_mudanca"], "segunda varredura sem mudança não acusa delta")

    arv = {k: list(v) for k, v in ARVORE.items()}
    arv["sond"] = [_arq("f-spt", "Sondagem SPT.pdf", mod="2026-07-29T09:00:00Z")]
    arv["p05"] = [a for a in arv["p05"] if a["id"] != "f-cnd"]
    inv3 = cartografo.varrer("raiz", DriveFalso(arv))
    d3 = cartografo.calcular_delta(emp, inv3)
    ok(len(d3["novos"]) == 1 and d3["novos"][0]["nome"] == "Sondagem SPT.pdf",
       "detecta documento NOVO")
    ok(d3["removidos"] == ["f-cnd"], "detecta documento REMOVIDO")
    ok(not inv3["pastas_vazias"] or not any("Sondagem" in v for v in inv3["pastas_vazias"]),
       "pasta de sondagem deixa de ser vazia após a entrega")


def teste_invariantes():
    print("\n[3] Invariantes do Livro")
    a_sem = Afirmacao(id="A1", disciplina="ambiental", texto="APP no terreno")
    ok(len(a_sem.valida()) > 0, "afirmação sem evidência é rejeitada pela validação")

    a_com = Afirmacao(
        id="A2", disciplina="ambiental", texto="APP de manguezal a 30 m",
        evidencias=[Evidencia(origem="documento_emp", ref="f-rel",
                              trecho="interseção de 127,90 m² com manguezal",
                              localizacao="p. 3", fonte_declarada_pelo_doc="EVA 2026")])
    ok(a_com.valida() == [], "afirmação com evidência válida passa")

    ev_nome = Afirmacao(id="A3", disciplina="topografia", texto="x",
                        evidencias=[Evidencia(origem="documento_emp", ref="f1", trecho="")])
    ok(any("trecho" in e for e in ev_nome.valida()),
       "nome de arquivo sem trecho literal não é evidência")

    # Teto de confiança: Diário não sustenta 'alta'
    a_diario = Afirmacao(
        id="A4", disciplina="urbanístico", texto="Alvarás suspensos", confianca="alta",
        evidencias=[Evidencia(origem="diario", ref="anc:slack:X:y",
                              trecho="Estão suspensos novos alvarás no SOUS")])
    ok(a_diario.confianca_efetiva() == "media",
       "evidência de Diário rebaixa confiança 'alta' para 'media'")

    # Subgrafo de dependências
    lv = Livro(emp_id="T", nome="T")
    lv.afirmacoes = [
        Afirmacao(id="B1", disciplina="topografia", texto="base",
                  evidencias=[Evidencia(origem="documento_emp", ref="f", trecho="t")]),
        Afirmacao(id="B2", disciplina="topografia", texto="dep1", depende_de=["B1"],
                  evidencias=[Evidencia(origem="documento_emp", ref="f", trecho="t")]),
        Afirmacao(id="B3", disciplina="topografia", texto="dep2", depende_de=["B2"],
                  evidencias=[Evidencia(origem="documento_emp", ref="f", trecho="t")]),
        Afirmacao(id="B4", disciplina="ambiental", texto="solta",
                  evidencias=[Evidencia(origem="documento_emp", ref="f", trecho="t")]),
    ]
    ok(lv.dependentes_de("B1") == ["B2", "B3"],
       "fecho transitivo de dependências (contestar B1 reabre B2 e B3, não B4)")


def _livro_base(inv, rodada=1) -> Livro:
    lv = Livro(
        emp_id="TESTE", nome="Empreendimento Teste", rodada=rodada,
        gerado_em="2026-07-29T18:00:00+00:00",
        perfil=PerfilCaso(emp_id="TESTE", nome="Empreendimento Teste",
                          cidade="São Miguel dos Milagres", uf="AL",
                          regime_dominial="ocupação", flags=["marinha", "APP"]),
        cobertura=cartografo.cobertura(inv, {"f-mat", "f-prancha"}),
        proveniencia={"areas_tabela": {
            "matricula": [{"ref": "Matrícula 2.007", "area": "8.573,00 m²"}],
            "topografico": "8.656,71 m²"}},
    )
    lv.afirmacoes = [
        Afirmacao(
            id="AF-001", disciplina="topografia", severidade="Crítico", tipo="fato",
            texto="O levantamento indica que o lote não intercepta a área de marinha.",
            evidencias=[Evidencia(
                origem="documento_emp", ref="f-prancha",
                trecho="Área da União segundo LPM atual: não interceptado",
                localizacao="prancha, quadro de notas",
                fonte_declarada_pelo_doc=None)]),   # ← dispara R10
        Afirmacao(
            id="AF-002", disciplina="ambiental", severidade="Atenção", tipo="fato",
            texto="Interseção de 127,90 m² com manguezal (APP).",
            evidencias=[Evidencia(
                origem="documento_emp", ref="f-rel", trecho="127,90 m² de manguezal",
                localizacao="p. 3", fonte_declarada_pelo_doc="EVA/2026")]),
        Afirmacao(
            id="AF-003", disciplina="jurídico-cartorial", severidade="Crítico",
            tipo="fato", texto="Patacho perdeu o terreno por área de marinha.",
            evidencias=[Evidencia(
                origem="base_historica", ref="A-2291",
                trecho="área de marinha maior que a estimada; terreno perdido")]),
    ]
    return lv


def teste_regras(inv):
    print("\n[4] Regras determinísticas")
    lv = _livro_base(inv)
    disparos = regras.aplicar(lv)
    txt = " | ".join(disparos)

    ok(any(a.regra == "R10" for a in lv.afirmacoes),
       f"R10 dispara em documento sem fonte declarada ({txt[:60]}…)")
    ok(not [a for a in lv.afirmacoes if a.regra == "R1"],
       "R1 NÃO dispara abaixo de 3% (0,98% no caso) — sem falso positivo")
    ok(not any("erro ao aplicar" in d for d in disparos),
       f"nenhuma regra falhou ao aplicar ({txt[:70]})")

    ok(any(a.regra == "R6.b" for a in lv.afirmacoes),
       "R6.b dispara para documentos relevantes não lidos")
    ok(any(a.regra == "R6.a" for a in lv.afirmacoes),
       "R6.a dispara para pastas de template vazias")
    ok(any("SPU" in a.id for a in lv.afirmacoes),
       "marinha sem consulta à SPU vira lacuna crítica")

    af3 = lv.por_id("AF-003")
    ok(af3.tipo == "precedente",
       "precedente da base histórica é reclassificado — não é fato sobre este terreno")

    # R1 com divergência real (>3%)
    lv2 = _livro_base(inv)
    lv2.proveniencia["areas_tabela"] = {
        "matricula": [{"ref": "M", "area": "8.573,00 m²"}], "topografico": "9.200,00 m²"}
    regras.aplicar(lv2)
    ok(any(a.regra == "R1" for a in lv2.afirmacoes),
       "R1 dispara acima de 3% (9.200 vs 8.573 = 7,3%)")
    return lv


def teste_changelog(inv, lv1):
    print("\n[5] Changelog entre rodadas")
    d0 = diff_livros(None, lv1)
    ok(d0["primeira_rodada"], "primeira rodada identificada")

    lv2 = _livro_base(inv, rodada=2)
    lv2.afirmacoes[1].severidade = "Crítico"          # AF-002 agrava
    lv2.afirmacoes.pop(0)                              # AF-001 desaparece
    lv2.afirmacoes.append(Afirmacao(
        id="AF-010", disciplina="engenharia", severidade="Crítico", tipo="fato",
        texto="Sondagem indica nível d'água a 0,8 m.",
        evidencias=[Evidencia(origem="documento_emp", ref="f-spt",
                              trecho="NA a 0,80 m", localizacao="p. 1",
                              fonte_declarada_pelo_doc="NBR 6484")]))
    regras.aplicar(lv2)

    d = diff_livros(lv1, lv2)
    ok(any("nível d'água" in x["texto"] for x in d["novos"]), "detecta achado NOVO")
    ok(any(x["id"] == "AF-002" for x in d["agravados"]),
       "detecta achado AGRAVADO (Atenção → Crítico)")
    ok(any("marinha" in x["texto"].lower() for x in d["fechados"]),
       "detecta achado FECHADO")


def teste_persistencia(inv, lv1):
    print("\n[6] Persistência e histórico")
    estado.gravar_livro(lv1)
    lido = estado.ler_livro("TESTE", 1)
    ok(lido is not None, "Livro grava e relê do disco")
    ok(lido.afirmacoes[0].evidencias[0].trecho == lv1.afirmacoes[0].evidencias[0].trecho,
       "evidências sobrevivem ao round-trip de serialização")
    ok(estado.proxima_rodada("TESTE") == 2, "próxima rodada é calculada corretamente")
    ok(len(estado.historico("TESTE")) == 1, "histórico lista a rodada gravada")


def teste_render(inv, lv1):
    print("\n[7] Renderização")
    md = relatorio.render_markdown(lv1, diff_livros(None, lv1))
    ok("Cobertura documental" in md, "parecer traz a seção de cobertura documental")
    ok("Lacunas e o que falta" in md, "parecer traz a seção de lacunas")
    ok("Precedentes consultados" in md, "parecer traz a seção de precedentes")
    ok("decisão humana" in md, "parecer declara que GO/NO-GO é decisão humana")
    ok("Recomendação:" not in md,
       "não emite linha de recomendação automática (GO/NO-GO é do humano — §12.3)")
    ok("Exposição técnica" in md, "emite exposição técnica no lugar da recomendação")
    ok("não declara a própria fonte" in md, "marca visualmente a violação de R10")
    ok("06 Confronto SPU" in md, "cobertura cita a pasta que o v1 não enxergava")

    r = relatorio.resumo_api(lv1)
    ok(r["contadores"]["criticos"] >= 1, "resumo conta achados críticos")
    ok(r["contadores"]["lacunas"] >= 1, "resumo conta lacunas")
    ok(all("evidencias" in a for a in r["achados"]), "resumo expõe evidências por achado")


def teste_diario_parse():
    print("\n[8] Parser do Diário")
    from auditor.fontes.diario import parse
    md = """# 📋 DIÁRIO — [12235] São Miguel

## Painel
- **Fase atual:** Vem aí

## ⚠️ Riscos / Pontos de atenção

### 💬 #juridico-sao-miguel · `25/07/2026` · [link](https://slack.com/p123)
- Estão suspensos novos alvarás no SOUS da Praia do Toque. <!--anc:slack:C0BE:estao-suspensos-->
- MPF orientou o IMA/AL a segurar licenças. <!--anc:slack:C0BE:mpf-orientou-->
"""
    d = parse(md)
    ok(len(d["eventos"]) == 2, "extrai os dois eventos de risco")
    e = d["eventos"][0]
    ok(e["ancora"] == "anc:slack:C0BE:estao-suspensos", "captura a âncora estável")
    ok(e["link"] == "https://slack.com/p123", "captura o link da fonte")
    ok(e["data"] == "25/07/2026", "captura a data")
    ok("<!--" not in e["texto"], "remove o comentário HTML do texto citável")


def teste_precedentes():
    """
    Ranqueamento multi-critério com dados no schema REAL de engine/schema.py.

    Não bate na planilha (exige service account) — injeta fixture no cache. O que se
    verifica é a LÓGICA: que o peso muda por disciplina, que distância geográfica
    domina em engenharia, que regime dominial domina em jurídico-cartorial, e que o
    canal de negativos vem separado em vez de diluído no ranking.
    """
    print("\n[9] Recuperação de precedentes")
    import os as _os
    _os.environ["BASE_SHEET_ID"] = "fixture"
    _os.environ["AUDITOR_COORDS"] = ("0584:-9.2361,-35.2372;2595:-27.6786,-48.4897;"
                                     "12235:-9.2789,-35.3897")
    from auditor.fontes import historica as h
    h.limpar_cache()
    h._CACHE["sintese"] = [
        {"empreendimento": "Japaratinga", "emp_id": "0584", "cidade": "Japaratinga, AL",
         "uf": "AL", "disciplina": "jurídico-cartorial", "categoria": "gargalo",
         "sintese": ("Terreno de marinha em regime de ocupação; a transferência exigiu "
                     "anuência da SPU."),
         "linhas_ref": "A-1,A-2"},
        {"empreendimento": "Campeche Spot", "emp_id": "2595", "cidade": "Florianópolis, SC",
         "uf": "SC", "disciplina": "jurídico-cartorial", "categoria": "acerto",
         "sintese": "Cadeia dominial limpa.", "linhas_ref": "A-3"},
        {"empreendimento": "Japaratinga", "emp_id": "0584", "cidade": "Japaratinga, AL",
         "uf": "AL", "disciplina": "engenharia", "categoria": "conhecimento-geral",
         "sintese": "Areia fofa até 6 m, NA a 1,2 m.", "linhas_ref": "A-5"},
    ]
    h._CACHE["aprendizados"] = [
        {"id": "A-1", "empreendimento": "Japaratinga", "emp_id": "0584",
         "cidade": "Japaratinga, AL", "uf": "AL", "disciplina": "jurídico-cartorial",
         "categoria": "gargalo", "tema": "terreno de marinha",
         "resumo": "Área da União maior que a estimada.",
         "desfecho": "Renegociação; atraso de 5 meses.", "link": "https://drive/A1"},
        {"id": "A-2", "empreendimento": "Japaratinga", "emp_id": "0584",
         "cidade": "Japaratinga, AL", "uf": "AL", "disciplina": "jurídico-cartorial",
         "categoria": "erro", "tema": "laudêmio", "resumo": "Laudêmio não orçado.",
         "desfecho": "Custo extra absorvido.", "link": "https://drive/A2"},
        {"id": "A-5", "empreendimento": "Japaratinga", "emp_id": "0584",
         "cidade": "Japaratinga, AL", "uf": "AL", "disciplina": "engenharia",
         "categoria": "conhecimento-geral", "tema": "sondagem",
         "resumo": "Areia fofa até 6 m.", "desfecho": "Estaca hélice.",
         "link": "https://drive/A5"},
    ]

    perfil = PerfilCaso(emp_id="12235", nome="São Miguel dos Milagres",
                        cidade="São Miguel dos Milagres", uf="AL",
                        lat=-9.2789, lon=-35.3897, regime_dominial="ocupação",
                        flags=["marinha"])

    r = h.buscar(perfil, "jurídico-cartorial")
    nomes = [p["empreendimento"] for p in r["precedentes"]]
    ok(nomes and nomes[0] == "Japaratinga",
       f"AL/17 km/mesmo regime vence SC/2.464 km (ordem: {nomes})")
    jap = r["precedentes"][0]
    camp = next(p for p in r["precedentes"] if p["emp_id"] == "2595")
    ok(jap["score"] > camp["score"] * 10,
       f"score separa bem os dois ({jap['score']} × {camp['score']})")
    ok("mesmo regime dominial" in jap["por_que_este"],
       f"explica POR QUE foi escolhido ({jap['por_que_este']})")

    # O critério de regime é substring em texto livre — heurística, não campo estruturado.
    # Este teste fixa o comportamento e documenta a fragilidade: síntese que não NOMEIA o
    # regime não pontua por ele, mesmo sendo o mesmo regime na prática.
    perfil_sem = PerfilCaso(emp_id="12235", nome="x", cidade="São Miguel dos Milagres",
                            uf="AL", lat=-9.2789, lon=-35.3897,
                            regime_dominial="enfiteuse")
    r_sem = h.buscar(perfil_sem, "jurídico-cartorial")
    ok(r_sem["precedentes"][0]["score"] < jap["score"],
       "regime que não casa pontua menos — o critério realmente pesa")

    ok(len(r["negativos"]) == 2,
       "canal de negativos traz os 2 casos ruins, separado do ranking")
    ok(all(n["desfecho"] for n in r["negativos"]),
       "negativos carregam o DESFECHO — é o que dá peso ao precedente")
    ok(all(n["link"] for n in r["negativos"]), "negativos carregam link verificável")

    r2 = h.buscar(perfil, "engenharia")
    ok(r2["precedentes"] and r2["precedentes"][0]["granulares"],
       "desce da síntese para as granulares via linhas_ref")

    r3 = h.buscar(perfil, "incêndio")
    ok(not r3["encontrado"] and r3.get("declaracao_de_ausencia"),
       "ausência de precedente é DECLARADA, não silenciosa")

    perfil_proprio = PerfilCaso(emp_id="0584", nome="Japaratinga", uf="AL")
    r4 = h.buscar(perfil_proprio, "jurídico-cartorial")
    ok(all(p["emp_id"] != "0584" for p in r4["precedentes"]),
       "empreendimento não é precedente de si mesmo")


def teste_diario_real():
    """Conector do Diário contra o repositório de verdade, se ele estiver por perto."""
    print("\n[10] Diário — repositório real")
    from auditor.fontes import diario as d
    disp, msg = d.disponivel()
    if not disp:
        print(f"  ⏭️  pulado — {msg[:80]}")
        return
    emps = d.listar_empreendimentos()
    ok(bool(emps), f"encontra diários no repo ({len(emps)} empreendimentos)")
    alvo = next((e.split("-")[0] for e in emps), None)
    if not alvo:
        return
    r = d.consultar(alvo, secao="riscos")
    ok(r.get("encontrado"), f"lê o diário do {alvo}")
    ok(r.get("total_eventos", 0) > 0, f"extrai eventos ({r.get('total_eventos')})")
    evs = r.get("eventos") or []
    if evs:
        ok(any(e["ancora"] for e in evs), "eventos trazem âncora estável (citação exata)")
        ok(any(e["link"] for e in evs), "eventos trazem link para reunião/Slack")
        ok(all("<!--" not in e["texto"] for e in evs),
           "texto citável limpo, sem comentário HTML")


def main():
    print("=" * 74)
    print("SMOKE TEST — Auditor de DD Técnica v2 (offline)")
    print("=" * 74)
    inv = teste_cartografo()
    teste_delta(inv)
    teste_invariantes()
    lv1 = teste_regras(inv)
    teste_changelog(inv, lv1)
    teste_persistencia(inv, lv1)
    teste_render(inv, lv1)
    teste_diario_parse()
    teste_precedentes()
    teste_diario_real()

    print("\n" + "=" * 74)
    if FALHAS:
        print(f"❌ {len(FALHAS)} FALHA(S):")
        for f in FALHAS:
            print(f"   · {f}")
        return 1
    print("✅ Todos os testes passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
