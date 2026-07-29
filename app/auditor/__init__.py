"""
Auditor de DD Técnica — núcleo v2.

Biblioteca headless: nenhuma interface (API, painel, CLI, skill) contém lógica de
auditoria. Todas chamam `auditor.pipeline.auditar()`. Ver §4.3-D1.
"""
__all__ = ["livro", "estado", "cartografo", "regras", "ferramentas", "agente",
           "relatorio", "pipeline", "fontes"]
