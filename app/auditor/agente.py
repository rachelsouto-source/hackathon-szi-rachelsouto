"""
Agente investigativo — substitui a chamada única de `core/dd_engine.py`.

O v1 era `client.messages.create(...)` uma vez, sem `tools`, sem loop. Aqui são três
fases, e o humano entra na quarta (sessão de contestação, em pipeline.py):

  FASE A  investigar  — loop com ferramentas até o agente declarar que terminou
  FASE B  consolidar  — transcrito da investigação → Livro de Evidências estruturado
  FASE C  contestar   — Contraditor adversarial sobre cada afirmação crítica

Por que a Fase C não é luxo: no São Miguel, a prancha da MCZ estava internamente
coerente (1,2 cm de divergência em 15 arestas — levantamento metricamente muito bom). O
erro estava na PREMISSA, e só apareceu quando alguém perguntou "de onde veio essa linha?".
Um leitor cuidadoso teria validado o documento. Foi preciso um refutador.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from . import cartografo, ferramentas
from .livro import (Afirmacao, Contestacao, Evidencia, Livro, PerfilCaso)

MODELO = os.getenv("ANTHROPIC_MODEL", "claude-opus-5")
MODELO_LEVE = os.getenv("ANTHROPIC_MODEL_LEVE", "claude-sonnet-5")
MAX_TOKENS_INVESTIGACAO = int(os.getenv("DD_MAX_TOKENS_INV", "8000"))
MAX_TOKENS_CONSOLIDACAO = int(os.getenv("DD_MAX_TOKENS", "32000"))
MAX_ITERACOES = int(os.getenv("DD_MAX_ITERACOES", "40"))


class AgenteError(RuntimeError):
    pass


def _cliente():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise AgenteError("Pacote 'anthropic' não instalado.") from e
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise AgenteError("ANTHROPIC_API_KEY ausente.")
    return anthropic.Anthropic(api_key=key)


# --------------------------------------------------------------------------- #
# Prompts
# --------------------------------------------------------------------------- #

def _base_metodo() -> str:
    """
    Carrega a metodologia de base-conhecimento/ se estiver presente no container.

    O método (persona, 5 leituras, 12 blocos, R1–R9, criticidade, estrutura do parecer)
    é conteúdo versionado, não string no código. Se não vier no build, cai no playbook.
    """
    from pathlib import Path
    for raiz in (Path(__file__).resolve().parents[2], Path.cwd(), Path("/app")):
        p = raiz / "base-conhecimento" / "PROMPT-SISTEMA.md"
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                pass
    try:
        from core.playbook import SYSTEM_PROMPT
        return SYSTEM_PROMPT
    except Exception:  # noqa: BLE001
        return ""


PROMPT_INVESTIGACAO = """Você é o AUDITOR DE DD TÉCNICA da Seazone Investimentos, agindo
como um coordenador de projetos sênior. Esta é a FASE DE INVESTIGAÇÃO: você ainda NÃO vai
escrever o parecer. Sua tarefa agora é REUNIR EVIDÊNCIA.

COMO UM ESPECIALISTA TRABALHA (e é isto que se espera de você):
1. Lê os documentos.
2. Gera hipóteses.
3. Detecta lacunas.
4. Busca novas evidências — inclusive fora da pasta.
5. Consulta a base de conhecimento e casos semelhantes.
6. Consulta o Diário do time.
7. Cruza tudo e atualiza as hipóteses.

REGRAS DA INVESTIGAÇÃO — todas nasceram de falhas reais:

R-VARREDURA (R6.a/R6.b) — pasta NÃO é documento. A estrutura de subpastas da Seazone é
criada por template e vem vazia. Nunca conclua que um documento existe porque a pasta
existe. E "existe e não foi lido" tem a MESMA severidade de "não existe": leia tudo que
for relevante ou declare explicitamente por que não leu.

R-FONTE (R10) — todo dado técnico DETERMINANTE de documento de terceiro deve declarar
sua fonte E sua premissa normativa. Se a prancha afirma onde está a linha de marinha mas
não diz de onde tirou isso, ISSO É UM ACHADO — por melhor que seja a medição. Medição
correta sobre premissa errada é o modo de falha mais caro da DD. Exemplo real: um
levantamento traçou a "LPM atual" (maré de hoje) quando a lei define terreno de marinha
pela preamar-média de 1831 (DL 9.760/1946, art. 2º). O levantamento era ótimo. A premissa
estava errada, e isso mudou 80% do terreno de mão.

R-MARINHA — encontrou um RIP, ou menção a marinha/aforamento/ocupação? Chame
`consultar_spu` IMEDIATAMENTE. Não espere que alguém peça. A situação de homologação da
demarcação é POR TRECHO — leia o atributo da feição, não presuma.

R-PRECEDENTE — para CADA disciplina em que encontrar algo relevante, chame
`buscar_precedentes`. A saída esperada tem esta forma: "Vocês tiveram um caso parecido no
[X]. Lá aconteceu [Y] e o desfecho foi [Z]. Aqui a assinatura é a mesma porque [W]. Ponto
de atenção." Se NÃO houver precedente, isso também é informação — declare a ausência.

R-DIÁRIO — chame `consultar_diario` no início. O time registra em reunião e Slack coisas
que não estão em documento nenhum (suspensão de alvará, ação do MP, atraso real). Trate
como GERADOR DE PERGUNTA: "o pessoal está preocupado com X — deixa eu investigar X".
Nunca como fato isolado.

R-LACUNA — se falta informação para concluir, você PARA e chama `pedir_ao_humano`. Não
estime, não presuma, não ofereça sugestão especulativa. Uma lacuna bem declarada vale
mais do que um palpite plausível. Isso é preferência explícita de quem usa o sistema.

R-JURÍDICO — a DD Jurídica é feita por outro time. Você CONSOME o resultado dela como
parâmetro (área da matrícula, cadeia dominial, ônus, aprovação) — não a refaz nem emite
exigência jurídica. Se o resultado não estiver na pasta, registre como lacuna.

R-ENTORNO — se sua análise caminha para "inviável" e existem empreendimentos vizinhos
construídos sob a MESMA restrição, isso é uma contradição a investigar, não um detalhe.
Pode haver um instrumento que não conhecemos (incorporação prévia, aforamento,
retificação de georreferenciamento). Falso positivo custa terreno bom.

FERRAMENTAS: use-as de verdade. Você tem no máximo {max_iter} rodadas. Quando tiver
esgotado o que é obtenível, chame `concluir_investigacao`.

--- PERFIL DO CASO ---
{perfil}

--- INVENTÁRIO COMPLETO DA PASTA (varredura exaustiva, sem whitelist) ---
{inventario}

--- MUDANÇAS DESDE A ÚLTIMA AUDITORIA ---
{delta}
"""

PROMPT_CONSOLIDACAO = """Você agora vai CONSOLIDAR a investigação no LIVRO DE EVIDÊNCIAS.

REGRA ABSOLUTA: não existe afirmação sem evidência. Se você não consegue apontar o
documento, o trecho literal e a localização, então NÃO é uma afirmação — é uma lacuna.
O schema não aceita o contrário.

Cada evidência exige:
  - origem: documento_emp | base_historica | diario | fonte_externa | legislacao | humano
  - ref: file_id, ou id da linha granular, ou âncora do Diário, ou URL
  - trecho: A CITAÇÃO LITERAL. Nome de arquivo NÃO é evidência.
  - localizacao: "p. 4", "camada X", "00:41:27"
  - fonte_declarada_pelo_doc: o que o próprio documento diz sobre de onde tirou o dado.
    Use null se o documento NÃO declara — isso dispara R10 e vira achado.

TIPOS de afirmação:
  fato       — está escrito no documento do terreno
  inferencia — você deduziu cruzando fontes (diga quais em depende_de)
  precedente — vem de caso anterior. NUNCA é fato sobre este terreno.
  hipotese   — explicação plausível ainda não confirmada. Se a confiança for baixa,
               NÃO infle a severidade.
  lacuna     — falta evidência. Preencha o_que_falta, como_obter, depende_de_humano.

SEVERIDADE: "Crítico" (impede ou muda o negócio), "Atenção", "OK".
`depende_de`: ids das afirmações que sustentam esta. É o que permite reabrir só o
subgrafo afetado quando um humano contestar. Preencha com cuidado.

SOBRE A RECOMENDAÇÃO: você NÃO emite GO/NO-GO. Isso é decisão humana. O que você emite é
a EXPOSIÇÃO TÉCNICA: qual é a situação, qual a divergência, qual o ponto de atenção, qual
o precedente, qual o custo/prazo estimado das ressalvas, e o que ainda falta saber.
Preencha `exposicao` — não uma recomendação.

As seções de `conclusao` devem ser PROSA CORRIDA, técnico-formal, no padrão do parecer da
Seazone — não listas com ponto e vírgula. Seja específico: cite números, normas e órgãos
sempre que os documentos fornecerem. Não resuma em excesso.

Responda APENAS com JSON válido neste schema:
{{
  "perfil": {{"cidade": "", "uf": "", "produto": "", "regime_dominial": "",
              "instrumento_aquisicao": "", "flags": ["marinha", "APP", "..."]}},
  "imovel": {{"inscricoes": "", "endereco": "", "area_matricula_total": "", "matriculas": ""}},
  "proprietarios": ["..."],
  "areas_tabela": {{"matricula": [{{"ref": "", "area": ""}}],
                    "cadastro_pmf": [{{"ref": "", "area": ""}}], "topografico": ""}},
  "afirmacoes": [
    {{"id": "AF-001", "disciplina": "jurídico-cartorial", "texto": "",
      "tipo": "fato", "confianca": "alta", "severidade": "Crítico",
      "regra": "R4", "premissa_normativa": null, "acao": "",
      "depende_de": [], "o_que_falta": "", "como_obter": "", "depende_de_humano": false,
      "evidencias": [{{"origem": "documento_emp", "ref": "<file_id>", "trecho": "",
                       "link": "", "localizacao": "p. 2", "data_do_documento": "",
                       "fonte_declarada_pelo_doc": null}}]}}
  ],
  "precedentes": [
    {{"empreendimento": "", "emp_id": "", "distancia_ou_relacao": "",
      "o_que_aconteceu_la": "", "por_que_se_aplica_aqui": "", "link": "",
      "fonte": "linha granular #..."}}
  ],
  "conclusao": {{"topografia": "", "ambiental": "", "urbanistico": "",
                 "validacao_ep": "", "sondagem": "", "estrutura_fundacao": "",
                 "juridico_dominial": "", "final": ""}},
  "validacao": {{"ajustes": [], "docs_aprovacao": [], "docs_alvara": []}},
  "exposicao": {{
    "situacao": "o que se apurou, em uma frase",
    "divergencias": ["..."],
    "pontos_de_atencao": ["..."],
    "impacto_custo_prazo": "",
    "o_que_falta_para_concluir": ["..."],
    "decisao_e_humana": true
  }}
}}"""

PROMPT_CONTRADITOR = """Você é o CONTRADITOR da auditoria. Sua tarefa é DERRUBAR a
afirmação abaixo, não concordar com ela. Trabalhe como um revisor hostil e competente.

Ataque nesta ordem:
1. A PREMISSA NORMATIVA está certa? (o caso clássico: usar a maré de hoje quando a lei
   manda usar a preamar-média de 1831)
2. A evidência realmente SUSTENTA a conclusão, ou sustenta algo mais fraco?
3. Existe leitura ALTERNATIVA dos mesmos dados?
4. A fonte é apropriada para esse tipo de afirmação? (fala de reunião não prova fato
   sobre o terreno; precedente não prova fato sobre o terreno)
5. Há salto de escopo — o dado é de outro imóvel, outra data, outra revisão?

Se não conseguir derrubar com argumento concreto, diga "improcede". Não invente objeção
para parecer rigoroso: objeção fraca gasta a atenção de quem revisa.

Responda APENAS com JSON:
{"veredito": "procede|improcede|inconclusivo", "argumento": "1-3 frases objetivas",
 "estado_sugerido": "confirmada|refutada|indeterminada"}"""


# --------------------------------------------------------------------------- #
# FASE A — investigação
# --------------------------------------------------------------------------- #

def investigar(ctx: ferramentas.Contexto, delta: dict,
               progresso: Callable[[str], None] | None = None) -> list[dict]:
    """Roda o loop de ferramentas. Devolve o histórico de mensagens."""
    cli = _cliente()
    aviso = lambda m: progresso and progresso(m)  # noqa: E731

    sistema = [
        {"type": "text", "text": _base_metodo(), "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": PROMPT_INVESTIGACAO.format(
            max_iter=MAX_ITERACOES,
            perfil=ctx.perfil.resumo(),
            inventario=cartografo.resumo_para_prompt(ctx.inventario),
            delta=_delta_texto(delta),
        )},
    ]

    mensagens: list[dict] = [{
        "role": "user",
        "content": [{"type": "text", "text":
                     f"Investigue o empreendimento '{ctx.nome}'. Comece consultando o "
                     f"Diário e lendo os documentos jurídicos e de topografia."}],
    }]

    tools = ferramentas.schemas()
    for i in range(MAX_ITERACOES):
        try:
            resp = cli.messages.create(
                model=MODELO, max_tokens=MAX_TOKENS_INVESTIGACAO,
                system=sistema, messages=mensagens, tools=tools,
            )
        except Exception as e:  # noqa: BLE001
            raise AgenteError(f"Falha na investigação (iteração {i+1}): {e}") from e

        mensagens.append({"role": "assistant", "content": resp.content})
        usos = [b for b in resp.content if getattr(b, "type", "") == "tool_use"]
        if not usos:
            break

        conteudo_retorno: list[dict] = []
        terminou = False
        for u in usos:
            if u.name == "concluir_investigacao":
                terminou = True
                conteudo_retorno.append({
                    "type": "tool_result", "tool_use_id": u.id,
                    "content": "Investigação encerrada. Aguarde a fase de consolidação.",
                })
                continue
            aviso(f"{u.name}: {json.dumps(u.input, ensure_ascii=False)[:90]}")
            texto, extras = ferramentas.executar(u.name, dict(u.input), ctx)
            conteudo_retorno.append({
                "type": "tool_result", "tool_use_id": u.id, "content": texto})
            conteudo_retorno.extend(extras)

        mensagens.append({"role": "user", "content": conteudo_retorno})
        if terminou:
            break
    else:
        aviso(f"limite de {MAX_ITERACOES} iterações atingido — consolidando o que há")

    return mensagens


def _delta_texto(delta: dict) -> str:
    if delta.get("primeira_varredura"):
        return "Primeira auditoria deste empreendimento — não há rodada anterior."
    if not delta.get("houve_mudanca"):
        return ("Nenhum documento mudou desde a última auditoria. AINDA ASSIM, refaça a "
                "análise do zero: conclusão anterior nunca é reaproveitada.")
    p = [f"{len(delta['novos'])} novo(s), {len(delta['alterados'])} alterado(s), "
         f"{len(delta['removidos'])} removido(s):"]
    for a in delta["novos"][:25]:
        p.append(f"  + {a['caminho']}/{a['nome']} ({a['modificado'][:10]})")
    for a in delta["alterados"][:25]:
        p.append(f"  ~ {a['caminho']}/{a['nome']} ({a['modificado'][:10]})")
    if delta["removidos"]:
        p.append(f"  − {len(delta['removidos'])} arquivo(s) REMOVIDO(S) — as conclusões "
                 f"que dependiam deles voltam a ficar em aberto.")
    p.append("PRIORIZE ler os novos e alterados, sem deixar de reavaliar o conjunto.")
    return "\n".join(p)


# --------------------------------------------------------------------------- #
# FASE B — consolidação
# --------------------------------------------------------------------------- #

def consolidar(mensagens: list[dict], ctx: ferramentas.Contexto) -> dict:
    cli = _cliente()
    msgs = list(mensagens) + [{
        "role": "user",
        "content": [{"type": "text", "text": PROMPT_CONSOLIDACAO}],
    }]
    try:
        resp = cli.messages.create(
            model=MODELO, max_tokens=MAX_TOKENS_CONSOLIDACAO, messages=msgs)
    except Exception as e:  # noqa: BLE001
        raise AgenteError(f"Falha ao consolidar: {e}") from e

    raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
    if getattr(resp, "stop_reason", "") == "max_tokens":
        raise AgenteError(
            "A consolidação foi truncada por limite de tokens (stop_reason=max_tokens). "
            "Aumente DD_MAX_TOKENS. O v1 falhava aqui em silêncio, reportando apenas "
            "'JSON inválido'.")
    return _json(raw)


def _json(raw: str) -> dict:
    s = raw.strip()
    if s.startswith("```"):
        partes = s.split("```")
        s = partes[1] if len(partes) > 1 else s
        if s.lstrip().lower().startswith("json"):
            s = s.lstrip()[4:]
    a, b = s.find("{"), s.rfind("}")
    if a == -1 or b == -1:
        raise AgenteError(f"Resposta sem JSON: {raw[:400]}")
    try:
        return json.loads(s[a:b + 1])
    except json.JSONDecodeError as e:
        raise AgenteError(f"JSON inválido: {e}") from e


# --------------------------------------------------------------------------- #
# FASE C — Contraditor
# --------------------------------------------------------------------------- #

def contestar(livro: Livro, limite: int = 12,
              progresso: Callable[[str], None] | None = None) -> None:
    """Roda o Contraditor sobre as afirmações críticas. Muta o Livro."""
    cli = _cliente()
    alvos = [a for a in livro.afirmacoes
             if a.severidade == "Crítico" and a.tipo != "lacuna"][:limite]
    for a in alvos:
        if progresso:
            progresso(f"contestando {a.id}")
        ev = "\n".join(
            f"- [{e.origem}] {e.trecho[:400]} ({e.localizacao or 's/ localização'}; "
            f"fonte declarada pelo doc: {e.fonte_declarada_pelo_doc or 'NENHUMA'})"
            for e in a.evidencias)
        alvo = (f"AFIRMAÇÃO {a.id} ({a.disciplina}, {a.tipo}, severidade {a.severidade})\n"
                f"{a.texto}\n\nPremissa normativa declarada: "
                f"{a.premissa_normativa or 'NENHUMA'}\n\nEvidências:\n{ev}")
        try:
            r = cli.messages.create(
                model=MODELO, max_tokens=1200,
                system=PROMPT_CONTRADITOR,
                messages=[{"role": "user", "content": alvo}])
            txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
            d = _json(txt)
        except Exception as e:  # noqa: BLE001
            a.contestacoes.append(Contestacao(
                autor="contraditor", argumento=f"(falha ao contestar: {e})",
                veredito="inconclusivo", em=ferramentas.agora()))
            a.estado = "indeterminada"
            continue

        a.contestacoes.append(Contestacao(
            autor="contraditor", argumento=d.get("argumento", ""),
            veredito=d.get("veredito", "inconclusivo"), em=ferramentas.agora()))
        sug = d.get("estado_sugerido", "")
        a.estado = sug if sug in {"confirmada", "refutada", "indeterminada"} else "indeterminada"


# --------------------------------------------------------------------------- #
# JSON do modelo -> Livro
# --------------------------------------------------------------------------- #

def montar_livro(bruto: dict, ctx: ferramentas.Contexto, rodada: int) -> Livro:
    perf = bruto.get("perfil") or {}
    perfil = PerfilCaso(
        emp_id=ctx.perfil.emp_id, nome=ctx.nome,
        cidade=perf.get("cidade") or ctx.perfil.cidade,
        uf=perf.get("uf") or ctx.perfil.uf,
        lat=ctx.perfil.lat, lon=ctx.perfil.lon,
        produto=perf.get("produto", ""),
        regime_dominial=perf.get("regime_dominial", ""),
        instrumento_aquisicao=perf.get("instrumento_aquisicao", ""),
        flags=perf.get("flags", []) or [],
    )

    links = {a["id"]: a["link"] for a in ctx.inventario["arquivos"]}
    afirmacoes: list[Afirmacao] = []
    for i, d in enumerate(bruto.get("afirmacoes", []), start=1):
        evs = []
        for e in d.get("evidencias", []) or []:
            ref = str(e.get("ref", ""))
            evs.append(Evidencia(
                origem=e.get("origem", "documento_emp"),
                ref=ref,
                trecho=str(e.get("trecho", "")),
                link=e.get("link") or links.get(ref, ""),
                localizacao=e.get("localizacao", ""),
                data_do_documento=e.get("data_do_documento", ""),
                fonte_declarada_pelo_doc=e.get("fonte_declarada_pelo_doc"),
                consultado_em=ferramentas.agora(),
            ))
        afirmacoes.append(Afirmacao(
            id=d.get("id") or f"AF-{i:03d}",
            disciplina=d.get("disciplina", "arquitetura-projeto"),
            texto=d.get("texto", ""),
            tipo=d.get("tipo", "fato"),
            confianca=d.get("confianca", "media"),
            evidencias=evs,
            regra=d.get("regra"),
            premissa_normativa=d.get("premissa_normativa"),
            depende_de=d.get("depende_de", []) or [],
            severidade=d.get("severidade"),
            acao=d.get("acao", ""),
            o_que_falta=d.get("o_que_falta", ""),
            como_obter=d.get("como_obter", ""),
            depende_de_humano=bool(d.get("depende_de_humano")),
        ))

    livro = Livro(
        emp_id=ctx.emp_id, nome=ctx.nome, rodada=rodada,
        gerado_em=ferramentas.agora(), perfil=perfil,
        afirmacoes=afirmacoes,
        cobertura=cartografo.cobertura(ctx.inventario, ctx.lidos),
        precedentes=bruto.get("precedentes", []) or [],
        perguntas_ao_humano=ctx.pedidos_ao_humano,
        ferramentas_usadas=ctx.chamadas,
        proveniencia={
            "modelo": MODELO,
            "max_iteracoes": MAX_ITERACOES,
            "documentos_lidos": len(ctx.lidos),
            "chamadas_de_ferramenta": len(ctx.chamadas),
            "imovel": bruto.get("imovel", {}),
            "proprietarios": bruto.get("proprietarios", []),
            "areas_tabela": bruto.get("areas_tabela", {}),
            "conclusao": bruto.get("conclusao", {}),
            "validacao": bruto.get("validacao", {}),
            "exposicao": bruto.get("exposicao", {}),
        },
    )
    livro.aplicar_tetos()
    return livro
