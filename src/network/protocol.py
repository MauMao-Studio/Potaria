"""
Potaria - LAN Cooperative Multiplayer Protocol
Defines packet types, schemas, and encoding/decoding for 1 to 5 player sessions.
Developer: Kurados
"""

import json

# Packet Type Constants
PKT_JOIN = "join"               # Client requests to join
PKT_WELCOME = "welcome"         # Server assigns player ID and sends initial world seed
PKT_PLAYER_UPDATE = "p_update"  # Client sends (x, y, vx, vy, facing, anim, held_item)
PKT_SYNC_PLAYERS = "sync_p"     # Server broadcasts all player positions & stats
PKT_BLOCK_DELTA = "block_delta" # Block broken or placed
PKT_COMBAT_EVENT = "combat_ev"  # Hit, damage number, boss phase
PKT_CHAT = "chat"               # Text chat message
PKT_DISCONNECT = "disconnect"   # Player leaves session
PKT_SYNC_MOBS = "sync_mobs"     # Authoritative mob states broadcast from host
PKT_MOB_DAMAGE = "mob_dmg"      # Client-inflicted mob damage sent to host

def encode_packet(pkt_type, data):
    """Encodes a packet into UTF-8 JSON bytes with newline delimiter."""
    payload = {"type": pkt_type, "data": data}
    return (json.dumps(payload) + "\n").encode("utf-8")

def decode_packets(raw_buffer):
    """
    Decodes all complete newline-delimited JSON packets from a buffer.
    Returns: (list_of_packets, remaining_unprocessed_buffer)
    """
    lines = raw_buffer.split(b"\n")
    packets = []
    # If the last element does not end with newline, it is incomplete
    incomplete = lines[-1]
    
    for line in lines[:-1]:
        if not line.strip():
            continue
        try:
            pkt = json.loads(line.decode("utf-8"))
            packets.append(pkt)
        except Exception as e:
            print(f"[Network] Packet decode warning: {e}")

    return packets, incomplete
