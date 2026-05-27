const $ = (id) => document.getElementById(id);
const SEVPILL = { "Crítico":["🔴","div"], "Critico":["🔴","div"], "Atenção":["🟡","pend"],
  "Atencao":["🟡","pend"], "OK":["🟢","ok"] };
const STCLS = { "OK":"ok", "Pendente":"pend", "Divergência":"div", "Divergencia":"div",
  "Não se aplica":"na", "Nao se aplica":"na" };

async function init() {
  try {
    const h = await fetch("/api/health").then(r => r.json());
    $("modo").textContent = h.modo === "demo" ? "MODO DEMO" : "PRODUÇÃO";
    $("modo").classList.add(h.modo === "demo" ? "demo" : "prod");
  } catch { $("modo").textContent = "offline"; }

  try {
    const data = await fetch("/api/empreendimentos").then(r => r.json());
    const sel = $("empreendimento");
    sel.innerHTML = "";
    (data.itens || []).forEach(it => {
      const o = document.createElement("option");
      o.value = it.id; o.textContent = it.name; o.dataset.nome = it.name;
      sel.appendChild(o);
    });
    if (!sel.options.length) sel.innerHTML = "<option>(nenhum empreendimento)</option>";
  } catch (e) { $("status").textContent = "Erro ao listar empreendimentos: " + e; }
}

function loading(on) {
  $("btn-gerar").disabled = on;
  $("spin").classList.toggle("hidden", !on);
  $("btn-label").textContent = on ? "Auditando…" : "Gerar DD";
}

async function gerar() {
  const sel = $("empreendimento");
  const opt = sel.options[sel.selectedIndex];
  if (!opt || !opt.value) return;
  loading(true);
  $("status").textContent = "Lendo os documentos no Drive e cruzando as informações…";
  $("resultado").classList.add("hidden");
  try {
    const res = await fetch("/api/dd", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: opt.value, nome: opt.dataset.nome || opt.textContent }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    render(await res.json());
    $("status").textContent = "";
  } catch (e) {
    $("status").textContent = "Falha: " + e.message;
  } finally { loading(false); }
}

function render(r) {
  $("resultado").classList.remove("hidden");
  $("res-nome").textContent = r.nome || "";

  const reco = (r.negocio && r.negocio.recomendacao) || "—";
  const cls = reco.includes("NO-GO") ? "nogo" : reco.includes("RESSALVAS") ? "ressalvas" : "go";
  $("recomendacao").className = "reco " + cls;
  $("recomendacao").textContent = "Recomendação: " + reco;

  // Google Doc: link real (se já criado) + botão "Gerar Google Doc" sob demanda
  window._rid = r.rid;
  const ld = $("link-doc"), note = $("doc-note"), bg = $("btn-gdoc");
  bg.classList.remove("hidden"); bg.disabled = false; bg.textContent = "📝 Gerar Google Doc";
  if (r.doc_url) {
    ld.href = r.doc_url; ld.classList.remove("hidden"); note.classList.add("hidden");
  } else {
    ld.classList.add("hidden"); note.classList.remove("hidden");
    note.textContent = "📄 Clique em “Gerar Google Doc” para criar o parecer no Google Docs (também é salvo automaticamente na pasta “07 - DD Técnica” do empreendimento).";
  }
  $("link-xlsx").href = r.xlsx_url;

  // Resumo (contagem por status)
  const cnt = { ok:0, pend:0, div:0, na:0 };
  (r.achados || []).forEach(a => { const c = STCLS[a.status]; if (c) cnt[c]++; });
  $("resumo").innerHTML =
    `<span class="chip ok"><b>${cnt.ok}</b> OK</span>
     <span class="chip pend"><b>${cnt.pend}</b> Pendentes</span>
     <span class="chip div"><b>${cnt.div}</b> Divergências</span>
     <span class="chip na"><b>${cnt.na}</b> N/A</span>`;

  // Tabela
  const tb = $("tabela").querySelector("tbody");
  tb.innerHTML = "";
  (r.achados || []).forEach(a => {
    const tr = document.createElement("tr");
    tr.className = "st" + (a.status || "").toLowerCase().replace(/[^a-z]/g, "");
    const stc = STCLS[a.status] || "na";
    const sev = SEVPILL[a.severidade] || ["",""];
    let fonte = (a.fonte || "");
    [a.link, a.link2].filter(Boolean).forEach((l, i, arr) => {
      fonte += ` <a href="${l}" target="_blank" class="src">🔗 abrir${arr.length>1?" "+(i+1):""}</a>`;
    });
    tr.innerHTML = `<td>${a.etapa||""}</td>
      <td><span class="pill ${stc}">${a.status||""}</span></td>
      <td>${sev[0]}</td><td>${a.observacao||""}</td>
      <td>${a.acao||""}</td><td>${fonte}</td>`;
    tb.appendChild(tr);
  });

  window._parecerMdOrig = r.parecer_md || "";
  window._sectionEdits = {};
  renderParecer(window._parecerMdOrig);
  setTab("achados");
  $("resultado").scrollIntoView({ behavior: "smooth" });
}

// ---- Parecer editável por seção ----

function parseSections(md) {
  // Divide o markdown em blocos: tudo antes do 1º ### é "preamble", depois cada ### é uma seção
  const lines = md.split("\n");
  const sections = [];
  let current = null;
  lines.forEach(line => {
    if (/^### /.test(line)) {
      if (current) sections.push(current);
      current = { title: line.slice(4).trim(), raw: line + "\n" };
    } else {
      if (current) current.raw += line + "\n";
      else {
        if (!sections.length) sections.push({ title: "__preamble__", raw: "" });
        sections[0].raw += line + "\n";
      }
    }
  });
  if (current) sections.push(current);
  return sections;
}

function renderParecer(md) {
  const sections = parseSections(md);
  const container = $("parecer");
  container.innerHTML = "";
  sections.forEach(sec => {
    if (sec.title === "__preamble__") {
      const div = document.createElement("div");
      div.className = "sec-preamble";
      div.innerHTML = mdToHtml(sec.raw);
      container.appendChild(div);
      return;
    }
    const key = sec.title;
    const block = document.createElement("div");
    block.className = "sec-block";
    block.dataset.key = key;

    // Cabeçalho da seção
    const head = document.createElement("div");
    head.className = "sec-head";
    head.innerHTML = `<h3>${key}</h3>
      <button class="btn-edit-sec" title="Editar esta seção">✏️ Editar</button>`;
    block.appendChild(head);

    // Conteúdo renderizado
    const view = document.createElement("div");
    view.className = "sec-content";
    const rawToUse = window._sectionEdits[key] !== undefined ? window._sectionEdits[key] : sec.raw;
    view.innerHTML = mdToHtml(rawToUse);
    block.appendChild(view);

    // Área de edição (oculta inicialmente)
    const editArea = document.createElement("div");
    editArea.className = "sec-edit hidden";
    editArea.innerHTML = `
      <textarea class="sec-textarea" rows="12" placeholder="Edite o conteúdo desta seção em markdown...">${rawToUse.replace(/^### .+\n/, "")}</textarea>
      <div class="sec-edit-actions">
        <label class="btn-img-label" title="Inserir imagem por URL">
          🖼️ Inserir imagem
          <input type="text" class="img-url-input" placeholder="Cole a URL da imagem e pressione Enter" style="display:none"/>
        </label>
        <button class="btn-save-sec">💾 Salvar seção</button>
        <button class="btn-cancel-sec">✕ Cancelar</button>
      </div>`;
    block.appendChild(editArea);

    // Eventos
    head.querySelector(".btn-edit-sec").addEventListener("click", () => {
      view.classList.add("hidden");
      editArea.classList.remove("hidden");
      head.querySelector(".btn-edit-sec").classList.add("hidden");
    });
    editArea.querySelector(".btn-cancel-sec").addEventListener("click", () => {
      editArea.classList.add("hidden");
      view.classList.remove("hidden");
      head.querySelector(".btn-edit-sec").classList.remove("hidden");
    });
    editArea.querySelector(".btn-save-sec").addEventListener("click", () => {
      const txt = editArea.querySelector(".sec-textarea").value;
      window._sectionEdits[key] = "### " + key + "\n" + txt;
      view.innerHTML = mdToHtml("### " + key + "\n" + txt);
      editArea.classList.add("hidden");
      view.classList.remove("hidden");
      head.querySelector(".btn-edit-sec").classList.remove("hidden");
      // feedback visual
      block.classList.add("sec-saved");
      setTimeout(() => block.classList.remove("sec-saved"), 1500);
    });
    // Inserir imagem por URL
    const imgLabel = editArea.querySelector(".btn-img-label");
    const imgInput = editArea.querySelector(".img-url-input");
    imgLabel.addEventListener("click", (e) => {
      e.stopPropagation();
      imgInput.style.display = imgInput.style.display === "none" ? "inline-block" : "none";
      if (imgInput.style.display !== "none") imgInput.focus();
    });
    imgInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const url = imgInput.value.trim();
        if (url) {
          const ta = editArea.querySelector(".sec-textarea");
          ta.value += `\n\n![imagem](${url})\n`;
          imgInput.value = "";
          imgInput.style.display = "none";
        }
      }
    });

    container.appendChild(block);
  });
}

function getCurrentParecer() {
  // Reconstrói o markdown com as edições aplicadas
  const sections = parseSections(window._parecerMdOrig || "");
  return sections.map(sec => {
    if (sec.title === "__preamble__") return sec.raw;
    return window._sectionEdits[sec.title] !== undefined
      ? window._sectionEdits[sec.title]
      : sec.raw;
  }).join("\n");
}

// markdown -> html simples (títulos, negrito, links, listas, tabelas, citações, hr)
function mdToHtml(md) {
  const esc = (s) => s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const inline = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<figure class="fig"><img src="$2" alt="$1" loading="lazy" referrerpolicy="no-referrer"/><figcaption>$1</figcaption></figure>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  const lines = md.split("\n");
  let html = "", i = 0, inUl = false;
  const closeUl = () => { if (inUl) { html += "</ul>"; inUl = false; } };
  while (i < lines.length) {
    let l = lines[i];
    if (/^\s*\|/.test(l)) { // tabela
      closeUl();
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) { rows.push(lines[i]); i++; }
      const cells = (row) => row.trim().replace(/^\||\|$/g,"").split("|").map(c=>c.trim());
      html += "<table>";
      rows.forEach((row, ri) => {
        if (/^\s*\|[\s:|-]+\|?\s*$/.test(row)) return; // separador
        const tag = ri === 0 ? "th" : "td";
        html += "<tr>" + cells(row).map(c=>`<${tag}>${inline(c)}</${tag}>`).join("") + "</tr>";
      });
      html += "</table>";
      continue;
    }
    if (/^::FIG:: /.test(l)) { closeUl(); const cap=l.slice(8); html += `<div class="figbox"><span class="figph">📷 Inserir imagem aqui</span><span class="figcap">Figura — ${cap}</span></div>`; }
    else if (/^### /.test(l)) { closeUl(); html += `<h3>${inline(l.slice(4))}</h3>`; }
    else if (/^## /.test(l)) { closeUl(); const t=l.slice(3); const m=t.match(/^(\d+)\.\s*(.+)/); const num=m?m[1]:""; const title=(m?m[2]:t).toUpperCase(); const concl=/CONCLUS/i.test(title)?" concl":""; html += `<div class="banner${concl}">${num?`<span class="bnum">${num}</span>`:""}<span class="btxt">${title}</span></div>`; }
    else if (/^# /.test(l)) { closeUl(); html += `<h1>${inline(l.slice(2))}</h1>`; }
    else if (/^> /.test(l)) { closeUl(); html += `<blockquote>${inline(l.slice(2))}</blockquote>`; }
    else if (/^\s*[-*] /.test(l)) { if (!inUl){html+="<ul>";inUl=true;} html += `<li>${inline(l.replace(/^\s*[-*] /,""))}</li>`; }
    else if (/^---+$/.test(l.trim())) { closeUl(); html += "<hr/>"; }
    else if (l.trim() === "") { closeUl(); }
    else { closeUl(); html += `<p>${inline(l)}</p>`; }
    i++;
  }
  closeUl();
  return html;
}

function setTab(name) {
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === name));
  $("tab-achados").classList.toggle("hidden", name !== "achados");
  $("tab-parecer").classList.toggle("hidden", name !== "parecer");
}

async function gerarGDoc() {
  const bg = $("btn-gdoc");
  if (!window._rid) return;
  bg.disabled = true; bg.textContent = "Gerando…";
  try {
    const parecerAtual = getCurrentParecer();
    const res = await fetch(`/api/dd/${window._rid}/gdoc`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parecer_md: parecerAtual }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    if (data.doc_url) {
      const ld = $("link-doc");
      ld.href = data.doc_url; ld.classList.remove("hidden");
      $("doc-note").classList.add("hidden");
      bg.textContent = "✓ Google Doc criado";
      window.open(data.doc_url, "_blank");
    } else if (data.download_url) {
      // demo: baixa o .doc
      window.location = data.download_url;
      $("doc-note").classList.remove("hidden");
      $("doc-note").textContent = data.msg || "Documento .doc gerado para download.";
      bg.disabled = false; bg.textContent = "📝 Gerar Google Doc";
    } else {
      $("doc-note").textContent = data.msg || "Não foi possível gerar o documento.";
      bg.disabled = false; bg.textContent = "📝 Gerar Google Doc";
    }
  } catch (e) {
    $("doc-note").classList.remove("hidden");
    $("doc-note").textContent = "Falha ao gerar Google Doc: " + e.message
      + " (requer credenciais de produção — Service Account).";
    bg.disabled = false; bg.textContent = "📝 Gerar Google Doc";
  }
}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => setTab(t.dataset.tab)));
$("btn-gerar").addEventListener("click", gerar);
$("btn-gdoc").addEventListener("click", gerarGDoc);
init();
