# lessons.md — Erros encontrados (causa e solução)

Registro de problemas reais enfrentados durante a construção do projeto.

---

## L1 — `CLAUDE.md` colide com a pasta `claude.md/` no Windows
- **Sintoma:** ao tentar criar um arquivo `CLAUDE.md` na raiz do projeto, o sistema
  retornou `EISDIR: illegal operation on a directory` / pediu para "ler o arquivo antes".
- **Causa:** o Windows é **case-insensitive**. A pasta de entrega exigida pelo hackathon
  se chama `claude.md/`; um arquivo `CLAUDE.md` na mesma raiz é tratado como o mesmo nome
  e colide com a pasta.
- **Solução:** usar `README.md` como contexto na raiz e colocar o `CLAUDE.md` de contexto
  **dentro** da pasta `claude.md/` (diretório diferente, sem colisão).
- **Lição:** em projetos com a convenção de pastas `claude.md/ lessons.md/ memory.md/`,
  nunca criar arquivos homônimos no mesmo diretório das pastas.

---

## L2 — Áreas divergentes entre fontes não são "erro de digitação"
- **Sintoma:** matrícula (1.382,40 m²), cadastro PMF (1.145,10 m²) e topográfico
  (1.158,96 m²) não batem.
- **Causa:** é o comportamento esperado de terrenos antigos — cada base foi medida em
  época/critério diferente. O topográfico georreferenciado é a referência real.
- **Solução:** a regra R1 não "escolhe a certa": ela lista todas e aplica o gatilho de
  **3%** sobre (topográfico × matrícula) para exigir retificação. Mais de uma matrícula ⇒
  avaliar amembramento.
- **Lição:** a auditoria deve **expor a divergência e a ação**, não mascará-la.

---

## L3 — Nº de unidades inconsistente entre documentos
- **Sintoma:** EVA cita 68 unidades; documento de estrutura cita 69.
- **Causa:** documentos produzidos por fornecedores diferentes, em momentos diferentes do
  estudo preliminar.
- **Solução:** regra R2 compara o nº de unidades entre EVA × estrutura × EP e aponta a
  divergência como ponto de atenção (impacta VGV).
- **Lição:** números que aparecem em mais de um documento são ótimos "checksums" de
  consistência — sempre cruzar.

---

## L4 — Leitura de PDF: confiar no MCP do Drive em vez de parser próprio
- **Sintoma:** PDFs de sondagem/topografia têm layout complexo (tabelas, figuras).
- **Causa:** parsers genéricos de PDF erram muito em tabelas e plantas.
- **Solução:** usar o `read_file_content` do MCP do Google Drive, que devolve uma
  representação em linguagem natural já interpretada — mais robusto para formatos variados.
- **Lição:** preferir tool use (MCP) a reimplementar extração; menos código, mais robustez.

---

## L7 — Acento no nome do arquivo quebra o header HTTP de download
- **Sintoma:** `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xea` ao baixar a planilha
  do empreendimento "Jurerê Spot III".
- **Causa:** headers HTTP são latin-1; o `Content-Disposition` com `filename="...Jurerê..."`
  (ê) estourava na codificação.
- **Solução:** normalizar o nome do arquivo para ASCII puro (`unicodedata.normalize NFKD` +
  `encode('ascii','ignore')`) antes de montar o header.
- **Lição:** nomes de download devem ser ASCII no header (ou usar `filename*=UTF-8''` com
  percent-encoding).

## L8 — Leitura de PDF no servidor: enviar o PDF nativo à Claude API
- **Sintoma:** no app (sem o MCP do Drive), seria preciso extrair texto de PDFs complexos
  (sondagem, plantas) no servidor.
- **Causa:** parsers de PDF erram muito em tabelas/figuras.
- **Solução:** a Claude API aceita **document blocks** (PDF em base64) — o app baixa os bytes
  do Drive e envia o PDF direto, deixando o modelo ler nativamente. Google Docs/Sheets são
  exportados para PDF antes do envio.
- **Lição:** preferir a leitura nativa de documentos da API a reimplementar extração.

## L6 — Validar o escopo da DD com a especialista antes de codar regras
- **Sintoma:** a primeira versão (a) incluía a **DD Jurídica** dentro da DD Técnica;
  (b) atribuía o **zoneamento** ao EVA; (c) não tratava **SPU** em terreno de marinha.
- **Causa:** premissas tiradas só da leitura do parecer, sem validar o ritual real.
- **Solução:** a coordenadora corrigiu — a DD Jurídica é **consulta separada** (não entra);
  o zoneamento e as exigências legais vêm da **Viabilidade Técnica Construtiva** (documento
  do site da prefeitura); e **marinha ⇒ conferir SPU** + documentações.
- **Lição:** em domínios especializados, confirmar o escopo com quem opera o processo evita
  regras erradas. As fontes oficiais de cada dado importam tanto quanto o dado.

## L5 — Encoding ao manipular texto em pt-BR no shell
- **Sintoma:** `UnicodeEncodeError` ao imprimir texto com acentos/setas no terminal
  (cp1252) durante a extração inicial.
- **Causa:** terminal Windows em cp1252 não codifica caracteres como `→`.
- **Solução:** definir `PYTHONIOENCODING=utf-8` e salvar arquivos sempre em UTF-8.
- **Lição:** padronizar UTF-8 em todo I/O do projeto.
