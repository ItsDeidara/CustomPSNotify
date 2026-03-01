const LISTEN_PORT = 6969;

const SYSCALL = {
  read:       3n,
  write:      4n,
  open:       5n,
  close:      6n,
  ioctl:      54n,
  accept:     30n,
  socket:     97n,
  bind:       104n,
  setsockopt: 105n,
  listen:     106n,
};

function disablePF() {
  try {
    const DIOCSTOP = 0x20004477n;
    const O_RDWR = 2n;
    const fd = syscall(SYSCALL.open, alloc_string("/dev/pf"), O_RDWR, 0n);
    if (Number(fd) >= 0) {
      const r = syscall(SYSCALL.ioctl, fd, DIOCSTOP, 0n);
      syscall(SYSCALL.close, fd);
      log("pf ioctl ret: " + Number(r));
    } else {
      log("pf open errno: " + (-Number(fd)));
    }
  } catch (e) {
    log("pf error: " + e.message);
  }
}

function makeSockaddr(port) {
  const sa = malloc(16);
  for (let i = 0n; i < 16n; i++) write8(sa + i, 0n);
  write8(sa + 0n, 16n);                          
  write8(sa + 1n, 2n);                           
  write8(sa + 2n, BigInt((port >> 8) & 0xff));   
  write8(sa + 3n, BigInt(port & 0xff));          
  write32(sa + 4n, 0n);                          
  return sa;
}

function setSockOpt(fd, level, opt) {
  const val = malloc(4);
  write32(val, 1n);
  syscall(SYSCALL.setsockopt, fd, level, opt, val, 4n);
}

function readAll(fd) {
  const buf = malloc(2048);
  let out = "";
  while (true) {
    const n = Number(syscall(SYSCALL.read, fd, buf, 2048n));
    if (n <= 0) break;
    for (let i = 0; i < n; i++)
      out += String.fromCharCode(Number(read8(buf + BigInt(i))));
    if (out.indexOf("\n") !== -1) break;
  }
  return out.trim();
}

function writeStr(fd, s) {
  syscall(SYSCALL.write, fd, alloc_string(s), BigInt(s.length));
}

function handleClient(fd) {
  try {
    const raw = readAll(fd);
    log("recv: " + raw);
    let message = raw, subMessage = "";
    try {
      const p = JSON.parse(raw);
      if (p.message)    message    = String(p.message);
      if (p.subMessage) subMessage = String(p.subMessage);
    } catch (e2) {}
    send_notification(message + (subMessage ? "\n" + subMessage : ""));
    writeStr(fd, '{"ok":true}\n');
  } catch (e) {
    log("handleClient error: " + e.message);
    try { writeStr(fd, '{"ok":false}\n'); } catch (e3) {}
  }
  syscall(SYSCALL.close, fd);
}

function main() {
  log("customPSNotify starting");

  disablePF();

  
  const server = syscall(SYSCALL.socket, 2n, 1n, 0n);
  log("socket fd: " + Number(server));
  if (Number(server) < 0) {
    send_notification("socket() failed (errno " + (-Number(server)) + ")");
    return;
  }

  setSockOpt(server, 0xffffn, 0x4n);   
  setSockOpt(server, 0xffffn, 0x200n); 

  const sa = makeSockaddr(LISTEN_PORT);

  let ret = syscall(SYSCALL.bind, server, sa, 16n);
  log("bind ret: " + Number(ret));
  if (Number(ret) < 0) {
    send_notification("bind() failed (errno " + (-Number(ret)) + ")");
    syscall(SYSCALL.close, server);
    return;
  }

  ret = syscall(SYSCALL.listen, server, 8n);
  log("listen ret: " + Number(ret));
  if (Number(ret) < 0) {
    send_notification("listen() failed (errno " + (-Number(ret)) + ")");
    syscall(SYSCALL.close, server);
    return;
  }

  send_notification("customPSNotify ready\nPort " + LISTEN_PORT);
  log("Listening on 0.0.0.0:" + LISTEN_PORT);

  
  
  while (true) {
    const client = syscall(SYSCALL.accept, server, 0n, 0n);
    if (Number(client) < 0) {
      log("accept errno: " + (-Number(client)));
      continue;
    }
    log("client fd: " + Number(client));
    handleClient(client);
  }
}

main();