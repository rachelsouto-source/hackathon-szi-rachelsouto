"""
Fontes externas — SPU, geoprocessamento e legislação.

PRINCÍPIO INEGOCIÁVEL (§7, "regra de honestidade"):
ferramenta que falha ou que exige credencial humana NÃO degrada em silêncio para
inferência. Ela devolve um PEDIDO AO HUMANO, explícito. Um agente que finge ter
consultado o cadastro da SPU é pior do que um que declara a lacuna — e essa preferência
foi manifestada na revisão ("ele dá sugestões que não fazem sentido", 38:29).

Estado real de cada canal SPU, verificado em 29/07/2026:

| Canal                                   | Automatizável | Observação                                  |
|-----------------------------------------|---------------|---------------------------------------------|
| GeoPortal SPUNET (shapefiles LPM/LTM/TM)| SIM           | canal que funcionou no 12235                |
| geoportal.spu.gestao.gov.br             | NÃO           | fora do ar (525)                            |
| Consultar Dados Cadastrais de Imóvel    | NÃO           | exige login gov.br Bronze+ e reCAPTCHA      |
| Consultar Histórico Financeiro          | NÃO           | idem                                        |
| Qlik Transparência Ativa / dados.gov.br | NÃO           | cobrem uso especial, não ocupação privada   |

Isto é material: o número que disparou o alerta do São Miguel — a área da União no
cadastro — vem justamente da consulta que exige login humano.
"""
from __future__ import annotations

import re
from typing import Any

RE_RIP = re.compile(r"\b(\d{4})[.\s-]?(\d{7})[-.\s]?(\d{2})\b")

PORTAL_SPU = "https://sistema.patrimoniodetodos.gov.br"
GEOPORTAL_SPUNET = "https://geoportal.spunet.gestao.gov.br"


def normalizar_rip(txt: str) -> str | None:
    m = RE_RIP.search(txt or "")
    return f"{m.group(1)}.{m.group(2)}-{m.group(3)}" if m else None


def consultar_spu(rip: str, o_que: str = "cadastro") -> dict[str, Any]:
    """
    `o_que` ∈ {"cadastro", "financeiro", "camadas", "tudo"}.

    Devolve sempre o que é automatizável + os pedidos ao humano do que não é.
    """
    rip_n = normalizar_rip(rip) or rip
    pedidos: list[dict] = []
    automatico: dict[str, Any] = {}

    if o_que in ("cadastro", "tudo"):
        pedidos.append({
            "o_que_preciso": f"Consulta de Dados Cadastrais do imóvel da União, RIP {rip_n}",
            "para_que": ("Obter a ÁREA da União no cadastro, a natureza do terreno "
                         "(marinha / marinha com acrescido / alodial) e a situação de "
                         "ocupação. Sem isso não é possível dimensionar a exposição "
                         "dominial nem confrontar cadastro × geometria."),
            "onde": f"{PORTAL_SPU} → 'Consultar Dados Cadastrais de Imóvel da União'",
            "por_que_nao_automatico": ("Exige login gov.br nível Bronze ou superior e "
                                       "resolução de reCAPTCHA. O formulário renderiza "
                                       "vazio sem autenticação."),
            "custo": "grátis, atendimento imediato",
            "quem_pode": "qualquer pessoa do time com conta gov.br Bronze+",
        })

    if o_que in ("financeiro", "tudo"):
        pedidos.append({
            "o_que_preciso": f"Histórico Financeiro do imóvel da União, RIP {rip_n}",
            "para_que": ("Obter a taxa de ocupação anual lançada. Dela sai o VDP "
                         "(VDP = taxa ÷ 5% para ocupações posteriores a 30/09/1988; "
                         "÷ 2% se anterior — DL 2.398/1987 art. 1º) e, do VDP, o R$/m² e "
                         "o laudêmio (5% sobre VDP do terreno + benfeitorias, art. 3º)."),
            "onde": f"{PORTAL_SPU} → 'Consultar Histórico Financeiro de Imóvel da União'",
            "por_que_nao_automatico": "Mesma barreira de autenticação gov.br + captcha.",
            "custo": "grátis, atendimento imediato",
            "quem_pode": "qualquer pessoa do time com conta gov.br Bronze+",
        })

    if o_que in ("camadas", "tudo"):
        automatico["camadas"] = {
            "fonte": "GeoPortal SPUNET",
            "url": GEOPORTAL_SPUNET,
            "situacao": "canal disponível (validado no 12235 em 29/07/2026)",
            "o_que_traz": [
                "LPM — Linha de Preamar Média (a de 1831, que é a que a lei usa)",
                "LTM — Linha Limite de Terrenos de Marinha",
                "Polígono de Terreno de Marinha",
                "ATRIBUTOS das feições: trecho, situação da demarcação, data de aprovação",
            ],
            "atencao_critica": (
                "A situação de homologação é POR TRECHO, não por município: há trechos "
                "homologados e trechos com demarcação inconclusa. Ler o atributo da "
                "feição, não presumir. (Revisão de 29/07, 03:50 e 05:01.)"),
            "premissa_legal": (
                "Terreno de marinha se define pela preamar-média de 1831 "
                "(DL 9.760/1946, art. 2º) — NÃO pela maré atual. Levantamento que traça "
                "a 'LPM atual' está sobre premissa errada, ainda que metricamente "
                "impecável. Foi exatamente o erro da prancha da MCZ no 12235."),
            "como_obter": (
                "Baixar os shapefiles do trecho pelo GeoPortal SPUNET e salvá-los na "
                "pasta do empreendimento; a partir daí o confronto geométrico é local."),
        }

    return {
        "rip": rip_n,
        "automatico": automatico,
        "pedidos_ao_humano": pedidos,
        "resumo": (
            f"RIP {rip_n}: "
            + ("camadas geoespaciais disponíveis via SPUNET. " if automatico else "")
            + (f"{len(pedidos)} consulta(s) exigem login gov.br — registrar como LACUNA, "
               f"nunca estimar." if pedidos else "")),
    }


def orientacao_geoprocessamento() -> dict[str, Any]:
    """
    Técnica validada para confrontar prancha topográfica × demarcação oficial.

    Registrada aqui porque foi provada no 12235 e não deve virar folclore de sessão:
    o PDF da MCZ preservou as 27 camadas CAD como OCGs; parseando o content stream
    (blocos BDC/EMC + matriz CTM) dá para separar a geometria por camada, e
    georreferenciando pelos 15 vértices UTM da tabela da prancha (Procrustes) o resíduo
    foi de 1,4 cm.
    """
    return {
        "tecnica": "parsing de OCGs do PDF CAD + georreferenciamento por Procrustes",
        "quando_usar": ("toda prancha topográfica — revela o que a prancha DESENHOU "
                        "versus o que ela AFIRMA, e dispensa o DWG"),
        "cuidados": [
            "Conferir a escala real: pranchas declaram uma escala e são plotadas em outra "
            "(no 12235: declarava 1:1100, estava em 1:1150 — 4,3% em distância, 8,8% em área).",
            "Nunca medir sobre o PDF; a tabela de coordenadas é a fonte confiável.",
            "Validar a área por Gauss contra a área declarada antes de usar qualquer número.",
        ],
        "status": ("scripts existem como prova de conceito; promover a ferramenta do "
                   "Auditor é item da Fase 3 do roadmap (§15)."),
    }


def orientacao_legislacao(municipio: str, uf: str) -> dict[str, Any]:
    """
    ⚠️ Lacuna conhecida e assumida: só há base estruturada de legislação para
    Florianópolis (repositório MVP Floripa). Fora dali, a legislação tem de vir de busca
    web sobre texto primário, com verificação de vigência.

    Foi dito na revisão, 20:46: "para Milagres ela não vai ter" / "não vai ter nível Brasil".
    """
    m = (municipio or "").strip().lower()
    tem_base = "florian" in m
    return {
        "municipio": municipio, "uf": uf,
        "tem_base_estruturada": tem_base,
        "fonte": ("repositório MVP Legislação Florianópolis" if tem_base
                  else "sem base estruturada — usar busca web sobre texto primário"),
        "regra_inviolavel": (
            "NUNCA citar lei ou parâmetro de memória. A fonte primária do zoneamento é a "
            "Viabilidade Técnica Construtiva emitida para o terreno; a legislação é "
            "fundamento, e a vigência se reconfere a cada DD."),
        "o_que_verificar": [
            "vigência do dispositivo na data da análise",
            "se houve alteração posterior (LC/decreto revogador)",
            "regra de transição por data de protocolo, quando houver",
        ],
    }
