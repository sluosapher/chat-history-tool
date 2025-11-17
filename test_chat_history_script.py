import sys
import asyncio
import json
import os


async def list_session_ids():
    """List all available chat session IDs."""
    from urllib import request, error

    base_url = os.getenv("CHAT_HISTORY_BASE_URL", "http://127.0.0.1:6225")
    url = f"{base_url}/chat-history"

    print(f"Fetching all session IDs from URL: {url}", file=sys.stderr)

    try:
        with request.urlopen(url, timeout=10) as resp:
            status = resp.status
            body = resp.read()

        if status < 200 or status >= 300:
            text = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {status}: {text}")

        data = json.loads(body.decode("utf-8"))

        session_ids = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, (int, str)):
                    session_ids.append(int(item))
                elif isinstance(item, dict):
                    sid = item.get("session_id") or item.get("id") or item.get("sid")
                    if sid is not None:
                        session_ids.append(int(sid))
        elif isinstance(data, dict):
            candidates = (
                data.get("session_ids")
                or data.get("sessions")
                or data.get("ids")
                or []
            )
            if isinstance(candidates, list):
                for item in candidates:
                    if isinstance(item, (int, str)):
                        session_ids.append(int(item))
                    elif isinstance(item, dict):
                        sid = (
                            item.get("session_id")
                            or item.get("id")
                            or item.get("sid")
                        )
                        if sid is not None:
                            session_ids.append(int(sid))

        result = {
            "raw_response": data,
            "session_ids": sorted(set(session_ids)),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except error.URLError as e:
        raise RuntimeError(
            f"Error connecting to chat history service at {base_url}: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Error in list_session_ids: {str(e)}")


async def get_chat_history(session_id: int) -> dict:
    """Retrieve chat history for a given session ID."""
    from urllib import request, parse, error

    base_url = os.getenv("CHAT_HISTORY_BASE_URL", "http://127.0.0.1:6225")
    url = f"{base_url}/chat-history?sid={parse.quote(str(session_id))}"

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
        raise RuntimeError(
            f"Error connecting to chat history service at {base_url}: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Error in get_chat_history: {str(e)}")


async def main(argv):
    if len(argv) == 0 or (len(argv) == 1 and argv[0] in ("-h", "--help")):
        print(
            "Usage:\n"
            "  python test_chat_history_script.py --list\n"
            "  python test_chat_history_script.py <session_id:int>",
            file=sys.stderr,
        )
        sys.exit(1)

    if argv[0] in ("--list", "-l") and len(argv) == 1:
        try:
            await list_session_ids()
        except Exception as exc:
            print(f"Error listing session IDs: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    if len(argv) != 1:
        print(
            "Invalid arguments. Use --list or a single <session_id:int>.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        session_id_arg = int(argv[0])
    except ValueError:
        print("session_id must be an integer", file=sys.stderr)
        sys.exit(1)

    try:
        result = await get_chat_history(session_id_arg)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(
            f"Error calling get_chat_history({session_id_arg}): {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

