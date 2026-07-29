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
from dataclasses import dataclass, field
from typing import Any

from . import cartografo
from .fontes import diario as fdiario
from .fontes import externas as fexternas
from .fontes import historica as fhistorica

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

    def registrar(self, nome: str, args: dict, resumo: str) -> None:
        self.chamadas.append({"ferramenta": nome, "args": args,
                              "em": agora(), "resumo": resumo[:400]})

    def ja_tentou(self, nome: str, **args) -> bool:
        return any(c["ferramenta"] == nome and all(c["args"].get(k) == v
                   for k, v in args.items()) for c in self.chamadas)


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
                "Orienta a verificação de legislação municipal/estadual. Existe base "
                "estruturada apenas para Florianópolis; fora dali, use web_search sobre "
                "texto primário. Regra inviolável: NUNCA citar lei de memória, sempre "
                "conferir vigência na data da análise."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "municipio": {"type": "string"},
                    "uf": {"type": "string"},
                    "tema": {"type": "string"},
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
    r = fexternas.orientacao_legislacao(args.get("municipio", ""), args.get("uf", ""))
    ctx.registrar("consultar_legislacao", args, r.get("fonte", ""))
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
