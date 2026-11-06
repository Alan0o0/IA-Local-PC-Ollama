# Agente de Estudos Local

Assistente de estudos que roda inteiramente no computador com Ollama e o modelo `llama3.2`. Não usa chave de API, conta, serviço em nuvem ou cobrança por mensagem.

## Inicialização

No Windows, abra o Prompt de Comando ou PowerShell e execute uma vez:

```powershell
winget install Ollama.Ollama
ollama pull llama3.2
```

Feche e abra o terminal depois da instalação do Ollama. Em seguida, entre na aplicação e inicie-a:

```powershell
cd "C:\Users\oalan\Documents\Agente IA estudos\Agente-de-IA-Estudos\agente-estudos"
uv sync
uv run streamlit run app/streamlit_app.py
```

No primeiro uso, o Streamlit pode pedir um e-mail: deixe em branco e pressione Enter. Abra a URL local exibida, normalmente `http://localhost:8501`. Mantenha o terminal aberto enquanto usa o agente e use `Ctrl+C` para encerrá-lo.

## Configuração

Copie `agente-estudos/.env.example` para `agente-estudos/.env`. Os padrões são:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Não aponte `OLLAMA_HOST` para um servidor externo se quiser manter o uso estritamente local.

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
    ├── .env.example
    └── pyproject.toml
```

## Testes

```powershell
cd agente-estudos
uv run pytest tests/unit -q
```
