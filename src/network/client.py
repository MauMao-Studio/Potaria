"""
Potaria - LAN Client Network Handler
Connects to LAN host server, sends player updates, receives synchronized players & world,
and renders remote potato party members.
Developer: Kurados
"""

import socket
import threading
import pygame
from src.constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT
)
from src.network.protocol import (
    PKT_JOIN, PKT_WELCOME, PKT_PLAYER_UPDATE, PKT_SYNC_PLAYERS,
    PKT_BLOCK_DELTA, PKT_COMBAT_EVENT, PKT_CHAT, PKT_DISCONNECT,
    PKT_SYNC_MOBS, PKT_MOB_DAMAGE,
    encode_packet, decode_packets
)

class LANClient:
    def __init__(self):
        self.connected = False
        self.sock = None
        self.player_id = None
        self.world_seed = None
        
        self.remote_players = {}  # pid -> dict of player info
        self.smoothed_positions = {} # pid -> Vector2 smoothed world position
        self.chat_messages = []   # list of (sender, text)
        self.pending_block_deltas = []
        self.lock = threading.Lock()
        self.latest_mob_sync = None
        self.pending_mob_damages = []

        pygame.font.init()
        self.name_font = pygame.font.SysFont("Arial", 11, bold=True)

    def connect(self, host_ip, port=25565, player_name="Spud"):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host_ip, port))
            self.connected = True

            # Wait for welcome packet
            raw = self.sock.recv(2048)
            packets, _ = decode_packets(raw)
            for pkt in packets:
                if pkt.get("type") == PKT_WELCOME:
                    data = pkt.get("data", {})
                    self.player_id = data.get("player_id", 2)
                    self.world_seed = data.get("seed", 12345)
                    print(f"[LANClient] Connected as Player {self.player_id} with World Seed: {self.world_seed}")
                    join_pkt = encode_packet(PKT_JOIN, {"name": player_name})
                    self.sock.sendall(join_pkt)
                    break

            # Start receiver thread
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()
            return True, self.world_seed

        except Exception as e:
            print(f"[LANClient] Connection failed: {e}")
            self.connected = False
            return False, None

    def _recv_loop(self):
        buffer = b""
        while self.connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data
                packets, buffer = decode_packets(buffer)

                for pkt in packets:
                    ptype = pkt.get("type")
                    pdata = pkt.get("data", {})

                    if ptype == PKT_SYNC_PLAYERS:
                        # Update all players, excluding ourselves
                        all_p = pdata.get("players", {})
                        current_remote_ids = {int(k) for k in all_p.keys() if int(k) != self.player_id}
                        for stale_id in list(self.remote_players.keys()):
                            if stale_id not in current_remote_ids:
                                del self.remote_players[stale_id]
                        for pid_str, pinfo in all_p.items():
                            pid = int(pid_str)
                            if pid != self.player_id:
                                self.remote_players[pid] = pinfo

                    elif ptype == PKT_BLOCK_DELTA:
                        self.pending_block_deltas.append(pdata)

                    elif ptype == PKT_CHAT:
                        self.chat_messages.append((pdata.get("name", "Player"), pdata.get("text", "")))
                        if len(self.chat_messages) > 15:
                            self.chat_messages.pop(0)

                    elif ptype == PKT_DISCONNECT:
                        pid = pdata.get("player_id")
                        if pid in self.remote_players:
                            del self.remote_players[pid]

                    elif ptype == PKT_SYNC_MOBS:
                        with self.lock:
                            self.latest_mob_sync = pdata

                    elif ptype == PKT_MOB_DAMAGE:
                        with self.lock:
                            self.pending_mob_damages.append(pdata)

            except Exception:
                break
        self.connected = False

    def send_player_update(self, x, y, vx, vy, hp, max_hp, level, facing, anim, held_item):
        if not self.connected:
            return
        pkt = encode_packet(PKT_PLAYER_UPDATE, {
            "x": x, "y": y, "vx": vx, "vy": vy,
            "hp": hp, "max_hp": max_hp, "level": level,
            "facing": facing, "anim": anim, "held_item": held_item
        })
        try:
            self.sock.sendall(pkt)
        except Exception:
            self.connected = False

    def send_block_delta(self, tx, ty, tile_id):
        if not self.connected:
            return
        pkt = encode_packet(PKT_BLOCK_DELTA, {"tx": tx, "ty": ty, "tile_id": tile_id})
        try:
            self.sock.sendall(pkt)
        except Exception:
            self.connected = False

    def send_chat(self, name, text):
        if not self.connected:
            return
        pkt = encode_packet(PKT_CHAT, {"name": name, "text": text})
        try:
            self.sock.sendall(pkt)
        except Exception:
            self.connected = False

    def send_mob_damage(self, mob_id, damage, knockback_vx=0.0, knockback_vy=-2.0, is_crit=False):
        """Sends client-inflicted damage to a mob or boss to authoritative server."""
        if not self.connected:
            return
        pkt = encode_packet(PKT_MOB_DAMAGE, {
            "mob_id": mob_id,
            "damage": damage,
            "knockback_vx": knockback_vx,
            "knockback_vy": knockback_vy,
            "is_crit": is_crit
        })
        try:
            self.sock.sendall(pkt)
        except Exception:
            self.connected = False

    def send_sync_mobs(self, mobs_data, boss_data=None, sky_time=None, enemy_projectiles=None, dropped_items=None):
        """Called by Host client to upload authoritative mobs list to server."""
        if not self.connected:
            return
        pkt = encode_packet(PKT_SYNC_MOBS, {
            "mobs": mobs_data,
            "boss": boss_data,
            "sky_time": sky_time,
            "enemy_projectiles": enemy_projectiles or [],
            "dropped_items": dropped_items or [],
        })
        try:
            self.sock.sendall(pkt)
        except Exception:
            self.connected = False

    def get_latest_mob_sync(self):
        """Retrieves and consumes the latest mob state snapshot from host."""
        with self.lock:
            sync = self.latest_mob_sync
            self.latest_mob_sync = None
            return sync

    def get_pending_mob_damages(self):
        """Retrieves and consumes pending mob damage events."""
        with self.lock:
            damages = list(self.pending_mob_damages)
            self.pending_mob_damages.clear()
            return damages

    def render_remote_players(self, target_surf, camera, asset_factory):
        """Draws other connected potato players in the world with sub-pixel lerp smoothing and 12 FPS animations."""
        for pid, p in self.remote_players.items():
            tx = p.get("x", 0.0)
            ty = p.get("y", 0.0)
            target_vec = pygame.math.Vector2(tx, ty)
            
            # Smooth position with Vector2.lerp (60 FPS smooth interpolation)
            if pid not in self.smoothed_positions:
                self.smoothed_positions[pid] = pygame.math.Vector2(tx, ty)
            else:
                self.smoothed_positions[pid] = self.smoothed_positions[pid].lerp(target_vec, 0.28)

            pos = self.smoothed_positions[pid]
            px, py = pos.x, pos.y
            facing = p.get("facing", True)
            name = p.get("name", f"Player {pid}")
            level = p.get("level", 1)
            vx = p.get("vx", 0.0)

            sx, sy = camera.world_to_screen(px, py)
            sprout_offset_y = PLAYER_SPRITE_HEIGHT - PLAYER_HEIGHT
            draw_sy = sy - sprout_offset_y
            
            # 12 FPS Animation selection (8-frame walk vs 6-frame idle)
            ticks = pygame.time.get_ticks()
            if abs(vx) > 0.2:
                walk_frames = asset_factory.player_sprites.get("walk", [asset_factory.player_sprites["idle"]])
                frame_idx = int(ticks / 83.33) % len(walk_frames)
                sprite = walk_frames[frame_idx]
            else:
                idle_frames = asset_factory.player_sprites.get("idle_frames", [asset_factory.player_sprites["idle"]])
                frame_idx = int(ticks / 83.33) % len(idle_frames)
                sprite = idle_frames[frame_idx]

            scaled_sprite = pygame.transform.scale(sprite, (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT))
            if not facing:
                scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
            target_surf.blit(scaled_sprite, (sx, draw_sy))

            # Draw Remote Player Name Tag & Level
            tag_text = f"{name} (Lv.{level})"
            tag_surf = self.name_font.render(tag_text, True, (255, 230, 100))
            bg_rect = pygame.Rect(sx + PLAYER_WIDTH // 2 - tag_surf.get_width() // 2 - 2, draw_sy - 14, tag_surf.get_width() + 4, 13)
            pygame.draw.rect(target_surf, (0, 0, 0, 180), bg_rect, border_radius=3)
            target_surf.blit(tag_surf, (sx + PLAYER_WIDTH // 2 - tag_surf.get_width() // 2, draw_sy - 14))

    def disconnect(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
