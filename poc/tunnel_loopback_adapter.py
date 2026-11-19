"""Tunnel-container loopback TCP to fixed private Unix socket; no public listener or auth injection."""
import os,select,signal,socket,socketserver,threading,time
from pathlib import Path

SOCK=Path("/relay/mcp.sock")
BIND=("127.0.0.1",8765)
slots=threading.BoundedSemaphore(4)

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as upstream:
                upstream.settimeout(4)
                upstream.connect(str(SOCK))
                client=self.request
                client.settimeout(5)
                upstream.settimeout(5)
                peer={client:upstream,upstream:client}
                live=set(peer)
                totals={client:0,upstream:0}
                caps={client:262144,upstream:1048576}
                deadline=time.monotonic()+30
                while live:
                    remaining=deadline-time.monotonic()
                    if remaining<=0:return
                    readable,_,_=select.select(list(live),[],[],min(remaining,5))
                    for src in readable:
                        data=src.recv(16384)
                        dst=peer[src]
                        if not data:
                            live.remove(src)
                            try:dst.shutdown(socket.SHUT_WR)
                            except OSError:pass
                            continue
                        totals[src]+=len(data)
                        if totals[src]>caps[src]:return
                        dst.sendall(data)
        except (OSError,ValueError):
            return

class Relay(socketserver.ThreadingMixIn,socketserver.TCPServer):
    daemon_threads=True
    allow_reuse_address=True
    request_queue_size=8
    def process_request(self,request,address):
        if not slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:super().process_request(request,address)
        except BaseException:
            slots.release()
            raise
    def process_request_thread(self,request,address):
        try:super().process_request_thread(request,address)
        finally:slots.release()

def terminate(*_):raise SystemExit(0)

def main():
    os.umask(0o077)
    if not SOCK.is_socket():raise RuntimeError("Private relay socket missing")
    signal.signal(signal.SIGTERM,terminate)
    signal.signal(signal.SIGINT,terminate)
    with Relay(BIND,Handler) as server:
        print("TUNNEL_LOOPBACK_READY",flush=True)
        server.serve_forever(poll_interval=.25)

if __name__=="__main__":main()
