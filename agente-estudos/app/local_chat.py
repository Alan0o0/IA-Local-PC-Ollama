"""Persistência local e comunicação streaming com o Ollama."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4


DEFAULT_MODEL = "llama3.2"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"


class OllamaError(RuntimeError):
    """Erro de comunicação com o servidor Ollama local."""


def _data_dir() -> Path:
    configured = os.environ.get("LOCAL_DATA_DIR")
    return Path(configured) if configured else Path(__file__).resolve().parents[1] / "data"


def _conversations_dir() -> Path:
    return _data_dir() / "conversations"


def _conversation_path(conversation_id: str) -> Path:
    return _conversations_dir() / f"{conversation_id}.json"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def new_conversation() -> dict[str, Any]:
    conversation = {"id": uuid4().hex, "title": "Nova conversa", "messages": [], "updated_at": _now()}
    save_conversation(conversation)
    return conversation


def save_conversation(conversation: dict[str, Any]) -> None:
    conversation["updated_at"] = _now()
    path = _conversation_path(conversation["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(conversation, ensure_ascii=False, indent=2), encoding="utf-8")


def load_conversation(conversation_id: str) -> dict[str, Any] | None:
    path = _conversation_path(conversation_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_conversations() -> list[dict[str, Any]]:
    conversations: list[dict[str, Any]] = []
    for path in _conversations_dir().glob("*.json") if _conversations_dir().exists() else []:
        try:
            conversation = json.loads(path.read_text(encoding="utf-8"))
            conversations.append({key: conversation[key] for key in ("id", "title", "updated_at")})
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(conversations, key=lambda item: item["updated_at"], reverse=True)


def clear_conversation(conversation: dict[str, Any]) -> None:
    conversation["title"] = "Nova conversa"
    conversation["messages"] = []
    save_conversation(conversation)


def log_usage(response: dict[str, Any], *, model: str, success: bool) -> None:
    """Registra apenas métricas; o texto da conversa fica fora dos logs."""
    entry = {
        "timestamp": _now(),
        "model": model,
        "success": success,
        "prompt_tokens": response.get("prompt_eval_count"),
        "response_tokens": response.get("eval_count"),
        "total_duration_ns": response.get("total_duration"),
    }
    path = _data_dir() / "logs" / "usage.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def agent_instructions() -> str:
    """Carrega as regras de comportamento mantidas nas skills do projeto."""
    skill_files = (
        SKILLS_DIR / "plano-de-estudos" / "SKILL.md",
        SKILLS_DIR / "revisao-ativa" / "SKILL.md",
    )
    skills = "\n\n".join(path.read_text(encoding="utf-8") for path in skill_files)
    return (
        "Você é o Agente de Estudos local. Responda sempre em português do Brasil, "
        "com clareza e tom de mentor. Siga as skills abaixo quando o pedido se encaixar. "
        "Não alegue ter usado serviços externos ou salvo arquivos fora deste computador.\n\n"
        f"{skills}"
    )


def stream_chat(messages: list[dict[str, str]], model: str | None = None) -> Iterator[dict[str, Any]]:
    """Envia o histórico ao Ollama e produz cada objeto NDJSON recebido."""
    host = os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")
    selected_model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    payload = json.dumps(
        {
            "model": selected_model,
            "messages": [{"role": "system", "content": agent_instructions()}, *messages],
            "stream": True,
        }
    ).encode()
    request = urllib.request.Request(
        f"{host}/api/chat", data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            for line in response:
                if line.strip():
                    yield json.loads(line)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama retornou {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise OllamaError(
            "Não foi possível conectar ao Ollama local. Inicie-o e confirme OLLAMA_HOST."
        ) from error
