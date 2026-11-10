#!/usr/bin/env python3
"""Tiny Telegram helper for the Naukri job agent.

Token: first line of telegram.txt next to this script (or env TG_TOKEN).
Chat id: env TG_CHAT, or second line of telegram.txt, or discovered from the first private message.

  python3 tg.py send "text"                  send a message (Markdown off, plain text)
  python3 tg.py doc <file> "caption"         send a file
  python3 tg.py read                         print unconfirmed messages from the owner as JSON (does not confirm)
  python3 tg.py ack <update_id>              confirm everything up to and including update_id
  python3 tg.py wait <seconds>               long-poll up to N seconds for the next message, print it as JSON (or {})
  python3 tg.py chatid                       print the chat id found in pending updates
"""
import json, os, sys, time, urllib.request, urllib.parse, uuid, mimetypes

HERE = os.path.dirname(os.path.abspath(__file__))


def _cfg():
    lines = []
    p = os.path.join(HERE, "telegram.txt")
    if os.path.exists(p):
        lines = [l.strip() for l in open(p, encoding="utf-8") if l.strip()]
    token = os.environ.get("TG_TOKEN") or (lines[0] if lines else None)
    chat = os.environ.get("TG_CHAT") or (lines[1] if len(lines) > 1 else None)
    if not token:
        sys.exit("No Telegram token")
    return token, chat


TOKEN, CHAT = _cfg()
API = f"https://api.telegram.org/bot{TOKEN}/"


def call(method, params=None, timeout=60):
    data = urllib.parse.urlencode(params or {}).encode()
    with urllib.request.urlopen(API + method, data=data, timeout=timeout) as r:
        out = json.load(r)
    if not out.get("ok"):
        raise RuntimeError(out)
    return out["result"]


def updates(offset=None, wait=0):
    p = {"timeout": wait, "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        p["offset"] = offset
    return call("getUpdates", p, timeout=wait + 30)


def mine(us):
    res = []
    for u in us:
        m = u.get("message") or {}
        if m.get("chat", {}).get("type") != "private":
            continue
        if CHAT and str(m["chat"]["id"]) != str(CHAT):
            continue
        res.append({"update_id": u["update_id"], "chat_id": m["chat"]["id"], "date": m.get("date"),
                    "text": m.get("text", ""),
                    "reply_to": (m.get("reply_to_message") or {}).get("text", "")})
    return res


def chat_id():
    if CHAT:
        return CHAT
    ms = mine(updates())
    if not ms:
        sys.exit("No chat yet: press Start and send any message to your bot first")
    return ms[-1]["chat_id"]


def send(text):
    for i in range(0, len(text), 3900):
        call("sendMessage", {"chat_id": chat_id(), "text": text[i:i + 3900], "disable_web_page_preview": "true"})


def send_doc(path, caption=""):
    boundary = uuid.uuid4().hex
    fname = os.path.basename(path)
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    parts = []
    for k, v in (("chat_id", str(chat_id())), ("caption", caption[:1000])):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{fname}\"\r\n"
                 f"Content-Type: {ctype}\r\n\r\n".encode() + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(API + "sendDocument", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.load(r)
    if not out.get("ok"):
        raise RuntimeError(out)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "send":
        send(sys.argv[2])
    elif cmd == "doc":
        send_doc(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "read":
        print(json.dumps(mine(updates()), ensure_ascii=False, indent=1))
    elif cmd == "ack":
        updates(offset=int(sys.argv[2]) + 1)
    elif cmd == "wait":
        secs = int(sys.argv[2])
        before = {m["update_id"] for m in mine(updates())}
        end = time.time() + secs
        while time.time() < end:
            new = [m for m in mine(updates(wait=min(50, max(1, int(end - time.time()))))) if m["update_id"] not in before]
            if new:
                print(json.dumps(new[0], ensure_ascii=False))
                return
        print("{}")
    elif cmd == "chatid":
        print(chat_id())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
