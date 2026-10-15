"""
Potaria - Craftable Storage Chest System
Provides 20-slot interactive storage containers with deposit, withdraw,
quick stacking, and world save/load persistence.
Developer: Kurados
"""

from src.ui.inventory import ItemStack, ITEM_REGISTRY, ITEM_ALIASES

CHEST_SLOTS = 20

class StorageChest:
    def __init__(self, tx, ty, capacity=CHEST_SLOTS, chest_type="chest", is_player_placed=False):
        self.tx = int(tx)
        self.ty = int(ty)
        self.capacity = int(capacity)
        self.chest_type = str(chest_type)
        self.is_player_placed = bool(is_player_placed)
        self.slots = [None] * self.capacity

    def is_empty(self):
        return all(s is None for s in self.slots)

    def get_all_items(self):
        """Returns list of all non-empty ItemStack objects."""
        return [s for s in self.slots if s is not None]

    def count_wood(self):
        """Returns total wood count across all wood variants."""
        from src.constants import WOOD_VARIANTS_SET
        total = 0
        for slot in self.slots:
            if slot:
                slot_canon = ITEM_ALIASES.get(slot.item_id, slot.item_id)
                if slot.item_id in WOOD_VARIANTS_SET or slot_canon in WOOD_VARIANTS_SET:
                    total += slot.count
        return total

    def count_item(self, item_id):
        canon = ITEM_ALIASES.get(item_id, item_id)
        if item_id in ("wood", "oak_wood") or canon in ("wood", "oak_wood"):
            return self.count_wood()
        total = 0
        for slot in self.slots:
            if slot:
                slot_canon = ITEM_ALIASES.get(slot.item_id, slot.item_id)
                if slot.item_id == item_id or slot.item_id == canon or slot_canon == canon:
                    total += slot.count
        return total

    def can_add_item(self, item_id, count=1):
        canon = ITEM_ALIASES.get(item_id, item_id)
        data = ITEM_REGISTRY.get(item_id) or ITEM_REGISTRY.get(canon, {})
        max_s = data.get("max_stack", 999)
        needed = count
        for slot in self.slots:
            if slot and (slot.item_id == item_id or slot.item_id == canon):
                space = max_s - slot.count
                if space > 0:
                    needed -= space
                    if needed <= 0:
                        return True
            elif slot is None:
                needed -= max_s
                if needed <= 0:
                    return True
        return needed <= 0

    def add_item(self, item_id, count=1, enhancement_level=0, is_broken=False, affix_slots=0, affixes=None, removed_stats=None, base_rolls=None, additional_affix_slots=0, tags=None):
        """Adds items into chest, stacking where applicable. Returns remaining count."""
        canon = ITEM_ALIASES.get(item_id, item_id)
        data = ITEM_REGISTRY.get(item_id) or ITEM_REGISTRY.get(canon, {})
        max_s = data.get("max_stack", 999)

        # 1. Stack into existing slots (only if non-equipment or identical modifiers)
        is_modified = enhancement_level > 0 or is_broken or affixes or removed_stats or base_rolls or additional_affix_slots > 0 or tags
        if max_s > 1 and not is_modified:
            for slot in self.slots:
                if slot and (slot.item_id == item_id or slot.item_id == canon) and slot.count < max_s:
                    if not (slot.enhancement_level > 0 or slot.is_broken or slot.affixes or slot.removed_stats or getattr(slot, "base_rolls", None) or getattr(slot, "additional_affix_slots", 0) > 0 or getattr(slot, "tags", None)):
                        space = max_s - slot.count
                        transfer = min(space, count)
                        slot.count += transfer
                        count -= transfer
                        if count <= 0:
                            return 0

        # 2. Place into empty slots
        for idx in range(self.capacity):
            if self.slots[idx] is None:
                transfer = min(max_s, count)
                st = ItemStack(
                    item_id,
                    transfer,
                    enhancement_level=enhancement_level,
                    is_broken=is_broken,
                    affix_slots=affix_slots,
                    affixes=list(affixes) if affixes else [],
                    removed_stats=list(removed_stats) if removed_stats else [],
                    base_rolls=dict(base_rolls) if base_rolls else None,
                    additional_affix_slots=additional_affix_slots,
                    tags=list(tags) if tags else None
                )
                self.slots[idx] = st
                count -= transfer
                if count <= 0:
                    return 0

        return count

    def add_stack(self, stack):
        """Adds an existing ItemStack into chest."""
        if not stack or stack.count <= 0:
            return None
        rem = self.add_item(
            stack.item_id,
            count=stack.count,
            enhancement_level=getattr(stack, "enhancement_level", 0),
            is_broken=getattr(stack, "is_broken", False),
            affix_slots=getattr(stack, "affix_slots", 0),
            affixes=getattr(stack, "affixes", []),
            removed_stats=getattr(stack, "removed_stats", []),
            base_rolls=getattr(stack, "base_rolls", None),
            additional_affix_slots=getattr(stack, "additional_affix_slots", 0),
            tags=getattr(stack, "tags", None),
        )
        if rem <= 0:
            return None
        stack.count = rem
        return stack

    def quick_stack_from_inventory(self, inventory):
        """Deposits items from player inventory that already exist in chest."""
        if not inventory:
            return 0
        deposited = 0
        chest_item_ids = {s.item_id for s in self.slots if s is not None}
        for idx, inv_slot in enumerate(inventory.slots):
            if inv_slot and inv_slot.item_id in chest_item_ids:
                prev_cnt = inv_slot.count
                rem = self.add_item(
                    inv_slot.item_id,
                    count=inv_slot.count,
                    enhancement_level=getattr(inv_slot, "enhancement_level", 0),
                    is_broken=getattr(inv_slot, "is_broken", False),
                    affix_slots=getattr(inv_slot, "affix_slots", 0),
                    affixes=getattr(inv_slot, "affixes", []),
                    removed_stats=getattr(inv_slot, "removed_stats", [])
                )
                transferred = prev_cnt - rem
                deposited += transferred
                if rem <= 0:
                    inventory.slots[idx] = None
                else:
                    inv_slot.count = rem
        return deposited

    def deposit_all_from_inventory(self, inventory):
        """Transfers as many items as possible from inventory into chest."""
        if not inventory:
            return 0
        deposited = 0
        for idx, inv_slot in enumerate(inventory.slots):
            if inv_slot:
                prev_cnt = inv_slot.count
                rem = self.add_item(
                    inv_slot.item_id,
                    count=inv_slot.count,
                    enhancement_level=getattr(inv_slot, "enhancement_level", 0),
                    is_broken=getattr(inv_slot, "is_broken", False),
                    affix_slots=getattr(inv_slot, "affix_slots", 0),
                    affixes=getattr(inv_slot, "affixes", []),
                    removed_stats=getattr(inv_slot, "removed_stats", [])
                )
                transferred = prev_cnt - rem
                deposited += transferred
                if rem <= 0:
                    inventory.slots[idx] = None
                else:
                    inv_slot.count = rem
        return deposited

    def take_all_to_inventory(self, inventory):
        """Transfers all items from chest into player inventory, depositing from back to preserve hotbar."""
        if not inventory:
            return 0
        taken = 0
        for idx, c_slot in enumerate(self.slots):
            if c_slot:
                prev_cnt = c_slot.count
                rem = inventory.add_item(c_slot, from_back=True)
                transferred = prev_cnt - rem
                taken += transferred
                if rem <= 0:
                    self.slots[idx] = None
                else:
                    c_slot.count = rem
        return taken

    def to_dict(self):
        slots_data = []
        for idx, s in enumerate(self.slots):
            if s:
                slots_data.append({
                    "slot": idx,
                    "item_id": s.item_id,
                    "count": s.count,
                    "enhancement_level": getattr(s, "enhancement_level", 0),
                    "is_broken": getattr(s, "is_broken", False),
                    "affix_slots": getattr(s, "affix_slots", 0),
                    "affixes": getattr(s, "affixes", []),
                    "removed_stats": getattr(s, "removed_stats", []),
                    "base_rolls": getattr(s, "base_rolls", None),
                    "additional_affix_slots": getattr(s, "additional_affix_slots", 0),
                    "tags": getattr(s, "tags", None),
                })
        return {
            "tx": self.tx,
            "ty": self.ty,
            "capacity": self.capacity,
            "chest_type": self.chest_type,
            "is_player_placed": self.is_player_placed,
            "slots": slots_data
        }

    @classmethod
    def from_dict(cls, data):
        tx = data.get("tx", 0)
        ty = data.get("ty", 0)
        capacity = data.get("capacity", CHEST_SLOTS)
        ctype = data.get("chest_type", "chest")
        is_player = data.get("is_player_placed", True)
        chest = cls(tx, ty, capacity=capacity, chest_type=ctype, is_player_placed=is_player)
        for sdata in data.get("slots", []):
            idx = sdata.get("slot")
            if idx is not None and 0 <= idx < capacity:
                st = ItemStack(
                    sdata["item_id"],
                    sdata.get("count", 1),
                    enhancement_level=sdata.get("enhancement_level", 0),
                    is_broken=sdata.get("is_broken", False),
                    affix_slots=sdata.get("affix_slots", 0),
                    affixes=list(sdata.get("affixes", [])),
                    removed_stats=list(sdata.get("removed_stats", [])),
                    base_rolls=sdata.get("base_rolls"),
                    additional_affix_slots=sdata.get("additional_affix_slots", 0),
                    tags=sdata.get("tags")
                )
                chest.slots[idx] = st
        return chest

