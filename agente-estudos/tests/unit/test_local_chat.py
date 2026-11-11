from unittest.mock import MagicMock, patch
import json
from app.local_chat import DEFAULT_NUM_CTX, stream_chat


def test_stream_chat_payload_includes_num_ctx():
    mock_response = MagicMock()
    mock_response.__enter__.return_value = [b'{"message": {"content": "ok"}, "done": true}\n']

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        chunks = list(stream_chat([{"role": "user", "content": "olá"}], model="llama3.2", num_ctx=8192))
        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "ok"

        # Check request payload sent
        sent_request = mock_urlopen.call_args[0][0]
        payload = json.loads(sent_request.data.decode("utf-8"))
        assert payload["model"] == "llama3.2"
        assert payload["options"]["num_ctx"] == 8192
