# customPSNotify

Send custom notifications to a jailbroken PS5 from any PC app — Python GUI, Electron, Node.js, or anything that can open a TCP socket.

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
| `python-gui/build_exe.bat` | Builds a standalone `PS5Notify.exe` |

---

## PS5 Payload — `customPSNotify.js`

### Setup

1. Copy `customPSNotify.js` to wherever your jailbreak loads payloads from (e.g. `/data/ps5_autoloader/`).
2. Load it. You should see a toast: **"customPSNotify ready — Port 6969"**
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

## Python GUI — `notify_gui.py`

Full-featured desktop GUI. No external dependencies — stdlib only (`tkinter`, `socket`, `json`, `threading`).

### Run directly

```bash
python notify_gui.py
```

### CLI mode (no window)

```bash
python notify_gui.py 192.168.1.100 "Build finished" "v2.3.1 deployed"
```

### Build a standalone .exe (Windows)

Run `python-gui/build_exe.bat` — produces `python-gui/dist/PS5Notify.exe`. No Python install required on the target machine.

```
python-gui/
├── notify_gui.py
├── build_exe.bat
└── dist/
    └── PS5Notify.exe   <- output
```

---

## Node.js / Electron — `notifyClient.js`

No npm dependencies — uses Node built-in `net` module.

### API

```js
const ps5 = require('./notifyClient');

// Simple
await ps5.notify('192.168.1.100', 'Build succeeded!');

// With options
await ps5.notify('192.168.1.100', 'Deploy complete', {
  subMessage: 'v2.1.0 is live',
  port: 6969,
  timeout: 5000,
});
```

### CLI

```bash
node notifyClient.js 192.168.1.100 "Hello PS5" "Sub text"
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Connection refused` | Payload not running, or `bind()`/`listen()` failed | Reload the payload; check PS5 debug log for `bind() failed (errno N)` |
| `Timed out` | `pf` firewall still active | Check debug log for `pf open errno` — your jailbreak may need to disable pf before loading |
| `Invalid or unexpected token` | File saved with UTF-8 BOM | Re-save `customPSNotify.js` as UTF-8 **without BOM** |
| Toast shows but text is wrong | JSON not terminated with `\n` | Ensure your client appends `\n` to the JSON string |

---

## License

MIT