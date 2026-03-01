# customPSNotify

Send custom notifications to a jailbroken PS5 from any PC app — Python GUI, Electron, Node.js, or anything that can open a TCP socket.

<img width="637" height="244" alt="image" src="https://github.com/user-attachments/assets/454aedcd-94a6-417c-a749-3a9beb6456c8" />


---

## How it works

```
Your PC                          PS5 (jailbroken)
─────────────────────────────    ────────────────────────────────────
Python GUI  ─┐                   customPSNotify.js  (JS payload)
Electron app ├──> TCP :6969 ───> ├─ disables pf firewall
Node script ─┘    JSON msg       ├─ bind/listen on 0.0.0.0:6969
                                 ├─ accept() -> parse JSON
                                 └─ send_notification() toast
```

1. Load `customPSNotify.js` on your PS5 once via your jailbreak's JS payload loader.
2. The payload disables the `pf` packet-filter firewall and starts a **persistent TCP listener on port 6969**.
3. From your PC, send a JSON message — the PS5 displays it as a native toast notification instantly.

---

## Requirements

- Jailbroken PS5 with a WebKit JS payload loader (e.g. [ps5-payload-dev](https://github.com/ps5-payload-dev/sdk))
- Your PC and PS5 on the same local network

---

## Files

| File | Purpose |
|---|---|
| `customPSNotify.js` | JS payload — runs **on the PS5** |
| `notifyClient.js` | Node.js / Electron client module |
| `python-gui/notify_gui.py` | Python Tkinter GUI client |

---

## PS5 Payload — `customPSNotify.js`

### Setup

1. Copy `customPSNotify.js` to wherever your jailbreak loads payloads from (e.g. `/data/ps5_autoloader/`).
2. Load it. You should see: **"customPSNotify ready — Port 6969"**
3. The payload keeps running in the background, waiting for connections.

### Configuration

Edit the top of `customPSNotify.js`:

```js
const LISTEN_PORT = 6969;  // change if needed
```

### Protocol

Send a UTF-8 JSON line over TCP, terminated with `\n`:

```json
{"message": "Hello PS5!", "subMessage": "optional second line"}
```

The payload responds with:

```json
{"ok": true}
```
---
