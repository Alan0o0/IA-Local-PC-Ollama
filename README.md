# Agente de Estudos Local

Assistente de estudos que roda inteiramente no computador com Ollama e modelos de código aberto. Não usa chave de API, conta, serviço em nuvem ou cobrança por mensagem.

## Inicialização

No Windows, abra o Prompt de Comando ou PowerShell e execute uma vez:

```powershell
winget install Ollama.Ollama
ollama pull llama3.2
```

Feche e abra o terminal depois da instalação do Ollama. Em seguida, entre na aplicação e inicie-a:

```powershell
cd "C:\Users\oalan\Documents\IA-Local\Agente-de-IA-Estudos\agente-estudos"
uv sync
uv run streamlit run app/streamlit_app.py
```

No primeiro uso, o Streamlit pode pedir um e-mail: deixe em branco e pressione Enter. Abra a URL local exibida, normalmente `http://localhost:8501`. Mantenha o terminal aberto enquanto usa o agente e use `Ctrl+C` para encerrá-lo.

## Configuração

Copie `agente-estudos/.env.example` para `agente-estudos/.env` (ou edite o `.env` existente):

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_NUM_CTX=8192
```

- `OLLAMA_HOST`: Endereço do servidor Ollama local (mantenha `localhost` para uso estritamente local e offline).
- `OLLAMA_MODEL`: Nome do modelo que o chat utilizará (veja as opções abaixo).
- `OLLAMA_NUM_CTX`: Janela de contexto em tokens enviada ao Ollama. O padrão nativo do Ollama é de apenas 2.048 tokens (faz o assistente esquecer o começo de conversas médias). Definimos **8.192 tokens** por padrão, o que garante cerca de 25 a 30 páginas de memória contínua sem consumir memória RAM excessiva.

---

## Modelos Suportados (Gratuitos, Leves e Recentes)

Todos os modelos abaixo são **100% gratuitos**, rodam localmente sem internet e não exigem cadastro. Você pode baixar qualquer um deles e alternar alterando o `OLLAMA_MODEL` no seu `.env`:

| Modelo | Comando de Download | Tamanho do Download | RAM Mínima Recomendada | Destaque |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3.2 (3B)** *(Padrão)* | `ollama pull llama3.2` | ~2.0 GB | 4 GB | Equilibrado, rápido e ótimo para uso geral. Lançado no final de 2024 pela Meta. |
| **Qwen 2.5 (3B)** | `ollama pull qwen2.5:3b` | ~2.0 GB | 4 GB | Excelente fluência em português do Brasil e estruturação de matérias. |
| **Qwen 2.5 (7B)** | `ollama pull qwen2.5:7b` | ~4.5 GB | 8 GB - 16 GB | Versão mais inteligente do Qwen para quem tem um PC um pouco mais forte. |
| **DeepSeek-R1 (1.5B)** | `ollama pull deepseek-r1:1.5b` | ~1.1 GB | 4 GB | Ultraleve (2025). Modelo com raciocínio passo a passo (*chain-of-thought*). |
| **DeepSeek-R1 (7B / 8B)** | `ollama pull deepseek-r1:7b` | ~4.7 GB | 8 GB - 16 GB | Raciocínio aprofundado, ideal para resolução de questões e exercícios complexos. |
| **Gemma 2 (2B)** | `ollama pull gemma2:2b` | ~1.6 GB | 4 GB | Desenvolvido pelo Google, ultrarrápido e com respostas muito concisas. |

### Como alternar para outro modelo:
1. Baixe o modelo desejado no terminal (exemplo: `ollama pull qwen2.5:3b`).
2. No arquivo `agente-estudos/.env`, altere:
   ```env
   OLLAMA_MODEL=qwen2.5:3b
   ```
3. Reinicie o Streamlit (ou recarregue a página). O chat já iniciará com o novo modelo, mantendo todas as skills e histórico.

---

## O que o agente faz

- Chat com respostas em streaming.
- Memória durante a conversa e histórico local na barra lateral.
- Logs locais de modelo, duração e tokens, sem gravar o texto das mensagens.
- Plano de estudos personalizado e revisão ativa.

As conversas ficam em `agente-estudos/data/conversations/` e os logs em `agente-estudos/data/logs/`. Esses diretórios não entram no Git.

## Skills que orientam o agente

As regras abaixo são carregadas a cada resposta, portanto não são apenas documentação.

### Plano de estudos

Quando a pessoa pede um plano, o agente primeiro coleta somente o que falta: objetivo, datas de início e fim, disponibilidade e nível atual. Com esses dados, ele organiza módulos por pré-requisito, reserva margem para imprevistos, programa revisões em D+1/D+3/D+7, inclui entregáveis concretos e checkpoints semanais. Se o conteúdo não couber, prioriza o essencial e explica o que ficou opcional. Regras completas: [skills/plano-de-estudos/SKILL.md](skills/plano-de-estudos/SKILL.md).

### Revisão ativa

Quando a pessoa pede flashcards ou quiz, o agente pede o material ou tópico se ele ainda não foi informado. A resposta traz de 5 a 10 flashcards, exatamente 5 questões de múltipla escolha e um gabarito comentado. Regras completas: [skills/revisao-ativa/SKILL.md](skills/revisao-ativa/SKILL.md).

## Estrutura

```text
Agente-de-IA-Estudos/
├── skills/                         # comportamento do agente
│   ├── plano-de-estudos/SKILL.md
│   └── revisao-ativa/SKILL.md
└── agente-estudos/
    ├── app/local_chat.py          # Ollama, skills, memória e logs
    ├── app/streamlit_app.py      # interface de chat
    ├── tests/unit/                # testes locais
    ├── .env
    ├── .env.example
    └── pyproject.toml
```

## Testes

```powershell
cd agente-estudos
uv run pytest tests/unit -q
```
