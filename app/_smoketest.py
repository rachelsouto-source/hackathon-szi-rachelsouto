"""
Smoke test da API em modo demo (não precisa de credenciais).

Complementa `_smoketest_v2.py`, que cobre o núcleo. Este cobre o contrato HTTP.

    python app/_smoketest.py
"""
import os

os.environ["DEMO_MODE"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

c = TestClient(main.app)

# --- /api/health precisa DIZER o que falta -------------------------------- #
h = c.get("/api/health").json()
assert h["versao"] == "2.0", h
assert h["modo"] == "demo"
assert "itens" in h and "drive" in h["itens"], "health não diagnostica capacidades"
assert h["aviso"], "modo demo sem aviso explícito — foi assim que o v1 enganou todo mundo"
assert "EXEMPLOS FIXOS" in h["aviso"]
print(f"health: modo={h['modo']} · faltando={h['faltando_essencial']}")
for nome, it in h["itens"].items():
    print(f"  {'✅' if it['ativo'] else '❌'} {nome}"
          + (f" — {it['falta'][:70]}" if not it["ativo"] else ""))

# --- Lista só demos cujos arquivos existem -------------------------------- #
emp = c.get("/api/empreendimentos").json()
assert emp["itens"], "lista vazia"
assert all("EXEMPLO FIXO" in i["name"] for i in emp["itens"]), \
    "demo precisa ser rotulado como exemplo"
print(f"\nempreendimentos: {[i['name'] for i in emp['itens']]}")

# --- Auditoria em demo ----------------------------------------------------- #
eid, nome = emp["itens"][-1]["id"], emp["itens"][-1]["name"]
r = c.post("/api/dd", json={"id": eid, "nome": nome}).json()
assert r["modo"] == "demo"
assert r["job"] is None, "demo não dispara job"
res = r["resultado"]
assert res["demo"] is True
assert len(res["achados"]) >= 10, f"poucos achados: {len(res['achados'])}"
assert "exemplo estático" in res["markdown"], "parecer demo sem aviso de que é exemplo"
assert "Recomendação:" not in res["markdown"], \
    "não deve emitir recomendação automática (GO/NO-GO é decisão humana — §12.3)"
c_ = res["contadores"]
print(f"\nauditoria demo: {len(res['achados'])} achados "
      f"({c_['criticos']} críticos, {c_['atencao']} atenção, {c_['ok']} ok)")

# --- Endpoints do v2 existem ----------------------------------------------- #
for rota, esperado in [
    ("/api/dd/job/inexistente", 404),
    ("/api/dd/NAOEXISTE/livro", 404),
    ("/api/dd/NAOEXISTE/historico", 200),
    ("/api/dd/NAOEXISTE/base-conhecimento", 200),
]:
    got = c.get(rota).status_code
    assert got == esperado, f"{rota}: esperava {esperado}, veio {got}"
print("rotas v2: job / livro / historico / base-conhecimento respondem")

assert c.post("/api/dd/NAOEXISTE/contestar",
              json={"afirmacao_id": "AF-001", "argumento": "x"}).status_code == 400
assert c.post("/api/dd/NAOEXISTE/aceitar", json={"ids": ["AF-001"]}).status_code == 400
print("rotas de contestação/aceite respondem")

# --- Página --------------------------------------------------------------- #
page = c.get("/")
assert "Auditor de DD" in page.text
assert "Auditar agora" in page.text, "botão não reflete que a análise é sempre refeita"
assert "decisão humana" in page.text, "página não declara que GO/NO-GO é do humano"
print("\nOK — API v2 funcionando ponta a ponta em modo demo.")
