"""
Ferramentas do agente — o capítulo que no v1 era um CONJUNTO VAZIO.

`dd_engine.audit()` fazia uma única `messages.create` sem `tools`. O modelo não deixava
de investigar: ele não tinha o verbo. Não era falha de prompt, era falha de arquitetura.

Toda chamada de ferramenta é registrada em `Contexto.chamadas` e vira Evidência com
timestamp e parâmetros. É isso que permite (a) ao agente saber o que já tentou — critério
de parada; (b) ao humano auditar o caminho percorrido (§7, "regra que vale para todas").
"""
from __future__ import annotations

import base64
import datetime as _dt
import json
import os as _os
from dataclasses import dataclass, field
from typing import Any

from . import cartografo
from .fontes import diario as fdiario
from .fontes import externas as fexternas
from .fontes import historica as fhistorica
from .fontes import legislacao as flegislacao

MAX_DOCS_LIDOS = 40
MAX_BYTES_DOC = 28 * 1024 * 1024      # limite prático de document block
MAX_BYTES_SESSAO = 90 * 1024 * 1024


def agora() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


@dataclass
class Contexto:
    """Estado compartilhado entre as ferramentas durante uma auditoria."""
    emp_id: str
    nome: str
    inventario: dict
    perfil: Any                        # livro.PerfilCaso
    drive: Any                         # módulo core.drive_client (injetável em teste)
    lidos: set[str] = field(default_factory=set)
    chamadas: list[dict] = field(default_factory=list)
    pedidos_ao_humano: list[dict] = field(default_factory=list)
    bytes_gastos: int = 0
    # Preenchido por consultar_legislacao — usado pela regra que confere se a evidência
    # de legislação veio de domínio oficial.
    dominios_legislacao: list[str] = field(default_factory=list)

    def registrar(self, nome: str, args: dict, resumo: str) -> None:
        self.chamadas.append({"ferramenta": nome, "args": args,
                              "em": agora(), "resumo": resumo[:400]})

    def ja_tentou(self, nome: str, **args) -> bool:
        return any(c["ferramenta"] == nome and all(c["args"].get(k) == v
                   for k, v in args.items()) for c in self.chamadas)


# --------------------------------------------------------------------------- #
# Ferramentas DE SERVIDOR — executadas pela Anthropic, não por nós
# --------------------------------------------------------------------------- #

MAX_BUSCAS_WEB = int(_os.getenv("DD_MAX_BUSCAS_WEB", "12"))
MAX_FETCH_WEB = int(_os.getenv("DD_MAX_FETCH_WEB", "12"))

# Nomes das ferramentas de servidor: aparecem na resposta como `server_tool_use` +
# `*_tool_result`, e NÃO devem ser despachadas por `executar()` — a Anthropic já as rodou.
NOMES_SERVIDOR = {"web_search", "web_fetch"}


def schemas_servidor() -> list[dict]:
    """
    Dá ao agente acesso a sites de prefeitura e a texto legal primário.

    Sem isto, "analisar a legislação do lugar" fica só no discurso: fora de Florianópolis
    não existe base estruturada (revisão de 29/07, 20:46), então a única forma de ler a
    lei do município é ir ao site oficial.

    `web_fetch` só busca URLs JÁ PRESENTES na conversa — na prática ele lê o que a
    `web_search` (ou o `consultar_legislacao`) trouxe. Os dois vêm com filtragem dinâmica
    embutida, que roda execução de código por baixo: por isso NÃO declaramos
    `code_execution` junto — dois ambientes de execução confundem o modelo.
    """
    return [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": MAX_BUSCAS_WEB},
        {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": MAX_FETCH_WEB,
         "citations": {"enabled": True}},
    ]


# --------------------------------------------------------------------------- #
# Schemas expostos ao modelo
# --------------------------------------------------------------------------- #

def schemas() -> list[dict]:
    return [
        {
            "name": "ler_documento",
            "description": (
                "Lê um documento da pasta do empreendimento. PDFs e imagens são entregues "
                "nativamente ao modelo. Use para QUALQUER arquivo do inventário cuja "
                "situação seja 'a_ler'. Informe sempre o motivo — ele fica registrado na "
                "trilha de auditoria."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "id do arquivo no inventário"},
                    "motivo": {"type": "string",
                               "description": "o que você espera extrair deste documento"},
                },
                "required": ["file_id", "motivo"],
            },
        },
        {
            "name": "listar_arvore",
            "description": (
                "Relista a árvore de arquivos do empreendimento, opcionalmente filtrada. "
                "Use quando o inventário inicial foi truncado ou quando procura algo "
                "específico por nome/pasta/disciplina."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "filtro": {"type": "string",
                               "description": "texto a casar em nome ou caminho"},
                    "disciplina": {"type": "string", "enum": [
                        "ambiental", "urbanístico", "concessionárias", "incêndio",
                        "sanitário", "patrimônio", "jurídico-cartorial", "topografia",
                        "arquitetura-projeto", "engenharia", "negócio"]},
                    "apenas_nao_lidos": {"type": "boolean"},
                },
            },
        },
        {
            "name": "buscar_precedentes",
            "description": (
                "Busca casos anteriores da Seazone na base histórica de DD Técnica. "
                "USE SEMPRE que identificar um tema relevante (área de marinha, APP, "
                "supressão vegetal, alvará de demolição, sondagem, exigência de órgão). "
                "Devolve os empreendimentos mais comparáveis por cidade/estado/distância/"
                "regime dominial/produto, MAIS um canal separado de casos que deram errado. "
                "Precedente NUNCA é fato sobre este terreno — é recomendação."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "disciplina": {"type": "string", "enum": [
                        "ambiental", "urbanístico", "concessionárias", "incêndio",
                        "sanitário", "patrimônio", "jurídico-cartorial", "topografia",
                        "arquitetura-projeto", "engenharia", "negócio"]},
                    "tema": {"type": "string",
                             "description": "ex.: 'terreno de marinha', 'alvará de demolição'"},
                },
                "required": ["disciplina"],
            },
        },
        {
            "name": "consultar_diario",
            "description": (
                "Consulta o Diário de Lançamentos: riscos, decisões e preocupações que o "
                "time registrou em reuniões e no Slack sobre ESTE empreendimento. "
                "USE SEMPRE, no início da auditoria. Traz coisas que não estão em documento "
                "nenhum (suspensão de alvarás, ação do MP, atrasos reais). "
                "Teto de confiança MÉDIA: gera pergunta e corrobora — não conclui sozinho."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "termo": {"type": "string", "description": "filtro opcional"},
                    "secao": {"type": "string", "enum": ["riscos", "decisoes", "timeline"]},
                },
            },
        },
        {
            "name": "consultar_spu",
            "description": (
                "Consulta a situação de terreno de marinha a partir do RIP. USE SEMPRE que "
                "encontrar um RIP, menção a terreno de marinha, aforamento ou ocupação. "
                "Devolve o que é obtenível automaticamente (camadas do GeoPortal SPUNET, "
                "com o atributo de homologação POR TRECHO) e devolve PEDIDO AO HUMANO para "
                "o que exige login gov.br (área cadastral e taxa de ocupação). "
                "Nunca estime esses números: registre como lacuna."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "rip": {"type": "string"},
                    "o_que": {"type": "string",
                              "enum": ["cadastro", "financeiro", "camadas", "tudo"]},
                },
                "required": ["rip"],
            },
        },
        {
            "name": "consultar_legislacao",
            "description": (
                "Mapa da legislação do município: portais OFICIAIS onde procurar, leis-chave "
                "já conhecidas, armadilhas recorrentes e o checklist do que perguntar. "
                "CHAME ISTO ANTES de sair pesquisando na web — ele diz em quais domínios a "
                "resposta é confiável. Depois use web_search/web_fetch nesses domínios para "
                "ler o TEXTO PRIMÁRIO. Existe base estruturada apenas para Florianópolis."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "municipio": {"type": "string"},
                    "uf": {"type": "string"},
                    "tema": {"type": "string",
                             "description": "zoneamento, outorga, incentivos, licenciamento, "
                                            "eiv, esgoto, ambiental, patrimonio, bombeiro, "
                                            "vigencia — ou vazio para o checklist todo"},
                },
                "required": ["municipio"],
            },
        },
        {
            "name": "pedir_ao_humano",
            "description": (
                "Registra que você PRECISA de algo que não consegue obter e que sem isso "
                "não é possível fechar uma conclusão. Use em vez de estimar, presumir ou "
                "sugerir. É preferível uma lacuna bem declarada a um palpite plausível."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "o_que_preciso": {"type": "string"},
                    "para_que": {"type": "string",
                                 "description": "que conclusão isso destrava"},
                    "como_obter": {"type": "string"},
                    "bloqueia": {"type": "string",
                                 "description": "o que fica indeterminado sem isso"},
                },
                "required": ["o_que_preciso", "para_que"],
            },
        },
        {
            "name": "concluir_investigacao",
            "description": (
                "Encerra a fase de investigação. Só chame quando: (a) leu todo documento "
                "relevante do inventário; (b) buscou precedentes para cada disciplina "
                "ativa; (c) consultou o Diário; (d) as lacunas restantes dependem de "
                "terceiros ou de credencial humana, e você já as registrou."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "resumo": {"type": "string",
                               "description": "o que investigou e o que ficou em aberto"},
                },
                "required": ["resumo"],
            },
        },
    ]


# --------------------------------------------------------------------------- #
# Execução
# --------------------------------------------------------------------------- #

def executar(nome: str, args: dict, ctx: Contexto) -> tuple[str, list[dict]]:
    """
    Devolve (texto_do_resultado, blocos_extra).

    `blocos_extra` são content blocks (document/image) que precisam ir no MESMO turno de
    usuário, logo após o tool_result — é assim que um PDF chega nativamente ao modelo.
    """
    try:
        if nome == "ler_documento":
            return _ler_documento(args, ctx)
        if nome == "listar_arvore":
            return _listar_arvore(args, ctx), []
        if nome == "buscar_precedentes":
            return _precedentes(args, ctx), []
        if nome == "consultar_diario":
            return _diario(args, ctx), []
        if nome == "consultar_spu":
            return _spu(args, ctx), []
        if nome == "consultar_legislacao":
            return _legislacao(args, ctx), []
        if nome == "pedir_ao_humano":
            return _pedido(args, ctx), []
        return f"Ferramenta desconhecida: {nome}", []
    except Exception as e:  # noqa: BLE001
        ctx.registrar(nome, args, f"ERRO: {e}")
        # Falha de ferramenta é informação de auditoria, não exceção silenciosa.
        return (f"ERRO ao executar {nome}: {e}\n"
                f"Trate isto como LACUNA (a fonte existia e não pôde ser lida — R6.b), "
                f"não como ausência de informação."), []


def _ler_documento(args: dict, ctx: Contexto) -> tuple[str, list[dict]]:
    fid, motivo = args.get("file_id", ""), args.get("motivo", "")
    item = next((a for a in ctx.inventario["arquivos"] if a["id"] == fid), None)
    if not item:
        return (f"file_id {fid} não está no inventário. Use listar_arvore para "
                f"localizar o arquivo certo."), []
    if fid in ctx.lidos:
        return f"'{item['nome']}' já foi lido nesta auditoria.", []
    if len(ctx.lidos) >= MAX_DOCS_LIDOS:
        return (f"Limite de {MAX_DOCS_LIDOS} documentos atingido. Encerre a investigação "
                f"e declare como não lidos os que faltarem — eles aparecerão na seção de "
                f"cobertura documental."), []
    if ctx.bytes_gastos > MAX_BYTES_SESSAO:
        return "Limite de volume de leitura atingido nesta sessão.", []

    try:
        data, mime = ctx.drive.download_file_by_id(fid, item.get("mime", ""))
    except Exception as e:  # noqa: BLE001
        ctx.registrar("ler_documento", {"file_id": fid, "nome": item["nome"]}, f"ERRO: {e}")
        return (f"Não foi possível baixar '{item['nome']}': {e}. "
                f"Registre como LACUNA — o documento EXISTE e não pôde ser lido, o que "
                f"tem a mesma severidade de não existir (R6.b)."), []

    if len(data) > MAX_BYTES_DOC:
        ctx.registrar("ler_documento", {"file_id": fid, "nome": item["nome"]}, "grande demais")
        return (f"'{item['nome']}' tem {len(data)//1024//1024} MB — acima do limite de "
                f"leitura. Registre como lacuna e peça extração dirigida ao humano."), []

    ctx.lidos.add(fid)
    ctx.bytes_gastos += len(data)
    ctx.registrar("ler_documento", {"file_id": fid, "nome": item["nome"], "motivo": motivo},
                  f"lido ({len(data)//1024} KB)")

    cab = (f"DOCUMENTO: {item['nome']}\n"
           f"caminho: {item['caminho']}\n"
           f"file_id: {fid}\n"
           f"link: {item['link']}\n"
           f"modificado: {item['modificado']}\n"
           f"motivo da leitura: {motivo}\n"
           f"LEMBRETE R10: ao citar qualquer dado determinante deste documento, verifique "
           f"se ELE declara a própria fonte e a premissa normativa. Documento de terceiro "
           f"sem fonte declarada é ACHADO, por melhor que seja a medição.")

    blocos: list[dict] = []
    m = (mime or "").lower()
    if "pdf" in m:
        blocos.append({
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf",
                       "data": base64.standard_b64encode(data).decode("ascii")},
            "title": item["nome"],
        })
    elif m.startswith("image/"):
        blocos.append({
            "type": "image",
            "source": {"type": "base64", "media_type": m,
                       "data": base64.standard_b64encode(data).decode("ascii")},
        })
    else:
        try:
            txt = data.decode("utf-8", errors="replace")[:150000]
            blocos.append({"type": "text", "text": f"--- conteúdo de {item['nome']} ---\n{txt}"})
        except Exception:  # noqa: BLE001
            return cab + "\n\n(formato não legível diretamente — registre como lacuna)", []

    return cab, blocos


def _listar_arvore(args: dict, ctx: Contexto) -> str:
    arq = ctx.inventario["arquivos"]
    f = (args.get("filtro") or "").lower()
    if f:
        arq = [a for a in arq if f in a["nome"].lower() or f in a["caminho"].lower()]
    if args.get("disciplina"):
        arq = [a for a in arq if a["disciplina"] == args["disciplina"]]
    if args.get("apenas_nao_lidos"):
        arq = [a for a in arq if a["id"] not in ctx.lidos]
    ctx.registrar("listar_arvore", args, f"{len(arq)} arquivos")
    if not arq:
        return "Nenhum arquivo casa com esse filtro."
    return "\n".join(
        f"{a['id']} · {a['situacao']} · {a['disciplina'] or '—'} · "
        f"{a['caminho']}/{a['nome']} · {a['modificado'][:10]}" for a in arq[:200])


def _precedentes(args: dict, ctx: Contexto) -> str:
    disc = args.get("disciplina", "")
    r = fhistorica.buscar(ctx.perfil, disc, args.get("tema", ""))
    ctx.registrar("buscar_precedentes", args,
                  f"{len(r.get('precedentes', []))} precedentes")
    if not r.get("disponivel"):
        return (f"{r['motivo']}\n\nRegistre explicitamente no parecer que a comparação "
                f"histórica não pôde ser feita — silêncio é ambíguo.")
    if not r.get("encontrado"):
        emps = r.get("empreendimentos_na_base", [])
        return (f"{r['declaracao_de_ausencia']}\n"
                f"Empreendimentos hoje na base: {', '.join(emps) or '(nenhum)'}.\n"
                f"DECLARE ESSA AUSÊNCIA no parecer.")
    return json.dumps(r, ensure_ascii=False, indent=1)[:60000]


def _diario(args: dict, ctx: Contexto) -> str:
    r = fdiario.consultar(ctx.emp_id, args.get("termo", ""), args.get("secao", ""))
    ctx.registrar("consultar_diario", args, f"{len(r.get('eventos', []))} eventos")
    if not r.get("disponivel"):
        return r["motivo"]
    if not r.get("encontrado"):
        return r.get("motivo", "Sem diário para este empreendimento.")
    return json.dumps(r, ensure_ascii=False, indent=1)[:40000]


def _spu(args: dict, ctx: Contexto) -> str:
    r = fexternas.consultar_spu(args.get("rip", ""), args.get("o_que", "tudo"))
    for p in r.get("pedidos_ao_humano", []):
        if p not in ctx.pedidos_ao_humano:
            ctx.pedidos_ao_humano.append(p)
    ctx.registrar("consultar_spu", args, r.get("resumo", ""))
    return json.dumps(r, ensure_ascii=False, indent=1)


def _legislacao(args: dict, ctx: Contexto) -> str:
    r = flegislacao.orientar(args.get("municipio", ""), args.get("uf", ""),
                             args.get("tema", ""))
    ctx.dominios_legislacao = r.get("dominios_confiaveis") or []
    ctx.registrar("consultar_legislacao",
                  {"municipio": args.get("municipio"), "tema": args.get("tema")},
                  f"{'com' if r['municipio_conhecido'] else 'SEM'} registro de portais · "
                  f"{len(r['perguntar'])} perguntas")
    return json.dumps(r, ensure_ascii=False, indent=1)


def _pedido(args: dict, ctx: Contexto) -> str:
    p = {
        "o_que_preciso": args.get("o_que_preciso", ""),
        "para_que": args.get("para_que", ""),
        "como_obter": args.get("como_obter", ""),
        "bloqueia": args.get("bloqueia", ""),
        "em": agora(),
    }
    ctx.pedidos_ao_humano.append(p)
    ctx.registrar("pedir_ao_humano", {"o_que": p["o_que_preciso"]}, "registrado")
    return ("Pedido registrado. Ele aparecerá na seção 'Perguntas ao humano' do parecer. "
            "Registre também a Afirmação correspondente com tipo='lacuna'.")
