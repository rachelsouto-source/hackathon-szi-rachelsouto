"""
Motor de auditoria da DD Técnica.

Recebe os documentos de um empreendimento (PDFs em bytes ou texto) e usa a Claude API
para extrair os campos, rodar as regras do playbook e devolver achados + parecer estruturado.

A leitura de PDF é NATIVA da Claude API (document blocks) — sem parser frágil.
Usa prompt caching no system prompt (playbook) para reduzir custo/latência.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any

from .playbook import SYSTEM_PROMPT

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = int(os.getenv("DD_MAX_TOKENS", "8000"))


class DDEngineError(RuntimeError):
    pass


def _build_document_blocks(documents: list[dict[str, Any]]) -> list[dict]:
    """
    documents: [{"name": str, "mime": str, "data": bytes | None, "text": str | None}, ...]
    Gera content blocks para a Claude API: PDFs como 'document', o resto como texto.
    """
    blocks: list[dict] = []
    for doc in documents:
        name = doc.get("name", "documento")
        blocks.append({"type": "text", "text": f"\n=== DOCUMENTO: {name} ==="})
        data = doc.get("data")
        mime = (doc.get("mime") or "").lower()
        if data and "pdf" in mime:
            blocks.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.standard_b64encode(data).decode("ascii"),
                },
                "title": name,
            })
        elif doc.get("text"):
            blocks.append({"type": "text", "text": doc["text"][:200000]})
        elif data and mime.startswith("image/"):
            blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime,
                    "data": base64.standard_b64encode(data).decode("ascii"),
                },
            })
        else:
            blocks.append({"type": "text", "text": "(conteúdo não legível por este formato)"})
    return blocks


def audit(empreendimento: str, documents: list[dict[str, Any]]) -> dict:
    """Roda a auditoria. Requer ANTHROPIC_API_KEY no ambiente."""
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise DDEngineError("Pacote 'anthropic' não instalado.") from e

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise DDEngineError("ANTHROPIC_API_KEY ausente. Use DEMO_MODE para testar sem credenciais.")

    client = anthropic.Anthropic(api_key=api_key)

    user_blocks = [{
        "type": "text",
        "text": (
            f"Empreendimento: {empreendimento}\n"
            f"Abaixo estão os documentos da DD Técnica. Audite conforme as regras e "
            f"responda APENAS com o JSON do schema definido."
        ),
    }]
    user_blocks += _build_document_blocks(documents)

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # prompt caching
            }],
            messages=[{"role": "user", "content": user_blocks}],
        )
    except Exception as e:  # noqa: BLE001
        raise DDEngineError(f"Falha ao chamar a Claude API: {e}") from e

    raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
    return _parse_json(raw)


def _parse_json(raw: str) -> dict:
    """Extrai o JSON da resposta, tolerando cercas de código."""
    s = raw.strip()
    if s.startswith("```"):
        s = s.split("```", 2)[1] if "```" in s else s
        s = s.lstrip("json").strip()
    start, end = s.find("{"), s.rfind("}")
    if start == -1 or end == -1:
        raise DDEngineError(f"Resposta sem JSON válido: {raw[:300]}")
    try:
        return json.loads(s[start:end + 1])
    except json.JSONDecodeError as e:
        raise DDEngineError(f"JSON inválido na resposta: {e}") from e
