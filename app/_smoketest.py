"""Smoke test do app em modo demo (não precisa de credenciais)."""
import os
os.environ["DEMO_MODE"] = "1"

from fastapi.testclient import TestClient
import main

c = TestClient(main.app)

h = c.get("/api/health").json()
print("health:", h)
assert h["modo"] == "demo"

emp = c.get("/api/empreendimentos").json()
print("empreendimentos:", emp["itens"])
assert emp["itens"], "lista vazia"

eid = emp["itens"][0]["id"]
nome = emp["itens"][0]["name"]
r = c.post("/api/dd", json={"id": eid, "nome": nome}).json()
print("rid:", r["rid"], "| achados:", len(r["achados"]), "| reco:", r["negocio"].get("recomendacao"))
assert len(r["achados"]) >= 10
assert "PARECER TÉCNICO" in r["parecer_md"]

x = c.get(r["xlsx_url"])
print("xlsx bytes:", len(x.content), "| content-type:", x.headers.get("content-type"))
assert x.status_code == 200 and len(x.content) > 2000

page = c.get("/")
assert "Auditor de DD" in page.text
print("\nOK — app demo funcionando ponta a ponta.")
