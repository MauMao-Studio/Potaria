"""
Potaria - LAN Authoritative Server
Handles up to 5 concurrent LAN players on local Wi-Fi/Ethernet.
Synchronizes positions, world block modifications, party states, and chat.
Developer: Kurados
"""

import socket
import threading
import time
import select
from src.network.protocol import (
    PKT_JOIN, PKT_WELCOME, PKT_PLAYER_UPDATE, PKT_SYNC_PLAYERS,
    PKT_BLOCK_DELTA, PKT_COMBAT_EVENT, PKT_CHAT, PKT_DISCONNECT,
    PKT_SYNC_MOBS, PKT_MOB_DAMAGE,
    encode_packet, decode_packets
)

DEFAULT_PORT = 25565

class LANServer:
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT, max_players=5):
        self.host = host
        self.port = port
        self.max_players = max_players
        
        self.running = False
        self.server_sock = None
        self.clients = {}  # player_id -> socket
        self.players = {}  # player_id -> state_dict
        self.next_player_id = 1
        self.lock = threading.Lock()
        self.pending_mob_damages = []
        self.latest_mobs_sync = None

    def start(self, world_seed, host_is_client=False):
        self.world_seed = world_seed
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(self.max_players)
        self.running = True

        if not host_is_client:
            # Standalone server: Host is pre-registered as Player 1
            self.players[1] = {
                "name": "Host (Spud)",
                "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0,
                "hp": 100, "max_hp": 100, "level": 1,
                "facing": True, "anim": "idle", "held_item": "copper_shortsword"
            }
            self.next_player_id = 2
        else:
            # Game host connects via local client: first socket gets Player 1
            self.players = {}
            self.next_player_id = 1

        self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.accept_thread.start()

        self.sync_thread = threading.Thread(target=self._broadcast_sync_loop, daemon=True)
        self.sync_thread.start()
        print(f"[LANServer] Started on port {self.port}. Waiting for up to {self.max_players} players...")

    def _accept_loop(self):
        while self.running:
            try:
                sock, addr = self.server_sock.accept()
                with self.lock:
                    if len(self.clients) >= self.max_players - 1:
                        sock.close()
                        continue
                    
                    pid = self.next_player_id
                    self.next_player_id += 1
                    self.clients[pid] = sock
                    self.players[pid] = {
                        "name": f"Potato_{pid}",
                        "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0,
                        "hp": 100, "max_hp": 100, "level": 1,
                        "facing": True, "anim": "idle", "held_item": "copper_shortsword"
                    }

                print(f"[LANServer] Player {pid} connected from {addr}!")
                # Send welcome packet with assigned ID and seed
                welcome_pkt = encode_packet(PKT_WELCOME, {"player_id": pid, "seed": self.world_seed})
                sock.sendall(welcome_pkt)

                # Client worker thread
                t = threading.Thread(target=self._client_handler, args=(pid, sock), daemon=True)
                t.start()

            except Exception:
                break

    def _client_handler(self, player_id, sock):
        buffer = b""
        while self.running:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                packets, buffer = decode_packets(buffer)

                for pkt in packets:
                    ptype = pkt.get("type")
                    pdata = pkt.get("data", {})

                    if ptype == PKT_JOIN:
                        with self.lock:
                            if player_id in self.players:
                                self.players[player_id]["name"] = pdata.get("name", f"Potato_{player_id}")

                    elif ptype == PKT_PLAYER_UPDATE:
                        with self.lock:
                            if player_id in self.players:
                                self.players[player_id].update(pdata)

                    elif ptype == PKT_BLOCK_DELTA:
                        # Broadcast block modification to everyone
                        self.broadcast(PKT_BLOCK_DELTA, pdata, exclude_pid=player_id)

                    elif ptype == PKT_CHAT:
                        # Broadcast chat message
                        self.broadcast(PKT_CHAT, pdata)

                    elif ptype == PKT_SYNC_MOBS:
                        with self.lock:
                            self.latest_mobs_sync = pdata
                        self.broadcast(PKT_SYNC_MOBS, pdata, exclude_pid=player_id)

                    elif ptype == PKT_MOB_DAMAGE:
                        with self.lock:
                            self.pending_mob_damages.append(pdata)

            except Exception:
                break

        # Disconnect handling
        with self.lock:
            if player_id in self.clients:
                del self.clients[player_id]
            if player_id in self.players:
                del self.players[player_id]
        print(f"[LANServer] Player {player_id} disconnected.")
        self.broadcast(PKT_DISCONNECT, {"player_id": player_id})

    def _broadcast_sync_loop(self):
        """Broadcasts player states to all clients at 20 Hz (every 50ms)."""
        while self.running:
            time.sleep(0.05)
            with self.lock:
                if not self.clients:
                    continue
                sync_pkt = encode_packet(PKT_SYNC_PLAYERS, {"players": self.players})

            for sock in list(self.clients.values()):
                try:
                    sock.sendall(sync_pkt)
                except Exception:
                    pass

    def update_host_player(self, x, y, vx, vy, hp, max_hp, level, facing, anim, held_item):
        """Called by Host client to update Player 1 state."""
        with self.lock:
            if 1 in self.players:
                self.players[1].update({
                    "x": x, "y": y, "vx": vx, "vy": vy,
                    "hp": hp, "max_hp": max_hp, "level": level,
                    "facing": facing, "anim": anim, "held_item": held_item
                })

    def broadcast(self, pkt_type, data, exclude_pid=None):
        """Sends packet to all connected client sockets."""
        pkt_bytes = encode_packet(pkt_type, data)
        with self.lock:
            for pid, sock in self.clients.items():
                if pid != exclude_pid:
                    try:
                        sock.sendall(pkt_bytes)
                    except Exception:
                        pass

    def broadcast_mobs(self, mobs_data, boss_data=None, sky_time=None, enemy_projectiles=None, dropped_items=None):
        """Sends authoritative mobs and boss state to all connected clients."""
        pdata = {
            "mobs": mobs_data,
            "boss": boss_data,
            "sky_time": sky_time,
            "enemy_projectiles": enemy_projectiles or [],
            "dropped_items": dropped_items or [],
        }
        with self.lock:
            self.latest_mobs_sync = pdata
        self.broadcast(PKT_SYNC_MOBS, pdata)

    def get_pending_mob_damages(self):
        """Called by Host to retrieve and drain client-inflicted mob damage events."""
        with self.lock:
            damages = list(self.pending_mob_damages)
            self.pending_mob_damages.clear()
            return damages

    def stop(self):
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
