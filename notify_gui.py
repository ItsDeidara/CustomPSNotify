#!/usr/bin/env python3
"""
notify_gui.py  —  Python / Tkinter client for customPSNotify
──────────────────────────────────────────────────────────────
Connects to the customNotify.js payload running on your PS5 and sends
a custom notification.

The PS5 payload is a persistent TCP server (port 9999 by default).
Load it once via your jailbreak — it keeps listening forever.
Then use this GUI (or any other app) to push notifications to your PS5.

Requirements:  Python 3.7+  (stdlib only — tkinter, socket, json, threading)

Run
───
  python notify_gui.py

CLI (no GUI)
────────────
  python notify_gui.py 192.168.1.100 "Your message" "Sub text"
"""

import json
import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

DEFAULT_PORT    = 6969
DEFAULT_TIMEOUT = 5.0   # seconds


# ─── Send helper ─────────────────────────────────────────────────────────────

def send_notification(ps5_ip: str, message: str, sub_message: str = "",
                      port: int = DEFAULT_PORT,
                      timeout: float = DEFAULT_TIMEOUT) -> dict:
    """
    Connect to the customNotify.js TCP listener on the PS5 and push a notification.
    Returns the parsed ACK dict from the PS5 (e.g. {"ok": true}).
    Raises on connection error.
    """
    payload = json.dumps({"message": message, "subMessage": sub_message}) + "\n"

    with socket.create_connection((ps5_ip, port), timeout=timeout) as sock:
        sock.sendall(payload.encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)   # signal end-of-send; wait for ACK

        ack = b""
        while True:
            chunk = sock.recv(256)
            if not chunk:
                break
            ack += chunk

    try:
        return json.loads(ack.decode("utf-8").strip())
    except Exception:
        return {"ok": True}


# ─── GUI ─────────────────────────────────────────────────────────────────────

class NotifyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PS5 Custom Notify")
        self.resizable(True, True)
        self.minsize(520, 480)
        self._build_ui()

    def _build_ui(self):
        pad = dict(padx=12, pady=5)
        self.columnconfigure(1, weight=1)
        row = 0

        # ── Connection ────────────────────────────────────────────────────────
        ttk.Label(self, text="PS5 IP / Host:").grid(row=row, column=0, sticky="e", **pad)
        self.var_ip = tk.StringVar(value="192.168.1.100")
        ttk.Entry(self, textvariable=self.var_ip, width=22).grid(
            row=row, column=1, sticky="w", **pad)
        row += 1

        ttk.Label(self, text="Port:").grid(row=row, column=0, sticky="e", **pad)
        self.var_port = tk.StringVar(value=str(DEFAULT_PORT))
        ttk.Entry(self, textvariable=self.var_port, width=8).grid(
            row=row, column=1, sticky="w", **pad)
        row += 1

        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1

        # ── Message ───────────────────────────────────────────────────────────
        ttk.Label(self, text="Message:").grid(row=row, column=0, sticky="ne", **pad)
        self.txt_msg = tk.Text(self, height=4, wrap="word")
        self.txt_msg.insert("1.0", "Hello from Python!")
        self.txt_msg.grid(row=row, column=1, sticky="ew", **pad)
        row += 1

        ttk.Label(self, text="Sub-message:").grid(row=row, column=0, sticky="e", **pad)
        self.var_sub = tk.StringVar(value="Status update")
        ttk.Entry(self, textvariable=self.var_sub).grid(
            row=row, column=1, sticky="ew", **pad)
        row += 1

        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1

        # ── Buttons ───────────────────────────────────────────────────────────
        bf = ttk.Frame(self)
        bf.grid(row=row, column=0, columnspan=2, pady=4)
        self.btn_send = ttk.Button(
            bf, text="Send Notification", command=self._on_send, width=20)
        self.btn_send.pack(side="left", padx=6)
        ttk.Button(bf, text="Clear Log", command=self._clear_log, width=10).pack(
            side="left", padx=6)
        row += 1

        # ── Log ───────────────────────────────────────────────────────────────
        ttk.Label(self, text="Log:").grid(row=row, column=0, sticky="nw", **pad)
        self.log_box = scrolledtext.ScrolledText(
            self, height=10, state="disabled",
            font=("Consolas", 9), bg="#1e1e2e", fg="#cdd6f4",
            insertbackground="white")
        self.log_box.grid(row=row, column=1, sticky="nsew", **pad)
        self.rowconfigure(row, weight=1)

        self.log_box.tag_config("ok",   foreground="#a6e3a1")
        self.log_box.tag_config("err",  foreground="#f38ba8")
        self.log_box.tag_config("info", foreground="#89dceb")

    def _on_send(self):
        ip  = self.var_ip.get().strip()
        msg = self.txt_msg.get("1.0", "end-1c").strip()
        sub = self.var_sub.get().strip()

        if not ip:
            self.log("PS5 IP is required.", "err"); return
        if not msg:
            self.log("Message cannot be empty.", "err"); return
        try:
            port = int(self.var_port.get())
        except ValueError:
            self.log("Port must be a number.", "err"); return

        self.btn_send.config(state="disabled")
        self.log(f"Connecting to {ip}:{port} ...", "info")

        def worker():
            try:
                result = send_notification(ip, msg, sub, port)
                self.log(f"Sent!  ACK: {result}", "ok")
                self.log(f"  Message    : {msg[:80]}", "ok")
                if sub:
                    self.log(f"  Sub-message: {sub[:80]}", "ok")
            except Exception as exc:
                self.log(f"Error: {exc}", "err")
            finally:
                self.after(0, lambda: self.btn_send.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def log(self, text: str, tag: str = "info"):
        def _write():
            self.log_box.config(state="normal")
            self.log_box.insert("end", text + "\n", tag)
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.after(0, _write)


# ─── CLI mode ─────────────────────────────────────────────────────────────────

def _cli():
    import sys
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python notify_gui.py <ps5-ip> \"Message\" [\"Sub text\"]")
        sys.exit(1)
    ps5_ip  = args[0]
    message = args[1]
    sub     = args[2] if len(args) > 2 else ""
    try:
        result = send_notification(ps5_ip, message, sub)
        print(f"Sent — {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        _cli()
    else:
        app = NotifyApp()
        app.mainloop()

