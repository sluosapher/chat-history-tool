import sys
import asyncio
import json
import os


async def get_chat_history(session_id: int) -> dict:
    """Retrieve chat history for a given session ID."""
    from urllib import request, parse, error

    base_url = os.getenv("CHAT_HISTORY_BASE_URL", "http://127.0.0.1:6225")
    url = f"{base_url}/chat-history?sid={parse.quote(str(session_id))}"

    # Debug: show the URL being fetched
    print(f"Fetching chat history from URL: {url}", file=sys.stderr)

    try:
        with request.urlopen(url, timeout=10) as resp:
            status = resp.status
            body = resp.read()

        if status < 200 or status >= 300:
            text = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {status}: {text}")

        sessions = json.loads(body.decode("utf-8"))

        if not sessions:
            raise RuntimeError(f"No session found for id {session_id}")

        return {"session_id": session_id, "sessions": sessions}
    except error.URLError as e:
        raise RuntimeError(f"Error connecting to chat history service at {base_url}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error in get_chat_history: {str(e)}")

async def main(session_id: int) -> None:
    try:
        result = await get_chat_history(session_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"Error calling get_chat_history({session_id}): {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_get_chat_history_script.py <session_id:int>", file=sys.stderr)
        sys.exit(1)

    try:
        session_id_arg = int(sys.argv[1])
    except ValueError:
        print("session_id must be an integer", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main(session_id_arg))
