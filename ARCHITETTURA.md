# Manifold Harness — Pi Coding Agent Edition

## Architettura

Orchestratore Node.js ESM che esegue 20 sessioni consecutive di pi-coding-agent
per generare un "AI Manifold Brief" completo.

### Stack Translation Map

| Originale (Claude Code SDK)     | Nuovo (pi-coding-agent)                    |
|---------------------------------|--------------------------------------------|
| Python + claude-code-sdk        | Node.js ESM + spawn("pi")                  |
| ClaudeSDKClient                 | `pi -p --mode json` (process spawn)        |
| system_prompt param             | `--system-prompt` flag                     |
| allowed_tools param             | `--tools read,write,edit,bash,...` flag     |
| WebSearch built-in              | `bash curl` + brave-search skill           |
| WebFetch built-in               | `bash curl`                                |
| Puppeteer MCP                   | browser-tools skill                        |
| PreToolUse hook (Python)        | damage-control.ts extension (in-process)   |
| CLAUDE_CODE_OAUTH_TOKEN         | ANTHROPIC_API_KEY (o altro provider)       |
| Single provider (Claude)        | 20+ provider (anthropic, openai, google..) |
| Max turns: 1000                 | Session timeout + compaction               |
| Sandbox mode                    | Damage-control extension                   |

### Flow

```
CLI (cli.mjs)
  ↓
Main Loop (agent.mjs:runManifoldAgent)
  ├── loadState() / initState()
  ├── Loop 20 sessioni:
  │   ├── getNextAction() → {cycle, step, index}
  │   ├── buildPrompt() → context + template
  │   ├── runPiSession() → spawn pi -p --mode json
  │   │   ├── Stream JSON events (stdout)
  │   │   ├── Parse: message_update, tool_execution_*, error
  │   │   └── Return {status, responseText}
  │   ├── advanceStep() → salva stato
  │   └── sleep(3s)
  └── Complete
```

### Vantaggi Pi vs Claude Code

1. **Multi-provider**: Switch modello mid-run (Anthropic → OpenAI → Google)
2. **Thinking levels**: Controllo granulare del ragionamento (off → xhigh)
3. **Extensions in-process**: TypeScript nativo, nessun subprocess overhead
4. **Open source**: Codice visibile, fork possibile, community-driven
5. **Session branching**: Tree JSONL con fork/resume (futuro: retry branch)
6. **Costo flessibile**: Mix modelli cheap (flash) per scout + heavy (opus) per analysis

### Sessioni

| # | Ciclo | Step                        | Output                     |
|---|-------|-----------------------------|----------------------------|
| 1 | C1    | Swipe Analysis              | data/swipe/                |
| 2 | C1    | Scrape Research             | data/scrape/               |
| 3 | C1    | Source Extraction            | data/source/               |
| 4 | C1    | Survey Processing           | data/survey/               |
| 5 | C1    | Market Spec Generation      | market_spec.txt            |
| 6 | C2    | 01 Buyer Base               | chapters/01_buyer_base.txt |
| 7 | C2    | 02 Pain Matrix              | chapters/02_pain_matrix.txt|
| … | C2    | …                           | …                          |
|20 | C2    | 15 Ejection Triggers        | chapters/15_ejection_triggers.txt |

### Uso

```bash
# Con Anthropic (default)
export ANTHROPIC_API_KEY=sk-ant-...
node src/cli.mjs --client "NomeCliente" --product-info "Descrizione prodotto/mercato"

# Con OpenAI
export OPENAI_API_KEY=sk-...
node src/cli.mjs --client "NomeCliente" --provider openai --model gpt-4o --product-info "..."

# Dry run (1 sessione)
node src/cli.mjs --client "Test" --product-info "Test" --max-iterations 1

# Con input files
node src/cli.mjs --client "NomeCliente" --input-dir ./dati_cliente --product-info "..."

# Resume dopo crash
node src/cli.mjs --client "NomeCliente" --product-info "..."
# (riprende automaticamente dall'ultimo step completato)
```
