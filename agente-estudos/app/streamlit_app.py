"""Interface local de chat para o Agente de Estudos usando Ollama."""

from __future__ import annotations

import os

import streamlit as st

from local_chat import (
    DEFAULT_MODEL,
    OllamaError,
    clear_conversation,
    list_conversations,
    load_conversation,
    log_usage,
    new_conversation,
    save_conversation,
    stream_chat,
)


st.set_page_config(page_title="Agente de Estudos", page_icon="📚", layout="wide")
st.markdown("""<style>
    .stApp { background: #0e1117; } .block-container { max-width: 900px; }
    [data-testid="stSidebar"] { background: #171b24; }
</style>""", unsafe_allow_html=True)

if "conversation" not in st.session_state:
    st.session_state.conversation = new_conversation()

conversation = st.session_state.conversation
model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)

with st.sidebar:
    st.title(" Agente de Estudos")
    st.caption(f"Modelo local: `{model}`")
    if st.button("＋ Nova conversa", use_container_width=True):
        st.session_state.conversation = new_conversation()
        st.rerun()
    if st.button("Limpar conversa", use_container_width=True):
        clear_conversation(conversation)
        st.rerun()
    st.divider()
    st.caption("Histórico")
    for item in list_conversations():
        if st.button(item["title"], key=item["id"], use_container_width=True):
            loaded = load_conversation(item["id"])
            if loaded:
                st.session_state.conversation = loaded
                st.rerun()

st.title("Agente de Estudos")
st.caption("Converse com seu assistente de estudos. Tudo permanece no seu computador.")

for message in conversation["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar nos seus estudos?"):
    conversation["messages"].append({"role": "user", "content": prompt})
    if conversation["title"] == "Nova conversa":
        conversation["title"] = prompt[:48] + ("…" if len(prompt) > 48 else "")
    save_conversation(conversation)
    with st.chat_message("user"):
        st.markdown(prompt)

    response_data: dict = {}
    answer = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            for chunk in stream_chat(conversation["messages"], model):
                answer += chunk.get("message", {}).get("content", "")
                if chunk.get("done"):
                    response_data = chunk
                placeholder.markdown(answer + "▌")
            placeholder.markdown(answer)
        except OllamaError as error:
            placeholder.error(str(error))
            log_usage({}, model=model, success=False)
        else:
            conversation["messages"].append({"role": "assistant", "content": answer})
            save_conversation(conversation)
            log_usage(response_data, model=model, success=True)
