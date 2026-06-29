"""
Monitor automático da pasta "02 - Projetos".

Varre os empreendimentos, identifica os que (a) já têm todos os documentos obrigatórios
e (b) ainda NÃO têm um parecer de DD gerado, e dispara a DD para eles.

Projetado para rodar como um job agendado (cron do Coolify) chamando /api/monitor/run,
em vez de um loop infinito no processo web.
"""
from __future__ import annotations

from typing import Any

from . import drive_client
from .playbook import DOCUMENTOS

DD_DOC_MARKERS = ["dd técnica", "dd tecnica", "parecer técnico", "parecer tecnico", "due diligence"]


def _match(nome: str, aliases: list[str]) -> bool:
    n = nome.lower()
    return any(a in n for a in aliases)


def status_empreendimento(folder_id: str) -> dict[str, Any]:
    """Avalia a completude de um empreendimento e se já existe DD."""
    arquivos = drive_client.list_files(folder_id)
    nomes = [f["name"] for f in arquivos if f["mimeType"] != "application/vnd.google-apps.folder"]

    presentes, faltando = [], []
    for doc in DOCUMENTOS:
        if not doc["obrigatorio"]:
            continue
        (presentes if any(_match(n, doc["aliases"]) for n in nomes) else faltando).append(doc["etapa"])

    ja_tem_dd = any(any(m in n.lower() for m in DD_DOC_MARKERS) for n in nomes)
    return {
        "completo": not faltando,
        "presentes": presentes,
        "faltando": faltando,
        "ja_tem_dd": ja_tem_dd,
        "elegivel": (not faltando) and (not ja_tem_dd),
    }


def varrer() -> list[dict[str, Any]]:
    """Lista o status de todos os empreendimentos e marca os elegíveis para DD automática."""
    out = []
    for emp in drive_client.list_empreendimentos():
        st = status_empreendimento(emp["id"])
        out.append({"id": emp["id"], "nome": emp["name"], **st})
    return out
