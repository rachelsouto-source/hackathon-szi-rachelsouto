/* Auditor de DD Técnica — painel v2.
 *
 * O painel deixou de ser só um visualizador: é a SUPERFÍCIE DE CONTESTAÇÃO. Cada achado
 * pode ser contestado ("não é bem isso") ou aceito, e o backend reabre apenas o subgrafo
 * que dependia da afirmação contestada.
 *
 * A auditoria roda como job assíncrono e o painel faz polling — com loop de ferramentas
 * uma DD leva de 5 a 20 minutos e um POST síncrono estouraria o timeout do proxy.
 */
const $ = (id) => document.getElementById(id);
const ICONE = { "Crítico": "🔴", "Atenção": "🟡", "OK": "🟢" };
const ORIGEM_ROTULO = {
  documento_emp: "documento do empreendimento", base_historica: "base histórica",
  diario: "Diário de Lançamentos", repo_lancamento: "repo do lançamento",
  fonte_externa: "fonte externa", legislacao: "legislação", humano: "pessoa",
};

let ESTADO = { empId: null, dados: null, poll: null };

const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---------------------------------------------------------------- init ----
async function init() {
  try {
    const h = await fetch("/api/health").then((r) => r.json());
    const badge = $("modo");
    badge.textContent = h.modo === "demo" ? "MODO DEMO" : "PRODUÇÃO";
    badge.classList.add(h.modo === "demo" ? "demo" : "prod");
    renderAvisoModo(h);
  } catch { $("modo").textContent = "offline"; }

  try {
    const d = await fetch("/api/empreendimentos").then((r) => r.json());
    const sel = $("empreendimento");
    sel.innerHTML = "";
    (d.itens || []).forEach((it) => {
      const o = document.createElement("option");
      o.value = it.id;
      o.dataset.nome = it.name;
      o.dataset.empId = it.emp_id || "";
      o.textContent = it.rodadas
        ? `${it.name} — ${it.rodadas} auditoria(s)` : it.name;
      sel.appendChild(o);
    });
    if (!sel.options.length) sel.innerHTML = "<option>(nenhum empreendimento)</option>";
  } catch (e) { $("status").textContent = "Erro ao listar empreendimentos: " + e; }

  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => trocarAba(t.dataset.tab)));
  $("btn-gerar").addEventListener("click", auditar);
}

function renderAvisoModo(h) {
  const box = $("aviso-modo");
  const itens = Object.entries(h.itens || {});
  const desligados = itens.filter(([, v]) => !v.ativo);
  if (h.modo === "produção" && !desligados.length) { box.classList.add("hidden"); return; }

  box.classList.remove("hidden");
  box.className = "aviso " + (h.modo === "demo" ? "aviso-erro" : "aviso-alerta");
  let html = "";
  if (h.modo === "demo") {
    html += `<h3>⚠️ Modo demonstração — isto NÃO é uma auditoria</h3>
      <p>O conteúdo exibido são <strong>exemplos fixos versionados no repositório</strong>.
      Nenhum documento é lido do Drive e nenhuma análise é executada.
      Para operar de verdade, configure:</p>`;
  } else {
    html += `<h3>Funcionando com capacidades reduzidas</h3>
      <p>A auditoria roda, mas estas fontes estão desligadas:</p>`;
  }
  html += "<ul>";
  desligados.forEach(([k, v]) => {
    html += `<li><strong>${esc(k)}</strong>${v.essencial ? " <em>(essencial)</em>" : ""} — ${esc(v.falta)}`;
    if (v.beneficio) html += `<br/><span class="sub">Sem isso, perde-se: ${esc(v.beneficio)}</span>`;
    html += "</li>";
  });
  html += "</ul>";
  box.innerHTML = html;
}

function trocarAba(nome) {
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.tab === nome));
  document.querySelectorAll(".tabpane").forEach((p) =>
    p.classList.toggle("hidden", p.id !== "tab-" + nome));
}

function carregando(on) {
  $("btn-gerar").disabled = on;
  $("spin").classList.toggle("hidden", !on);
  $("btn-label").textContent = on ? "Auditando…" : "Auditar agora";
}

// ----------------------------------------------------------- auditoria ----
async function auditar() {
  const sel = $("empreendimento");
  const opt = sel.options[sel.selectedIndex];
  if (!opt || !opt.value) return;

  carregando(true);
  $("resultado").classList.add("hidden");
  $("progresso").classList.remove("hidden");
  $("progresso").innerHTML = "";
  $("status").textContent = "Varrendo a pasta e reconstruindo a análise do zero…";

  try {
    const res = await fetch("/api/dd", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: opt.value, nome: opt.dataset.nome || opt.textContent }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const d = await res.json();

    if (d.modo === "demo") {           // exemplo fixo: nada a acompanhar
      ESTADO.empId = null;
      render(d.resultado);
      $("status").textContent = "";
      carregando(false);
      return;
    }
    ESTADO.empId = opt.dataset.empId || null;
    acompanhar(d.job);
  } catch (e) {
    $("status").textContent = "Falha: " + e.message;
    carregando(false);
  }
}

function acompanhar(jobId) {
  clearInterval(ESTADO.poll);
  let vistos = 0;
  ESTADO.poll = setInterval(async () => {
    let j;
    try { j = await fetch(`/api/dd/job/${jobId}`).then((r) => r.json()); }
    catch { return; }

    (j.progresso || []).slice(vistos).forEach((m) => {
      const li = document.createElement("li");
      li.textContent = m;
      $("progresso").appendChild(li);
      $("progresso").scrollTop = $("progresso").scrollHeight;
    });
    vistos = (j.progresso || []).length;

    if (j.estado === "pronto") {
      clearInterval(ESTADO.poll);
      carregando(false);
      $("status").textContent = "";
      render(j.resultado);
    } else if (j.estado === "erro") {
      clearInterval(ESTADO.poll);
      carregando(false);
      $("status").textContent = "Falha na auditoria: " + j.erro;
    } else {
      $("status").textContent =
        j.estado === "na_fila" ? "Na fila…" : "Auditando — isto pode levar alguns minutos.";
    }
  }, 2000);
}

// -------------------------------------------------------------- render ----
function render(r) {
  ESTADO.dados = r;
  $("resultado").classList.remove("hidden");
  $("progresso").classList.add("hidden");

  const perf = r.perfil || {};
  const ctx = [perf.cidade && `${perf.cidade}/${perf.uf || ""}`, perf.regime_dominial,
               (perf.flags || []).join(", ")].filter(Boolean).join(" · ");
  $("res-nome").textContent =
    `${r.nome}${r.rodada ? ` — rodada ${r.rodada}` : ""}${ctx ? " · " + ctx : ""}`;

  if (ESTADO.empId) {
    $("link-xlsx").href = `/api/dd/${ESTADO.empId}/xlsx`;
    $("link-docx").href = `/api/dd/${ESTADO.empId}/docx`;
  } else {
    $("link-xlsx").classList.add("hidden");
    $("link-docx").classList.add("hidden");
  }

  renderExposicao(r.exposicao || {}, r.demo);
  renderContadores(r.contadores || {});
  renderAchados(r.achados || []);
  renderLacunas(r.lacunas || [], r.perguntas_ao_humano || []);
  renderPrecedentes(r.precedentes || []);
  renderMudancas(r.changelog || {});
  renderCobertura(r.cobertura || {});
  $("parecer").innerHTML = md(r.markdown || "");
  renderTrilha(r.trilha || []);
  trocarAba("achados");
}

function renderExposicao(e, demo) {
  const box = $("exposicao");
  if (demo) {
    box.innerHTML = `<div class="exp-demo">Exemplo fixo do repositório — não é uma auditoria.</div>`;
    return;
  }
  let h = "<h3>Exposição técnica</h3>";
  if (e.situacao) h += `<p class="exp-situacao">${esc(e.situacao)}</p>`;
  const bloco = (t, xs, cls) => (xs && xs.length)
    ? `<div class="exp-bloco ${cls}"><h4>${t}</h4><ul>${
        xs.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>` : "";
  h += bloco("Divergências", e.divergencias, "div");
  h += bloco("Pontos de atenção", e.pontos_de_atencao, "aten");
  h += bloco("O que falta para concluir", e.o_que_falta_para_concluir, "falta");
  if (e.impacto_custo_prazo)
    h += `<p><strong>Impacto de custo e prazo:</strong> ${esc(e.impacto_custo_prazo)}</p>`;
  h += `<p class="exp-humana">A recomendação de <strong>GO / GO COM RESSALVAS / NO-GO</strong>
        é decisão humana. O Auditor apresenta a exposição técnica e a evidência.</p>`;
  box.innerHTML = h;
}

function renderContadores(c) {
  const item = (v, r, cls) =>
    `<div class="kpi ${cls}"><span class="kpi-n">${v ?? 0}</span><span class="kpi-r">${r}</span></div>`;
  $("resumo").innerHTML =
    item(c.criticos, "críticos", "k-crit") + item(c.atencao, "atenção", "k-aten") +
    item(c.ok, "ok", "k-ok") + item(c.lacunas, "lacunas", "k-lac") +
    item(c.documentos_lidos, "docs lidos", "") +
    item(c.nao_lidos_criticos, "não lidos", c.nao_lidos_criticos ? "k-crit" : "") +
    item(c.precedentes, "precedentes", "") + item(c.consultas, "consultas", "");
  $("c-lac").textContent = c.lacunas || "";
  $("c-prec").textContent = c.precedentes || "";
}

function classeSev(s) {
  return ({ "Crítico": "crit", "Atenção": "aten", "OK": "ok" })[s] || "";
}

function renderAchados(as) {
  if (!as.length) { $("tab-achados").innerHTML = "<p class='vazio'>Nenhum achado.</p>"; return; }
  $("tab-achados").innerHTML = as.map((a) => {
    const ev = (a.evidencias || []).map((e) => `
      <li class="ev">
        <span class="ev-origem">${esc(ORIGEM_ROTULO[e.origem] || e.origem)}</span>
        ${e.localizacao ? `<span class="ev-loc">${esc(e.localizacao)}</span>` : ""}
        <blockquote>${esc(e.trecho)}</blockquote>
        ${e.link ? `<a href="${esc(e.link)}" target="_blank" rel="noopener">abrir documento →</a>` : ""}
        ${e.sem_fonte_declarada
          ? `<div class="r10">⚠️ o documento não declara a própria fonte (R10)</div>` : ""}
      </li>`).join("");
    const cont = (a.contestacoes || []).filter((c) => c.veredito !== "improcede")
      .map((c) => `<div class="contest"><strong>${esc(c.autor)} (${esc(c.veredito)}):</strong>
                   ${esc(c.argumento)}</div>`).join("");
    return `
    <article class="achado sev-${classeSev(a.severidade)}">
      <header>
        <span class="sev">${ICONE[a.severidade] || "·"}</span>
        <span class="aid">${esc(a.id)}</span>
        <h4>${esc(a.texto)}</h4>
      </header>
      <div class="meta">${esc(a.disciplina)} · ${esc(a.tipo)} · confiança ${esc(a.confianca)}
        ${a.regra ? ` · regra ${esc(a.regra)}` : ""}
        ${a.estado && a.estado !== "aberta" ? ` · ${esc(a.estado)}` : ""}
        ${a.depende_de && a.depende_de.length ? ` · depende de ${a.depende_de.map(esc).join(", ")}` : ""}
      </div>
      ${a.premissa_normativa ? `<p class="premissa">Premissa: ${esc(a.premissa_normativa)}</p>` : ""}
      ${a.acao ? `<p class="acao"><strong>Ação:</strong> ${esc(a.acao)}</p>` : ""}
      ${ev ? `<ul class="evidencias">${ev}</ul>` : ""}
      ${cont}
      ${ESTADO.empId ? `
        <div class="acoes-achado">
          <button class="mini" data-contestar="${esc(a.id)}">✋ Não é bem isso</button>
          <button class="mini ok" data-aceitar="${esc(a.id)}">✔ Aceitar</button>
        </div>` : ""}
    </article>`;
  }).join("");

  $("tab-achados").querySelectorAll("[data-contestar]").forEach((b) =>
    b.addEventListener("click", () => contestar(b.dataset.contestar)));
  $("tab-achados").querySelectorAll("[data-aceitar]").forEach((b) =>
    b.addEventListener("click", () => aceitar(b.dataset.aceitar)));
}

function renderLacunas(ls, perguntas) {
  let h = "";
  if (ls.length) {
    h += "<h3>Lacunas abertas</h3>" + ls.map((l) => `
      <article class="lacuna">
        <header>${ICONE[l.severidade] || "·"} <span class="aid">${esc(l.id)}</span>
          <h4>${esc(l.texto)}</h4></header>
        <div class="meta">${esc(l.disciplina)}</div>
        ${l.o_que_falta ? `<p><strong>Falta:</strong> ${esc(l.o_que_falta)}</p>` : ""}
        ${l.como_obter ? `<p><strong>Como obter:</strong> ${esc(l.como_obter)}</p>` : ""}
        ${l.depende_de_humano
          ? `<p class="humano">👤 Depende de uma pessoa — credencial, acesso ou decisão.</p>` : ""}
      </article>`).join("");
  }
  if (perguntas.length) {
    h += "<h3>Perguntas ao humano</h3>" + perguntas.map((q) => `
      <article class="pergunta">
        <h4>${esc(q.o_que_preciso || "")}</h4>
        ${q.para_que ? `<p><strong>Para:</strong> ${esc(q.para_que)}</p>` : ""}
        ${(q.como_obter || q.onde) ? `<p><strong>Onde:</strong> ${esc(q.como_obter || q.onde)}</p>` : ""}
        ${q.por_que_nao_automatico
          ? `<p class="sub">Por que não é automático: ${esc(q.por_que_nao_automatico)}</p>` : ""}
        ${q.bloqueia ? `<p><strong>Bloqueia:</strong> ${esc(q.bloqueia)}</p>` : ""}
      </article>`).join("");
  }
  $("tab-lacunas").innerHTML = h ||
    "<p class='vazio'>Nenhuma lacuna aberta — todas as conclusões têm evidência.</p>";
}

function renderPrecedentes(ps) {
  if (!ps.length) {
    $("tab-precedentes").innerHTML = `<div class="ausencia">
      <h4>Nenhum precedente recuperado</h4>
      <p>Declarar a ausência é informação: pode significar que a base histórica ainda não
      cobre casos comparáveis — e não que eles não existam. Hoje a base cobre 4
      empreendimentos; a fila dos demais está pausada.</p></div>`;
    return;
  }
  $("tab-precedentes").innerHTML = ps.map((p) => `
    <blockquote class="precedente">
      <h4>${esc(p.empreendimento || "—")}${p.emp_id ? ` [${esc(p.emp_id)}]` : ""}
        ${p.distancia_ou_relacao ? `<span class="rel">${esc(p.distancia_ou_relacao)}</span>` : ""}</h4>
      ${p.o_que_aconteceu_la ? `<p>${esc(p.o_que_aconteceu_la)}</p>` : ""}
      ${p.por_que_se_aplica_aqui
        ? `<p><strong>Aplicação a este caso:</strong> ${esc(p.por_que_se_aplica_aqui)}</p>` : ""}
      <footer>${esc(p.fonte || "")}
        ${p.link ? ` · <a href="${esc(p.link)}" target="_blank" rel="noopener">documento</a>` : ""}
      </footer>
    </blockquote>`).join("") +
    `<p class="nota">Precedente não é prova: embasa recomendação, nunca fato sobre este terreno.</p>`;
}

function renderMudancas(c) {
  if (!c || c.primeira_rodada) {
    $("tab-mudancas").innerHTML =
      "<p class='vazio'>Primeira auditoria deste empreendimento — não há rodada anterior.</p>";
    return;
  }
  let h = "";
  const d = c.documentos || {};
  if ((d.novos || []).length || (d.alterados || []).length || (d.removidos || []).length) {
    h += "<h3>Documentos</h3><ul class='docs'>";
    (d.novos || []).forEach((x) => h += `<li>➕ <code>${esc(x.caminho)}/${esc(x.nome)}</code>
      <span class="sub">${esc((x.modificado || "").slice(0, 10))}</span></li>`);
    (d.alterados || []).forEach((x) => h += `<li>🔄 <code>${esc(x.caminho)}/${esc(x.nome)}</code>
      <span class="sub">${esc((x.modificado || "").slice(0, 10))}</span></li>`);
    if ((d.removidos || []).length) h += `<li>➖ ${d.removidos.length} arquivo(s) removido(s)</li>`;
    h += "</ul>";
  }
  const grupo = (titulo, xs) => (xs && xs.length)
    ? `<h3>${titulo}</h3><ul class='mud'>${xs.map((i) =>
        `<li>${ICONE[i.severidade] || "·"} <span class="aid">${esc(i.id)}</span> ${esc(i.texto)}
         ${i.de ? `<span class="sub">${esc(i.de)} → ${esc(i.para)}</span>` : ""}</li>`).join("")}</ul>`
    : "";
  h += grupo("🆕 Novos achados", c.novos) + grupo("✅ Fechados", c.fechados) +
       grupo("⬆️ Agravados", c.agravados) + grupo("⬇️ Aliviados", c.aliviados) +
       grupo("🆕 Lacunas novas", c.lacunas_novas) + grupo("✅ Lacunas fechadas", c.lacunas_fechadas);
  $("tab-mudancas").innerHTML = h || "<p class='vazio'>Nenhuma mudança material.</p>";
}

function renderCobertura(c) {
  if (!c || !c.total) { $("tab-cobertura").innerHTML = "<p class='vazio'>Sem dados.</p>"; return; }
  const lista = (xs, cls) => `<ul class="cob ${cls}">${xs.map((x) =>
    `<li><code>${esc(x.caminho)}/${esc(x.nome)}</code>
     ${x.disciplina ? `<span class="sub">${esc(x.disciplina)}</span>` : ""}
     ${x.link ? ` <a href="${esc(x.link)}" target="_blank" rel="noopener">abrir</a>` : ""}</li>`).join("")}</ul>`;
  let h = `<p>Varridos <strong>${c.total}</strong> arquivos em ${c.total_pastas} pastas.</p>`;
  const crit = c.nao_lidos_criticos || [];
  if (crit.length) {
    h += `<h3 class="alerta">❌ ${crit.length} documento(s) relevante(s) NÃO lido(s)</h3>
      <p class="sub">“Existe e não foi lido” tem a mesma severidade de “não existe” (R6.b).</p>`
      + lista(crit, "ruim");
  }
  if ((c.requer_ferramenta || []).length) {
    h += `<h3>🛠️ ${c.requer_ferramenta.length} arquivo(s) exigem ferramenta específica</h3>`
      + lista(c.requer_ferramenta, "");
  }
  if ((c.pastas_vazias || []).length) {
    h += `<h3>📂 ${c.pastas_vazias.length} pasta(s) vazia(s)</h3>
      <p class="sub">Pasta vazia é documento AUSENTE, não “disponível” (R6.a).</p>
      <ul class="cob">${c.pastas_vazias.map((v) => `<li><code>${esc(v)}</code></li>`).join("")}</ul>`;
  }
  h += `<h3>✅ ${(c.lidos || []).length} lido(s)</h3>` + lista(c.lidos || [], "bom");
  h += `<p class="sub">${c.nao_aplicaveis || 0} arquivo(s) não aplicáveis (imagens, mídia, temporários).</p>`;
  $("tab-cobertura").innerHTML = h;
}

function renderTrilha(t) {
  $("tab-trilha").innerHTML = t.length
    ? `<ul class="trilha">${t.map((c) =>
        `<li><code>${esc((c.em || "").slice(11, 19))}</code>
         <strong>${esc(c.ferramenta)}</strong> — ${esc(c.resumo)}</li>`).join("")}</ul>`
    : "<p class='vazio'>Sem trilha registrada.</p>";
}

// --------------------------------------------------------- contestação ----
async function contestar(id) {
  const arg = prompt(
    `Contestar ${id}.\n\nO que está errado? Seja específico — o Auditor vai reabrir esta ` +
    `afirmação e todas as que dependem dela na próxima rodada.`);
  if (!arg || !ESTADO.empId) return;
  try {
    const r = await fetch(`/api/dd/${ESTADO.empId}/contestar`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ afirmacao_id: id, argumento: arg }),
    }).then((x) => x.json());
    alert(r.mensagem || "Contestação registrada.");
  } catch (e) { alert("Falha ao contestar: " + e.message); }
}

async function aceitar(id) {
  if (!ESTADO.empId) return;
  try {
    await fetch(`/api/dd/${ESTADO.empId}/aceitar`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids: [id] }),
    });
    alert(`${id} aceito. Afirmações aceitas alimentam a base de conhecimento — ` +
          `nada entra na base sem revisão humana.`);
  } catch (e) { alert("Falha: " + e.message); }
}

// ------------------------------------------------------------ markdown ----
function md(s) {
  const linhas = esc(s).split("\n");
  let out = "", emLista = false, emTabela = false;
  const inline = (t) => t
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/(^|[\s(])_([^_]+)_(?=[\s.,;:)]|$)/g, "$1<em>$2</em>");
  for (const l of linhas) {
    if (/^\|/.test(l)) {
      if (/^\|[\s:|-]+\|?$/.test(l)) continue;
      if (!emTabela) { out += "<table>"; emTabela = true; }
      out += "<tr>" + l.split("|").slice(1, -1)
        .map((c) => `<td>${inline(c.trim())}</td>`).join("") + "</tr>";
      continue;
    }
    if (emTabela) { out += "</table>"; emTabela = false; }
    const li = l.match(/^\s*[-*]\s+(.*)/);
    if (li) {
      if (!emLista) { out += "<ul>"; emLista = true; }
      out += `<li>${inline(li[1])}</li>`;
      continue;
    }
    if (emLista) { out += "</ul>"; emLista = false; }
    const h = l.match(/^(#{1,4})\s+(.*)/);
    if (h) { out += `<h${h[1].length + 1}>${inline(h[2])}</h${h[1].length + 1}>`; continue; }
    if (/^>\s?/.test(l)) { out += `<blockquote>${inline(l.replace(/^>\s?/, ""))}</blockquote>`; continue; }
    if (!l.trim()) continue;
    out += `<p>${inline(l)}</p>`;
  }
  if (emLista) out += "</ul>";
  if (emTabela) out += "</table>";
  return out;
}

init();
