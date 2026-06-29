"""
Auditor de DD Técnica — aplicação web (FastAPI).

Rotas:
  GET  /                      -> página (frontend)
  GET  /api/health            -> status e modo (drive/demo)
  GET  /api/empreendimentos   -> lista os empreendimentos de "02 - Projetos"
  POST /api/dd                 -> roda a DD de um empreendimento (body: {id, nome})
  GET  /api/dd/{rid}/xlsx     -> baixa a planilha de controle

Modo DEMO (DEMO_MODE=1 ou sem credenciais): usa os exemplos do Jurerê III,
sem chamar Drive/Claude — permite testar e gravar a demo offline.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core import dd_engine, docs_writer

ROOT = Path(__file__).resolve().parent.parent
EXEMPLOS = ROOT / "claude.md" / "exemplos"
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Auditor de DD Técnica — SZI Lançamentos")

_RESULTS: dict[str, dict] = {}  # cache em memória das DDs geradas


def demo_mode() -> bool:
    if os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}:
        return True
    try:
        from core import drive_client
        return not (drive_client.is_configured() and os.getenv("ANTHROPIC_API_KEY"))
    except Exception:  # noqa: BLE001
        return True


# ----------------- API -----------------

class DDRequest(BaseModel):
    id: str
    nome: str


LOGO_ID = os.getenv("LOGO_FILE_ID", "1QXKWeEZ9w8SVUq0lazUuRnBrnXJFsi9z")


@app.get("/api/health")
def health():
    return {"ok": True, "modo": "demo" if demo_mode() else "produção"}


@app.get("/api/logo")
def logo():
    """Logo da Seazone: em produção serve do Drive; em demo redireciona ao thumbnail."""
    if not demo_mode():
        try:
            from core import drive_client
            data, mime = drive_client.download_file_by_id(LOGO_ID, "image/png")
            return Response(content=data, media_type=mime or "image/png",
                            headers={"Cache-Control": "public, max-age=86400"})
        except Exception:  # noqa: BLE001
            pass
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"https://drive.google.com/thumbnail?id={LOGO_ID}&sz=w240")


@app.get("/api/empreendimentos")
def empreendimentos():
    if demo_mode():
        return {"modo": "demo", "itens": [
            {"id": "demo-jurere-iii", "name": "Jurerê Spot III (demo)"},
            {"id": "demo-farol-barra", "name": "Farol da Barra Spot (demo)"},
        ]}
    from core import drive_client
    try:
        return {"modo": "produção", "itens": drive_client.list_empreendimentos()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erro ao listar empreendimentos: {e}")


def _demo_result(emp_id: str = "demo-jurere-iii") -> dict:
    if emp_id == "demo-farol-barra":
        achados = json.loads((EXEMPLOS / "farol-barra-achados.json").read_text(encoding="utf-8"))["itens"]
        parecer_md = (EXEMPLOS / "farol-barra-parecer.md").read_text(encoding="utf-8")
        return {
            "nome": "Farol da Barra Spot (demo)",
            "achados": achados,
            "parecer_md": parecer_md,
            "negocio": {"recomendacao": "PAUSADO ATÉ RESOLUÇÃO DOS BLOQUEIOS"},
            "doc_url": "",
            "out_folder": None,
        }
    achados = json.loads((EXEMPLOS / "jurere-iii-achados.json").read_text(encoding="utf-8"))["itens"]
    parecer_md = (EXEMPLOS / "jurere-iii-parecer.md").read_text(encoding="utf-8")
    return {
        "nome": "Jurerê Spot III (demo)",
        "achados": achados,
        "parecer_md": parecer_md,
        "negocio": {"recomendacao": "GO COM RESSALVAS"},
        "doc_url": "",        # sem escrita no Drive em modo demo
        "out_folder": None,   # sem pasta de saída em demo
    }


@app.post("/api/dd")
def gerar_dd(req: DDRequest):
    rid = uuid.uuid4().hex[:8]

    if demo_mode():
        data = _demo_result(req.id)
        data["xlsx"] = docs_writer.gerar_xlsx_bytes(
            data["nome"], data["achados"], data.get("negocio", {}).get("recomendacao", "—"))
        _RESULTS[rid] = data
        return _public(rid, data)

    # Produção: localiza fontes no Drive -> Claude -> Google Doc + xlsx
    from core import drive_client, locator
    try:
        # 1. Localiza os documentos da DD nas subpastas (última versão em PDF) + links
        fontes = locator.localizar(req.id)

        # 2. Baixa os arquivos localizados para enviar ao motor
        docs = []
        for tipo, val in fontes.items():
            itens = val if isinstance(val, list) else ([val] if val else [])
            for it in itens:
                try:
                    data, mime = drive_client.download_file_by_id(it["id"], it.get("mime", ""))
                    docs.append({"name": it["nome"], "mime": mime, "data": data, "link": it.get("link", "")})
                except Exception:  # noqa: BLE001
                    continue
        if not docs:
            raise HTTPException(422, "Nenhum documento da DD encontrado nas subpastas do empreendimento.")

        # 3. Audita
        result = dd_engine.audit(req.nome, docs)
        achados = result.get("achados", [])

        # 4. Anexa os links das fontes a cada achado (rastreabilidade)
        locator.anexar_links(achados, fontes)
        # Imagens (localização/drone) entram como um achado próprio, com links
        imgs = fontes.get("imagens") or []
        if imgs:
            ach_img = {
                "etapa": "Imagens (localização/drone)", "documento": f"{len(imgs)} imagem(ns)",
                "status": "OK", "severidade": "OK",
                "observacao": "Imagens de localização/drone usadas para avaliar entorno, contexto urbano e vistas.",
                "acao": "—", "fonte": "; ".join(i["nome"] for i in imgs[:4]),
                "link": imgs[0].get("link", ""),
            }
            if len(imgs) > 1:
                ach_img["link2"] = imgs[1].get("link", "")
            achados.append(ach_img)
        result["achados"] = achados
        # Figuras de LOCALIZAÇÃO (imagens reais) — thumbnail p/ tela + bytes p/ embutir no doc
        figuras, doc_images = [], {}
        for i in (fontes.get("imagens") or []):
            url = f"https://drive.google.com/thumbnail?id={i['id']}&sz=w640"
            figuras.append({"url": url, "cap": i["nome"]})
            try:
                b, _ = drive_client.download_file_by_id(i["id"], i.get("mime", "image/png"))
                doc_images[url] = b
            except Exception:  # noqa: BLE001
                pass
        result["figuras"] = figuras
        # Figura por seção = thumbnail (1ª página) do documento de cada tópico
        def _thumb(tipo, cap):
            f = fontes.get(tipo)
            if isinstance(f, dict) and f.get("id"):
                return {"url": f"https://drive.google.com/thumbnail?id={f['id']}&sz=w640", "cap": cap}
            return None
        result["figuras_secao"] = {k: v for k, v in {
            "topografia": _thumb("topografico", "Levantamento topográfico"),
            "ambiental": _thumb("ambiental", "Estudo de viabilidade ambiental (EVA)"),
            "validacao_ep": _thumb("validacao_ep", "Validação do estudo preliminar"),
            "sondagem": _thumb("sondagem", "Relatório de sondagem"),
            "estrutura_fundacao": _thumb("estrutura", "Estrutura / fundação"),
        }.items() if v}
        parecer_md = docs_writer.render_parecer_md(req.nome, result)

        # 5. Grava o Google Doc na pasta 07 - DD Técnica (fallback: raiz do empreendimento)
        out_folder = locator.find_dd_folder(req.id) or req.id
        try:
            doc = docs_writer.create_google_doc(
                out_folder, f"[{req.nome}] DD Técnica (auto)", parecer_md, images=doc_images)
            doc_url = doc.get("url", "")
        except Exception:  # noqa: BLE001  (não trava a DD se a escrita falhar)
            doc_url = ""
        data = {
            "nome": req.nome, "achados": achados, "parecer_md": parecer_md,
            "negocio": result.get("negocio", {}), "doc_url": doc_url,
            "out_folder": out_folder, "figuras": figuras, "doc_images": doc_images,
            "xlsx": docs_writer.gerar_xlsx_bytes(
                req.nome, achados, result.get("negocio", {}).get("recomendacao", "—")),
        }
        _RESULTS[rid] = data
        return _public(rid, data)
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Falha ao gerar a DD: {e}")


def _public(rid: str, data: dict) -> dict:
    return {
        "rid": rid, "nome": data["nome"], "achados": data["achados"],
        "parecer_md": data["parecer_md"], "negocio": data.get("negocio", {}),
        "doc_url": data.get("doc_url", ""),
        "xlsx_url": f"/api/dd/{rid}/xlsx",
    }


class GDocRequest(BaseModel):
    parecer_md: str | None = None


@app.post("/api/dd/{rid}/gdoc")
def gerar_gdoc(rid: str, body: GDocRequest | None = None):
    """Cria o parecer como Google Doc na pasta 07 - DD Técnica (sob demanda).
    Aceita opcionalmente um parecer_md editado no body (edições feitas na UI)."""
    data = _RESULTS.get(rid)
    if not data:
        raise HTTPException(404, "Resultado não encontrado.")
    # Se o cliente enviou um parecer editado, sobrescreve o original
    if body and body.parecer_md:
        data["parecer_md"] = body.parecer_md
    if data.get("doc_url"):
        return {"doc_url": data["doc_url"], "msg": "Google Doc já criado."}
    # Produção: cria o Google Doc de verdade na pasta 07 - DD Técnica
    if not demo_mode() and data.get("out_folder"):
        try:
            doc = docs_writer.create_google_doc(
                data["out_folder"], f"[{data['nome']}] DD Técnica (auto)",
                data["parecer_md"], images=data.get("doc_images"))
            data["doc_url"] = doc.get("url", "")
            return {"doc_url": data["doc_url"]}
        except Exception as e:  # noqa: BLE001
            raise HTTPException(500, f"Falha ao criar Google Doc: {e}")
    # Demo / sem credenciais: oferece download de um .doc (abre no Word)
    return {"doc_url": "", "download_url": f"/api/dd/{rid}/doc",
            "msg": "Documento gerado para download (.doc). Em produção, é criado direto no "
                   "Google Docs e salvo na pasta “07 - DD Técnica”."}


@app.get("/api/dd/{rid}/doc")
def baixar_doc(rid: str):
    """Parecer como documento .docx formatado (Word) — usado no modo demo."""
    data = _RESULTS.get(rid)
    if not data:
        raise HTTPException(404, "Resultado não encontrado.")
    import unicodedata
    docx_bytes = docs_writer.gerar_docx_bytes(data["nome"], data["parecer_md"], data.get("doc_images"))
    base = (unicodedata.normalize("NFKD", f"DD_Tecnica_{data['nome']}")
            .encode("ascii", "ignore").decode("ascii")).replace(" ", "_")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{base}.docx"'},
    )


@app.get("/api/dd/{rid}/xlsx")
def baixar_xlsx(rid: str):
    data = _RESULTS.get(rid)
    if not data or "xlsx" not in data:
        raise HTTPException(404, "Resultado não encontrado.")
    import unicodedata
    base = f"controle-dd-{data['nome']}".replace(" ", "_")
    # nome ASCII puro p/ o header (HTTP headers são latin-1)
    ascii_name = (unicodedata.normalize("NFKD", base)
                  .encode("ascii", "ignore").decode("ascii")) or "controle-dd"
    fname = f"{ascii_name}.xlsx"
    return Response(
        content=data["xlsx"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


# ----------------- Monitor automático -----------------

@app.get("/api/monitor")
def monitor_status():
    """Varre '02 - Projetos' e mostra a completude de cada empreendimento."""
    if demo_mode():
        return {"modo": "demo", "itens": [
            {
                "id": "demo-jurere-iii", "nome": "Jurerê Spot III (demo)",
                "completo": True, "ja_tem_dd": True, "elegivel": False,
                "presentes": ["(demo)"], "faltando": [],
            },
            {
                "id": "demo-farol-barra", "nome": "Farol da Barra Spot (demo)",
                "completo": False, "ja_tem_dd": False, "elegivel": False,
                "presentes": ["matrícula", "topografia", "sondagem", "estudo ambiental"],
                "faltando": ["aprovações", "validação EP", "proposta CCV"],
            },
        ]}
    from core import monitor
    try:
        return {"modo": "produção", "itens": monitor.varrer()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erro no monitor: {e}")


@app.post("/api/monitor/run")
def monitor_run():
    """Dispara a DD automaticamente para os empreendimentos elegíveis (cron do Coolify)."""
    if demo_mode():
        return {"modo": "demo", "processados": [], "msg": "Sem ação em modo demo."}
    from core import monitor
    processados = []
    for emp in monitor.varrer():
        if emp.get("elegivel"):
            try:
                res = gerar_dd(DDRequest(id=emp["id"], nome=emp["nome"]))
                processados.append({"nome": emp["nome"], "rid": res["rid"], "doc_url": res.get("doc_url", "")})
            except Exception as e:  # noqa: BLE001
                processados.append({"nome": emp["nome"], "erro": str(e)})
    return {"modo": "produção", "processados": processados, "total": len(processados)}


# ----------------- Frontend -----------------

@app.get("/", response_class=HTMLResponse)
def index():
    content = (STATIC / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=content, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache", "Expires": "0",
    })


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
