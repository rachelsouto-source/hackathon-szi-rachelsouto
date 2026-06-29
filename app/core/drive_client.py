"""
Cliente de Google Drive via Service Account.

- Autentica server-to-server (sem login interativo) — ideal p/ Coolify.
- Lista empreendimentos (subpastas de PROJETOS_FOLDER_ID = "02 - Projetos").
- Baixa os documentos de uma pasta (PDFs em bytes; Google Docs exportados em PDF).

Credencial: env GOOGLE_SERVICE_ACCOUNT_JSON (conteúdo JSON) OU
GOOGLE_SERVICE_ACCOUNT_FILE (caminho do arquivo .json).

Se nada estiver configurado, levanta DriveNotConfigured (o app cai no DEMO_MODE).
"""
from __future__ import annotations

import io
import json
import os
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/drive"]
# Pasta que LISTA os empreendimentos (ex.: "00 - Empreendimentos Estruturados / em Estruturação").
# Cada subpasta é um empreendimento (ex.: "1.43 - [6468] Jurerê Spot III").
EMPREENDIMENTOS_FOLDER_ID = (os.getenv("EMPREENDIMENTOS_FOLDER_ID")
                             or os.getenv("PROJETOS_FOLDER_ID", ""))
PROJETOS_FOLDER_ID = EMPREENDIMENTOS_FOLDER_ID  # compatibilidade

# Tipos exportáveis do Google Workspace -> exportar como PDF
GOOGLE_EXPORTABLE = {
    "application/vnd.google-apps.document": "application/pdf",
    "application/vnd.google-apps.spreadsheet": "application/pdf",
    "application/vnd.google-apps.presentation": "application/pdf",
}


class DriveNotConfigured(RuntimeError):
    pass


def _credentials():
    try:
        from google.oauth2 import service_account
    except ImportError as e:  # pragma: no cover
        raise DriveNotConfigured("Pacote google-auth não instalado.") from e

    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if raw:
        info = json.loads(raw)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if path and os.path.exists(path):
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    raise DriveNotConfigured("Service Account não configurada (GOOGLE_SERVICE_ACCOUNT_JSON/FILE).")


def _service():
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


def is_configured() -> bool:
    return bool(
        (os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or
         (os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") and os.path.exists(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", ""))))
        and PROJETOS_FOLDER_ID
    )


def list_empreendimentos() -> list[dict[str, str]]:
    """Subpastas de '02 - Projetos' = empreendimentos."""
    if not PROJETOS_FOLDER_ID:
        raise DriveNotConfigured("PROJETOS_FOLDER_ID não definido.")
    svc = _service()
    q = (f"'{PROJETOS_FOLDER_ID}' in parents and "
         f"mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    out, token = [], None
    while True:
        resp = svc.files().list(
            q=q, fields="nextPageToken, files(id, name)",
            orderBy="name", pageSize=100, pageToken=token,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        out += [{"id": f["id"], "name": f["name"]} for f in resp.get("files", [])]
        token = resp.get("nextPageToken")
        if not token:
            break
    return out


def list_files(folder_id: str) -> list[dict[str, Any]]:
    svc = _service()
    q = f"'{folder_id}' in parents and trashed = false"
    out, token = [], None
    while True:
        resp = svc.files().list(
            q=q, fields="nextPageToken, files(id, name, mimeType, webViewLink)",
            pageSize=200, pageToken=token,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        out += resp.get("files", [])
        token = resp.get("nextPageToken")
        if not token:
            break
    return out


def download_file_by_id(file_id: str, mime: str = "") -> tuple[bytes, str]:
    """Baixa um arquivo por ID (exporta Google-native p/ PDF). Retorna (bytes, mime)."""
    import io as _io
    from googleapiclient.http import MediaIoBaseDownload
    svc = _service()
    buf = _io.BytesIO()
    if mime in GOOGLE_EXPORTABLE:
        req = svc.files().export_media(fileId=file_id, mimeType=GOOGLE_EXPORTABLE[mime])
        out_mime = GOOGLE_EXPORTABLE[mime]
    else:
        req = svc.files().get_media(fileId=file_id, supportsAllDrives=True)
        out_mime = mime or "application/octet-stream"
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue(), out_mime


def download_documents(folder_id: str, max_files: int = 25) -> list[dict[str, Any]]:
    """Baixa os documentos (PDF/Docs) de uma pasta como bytes p/ enviar à Claude API."""
    from googleapiclient.http import MediaIoBaseDownload
    svc = _service()
    docs: list[dict[str, Any]] = []
    for f in list_files(folder_id)[:max_files]:
        mime = f["mimeType"]
        if mime == "application/vnd.google-apps.folder":
            continue
        buf = io.BytesIO()
        try:
            if mime in GOOGLE_EXPORTABLE:
                req = svc.files().export_media(fileId=f["id"], mimeType=GOOGLE_EXPORTABLE[mime])
                out_mime = GOOGLE_EXPORTABLE[mime]
            else:
                req = svc.files().get_media(fileId=f["id"], supportsAllDrives=True)
                out_mime = mime
            dl = MediaIoBaseDownload(buf, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        except Exception:  # noqa: BLE001  (pula arquivo problemático, não trava a DD)
            continue
        docs.append({
            "name": f["name"], "mime": out_mime, "data": buf.getvalue(),
            "link": f.get("webViewLink", ""),
        })
    return docs
