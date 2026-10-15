import os
import sys
import pygame

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.assets.asset_factory import AssetFactory
from src.ui.crafting import load_craftable_recipes
from scripts.build_cookbook_docs import SECTIONS

def export_culinary_sprites():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    af = AssetFactory()

    craftable_recipes = load_craftable_recipes()
    crafting_ids = {r["result"] for r in craftable_recipes}

    all_items = []
    for _, items, _ in SECTIONS:
        for it in items:
            if it not in all_items:
                all_items.append(it)

    print(f"Total unique cookbook items to export: {len(all_items)}")

    craftable_dir = os.path.join("assets", "craftable_items")
    items_dir = os.path.join("assets", "items")
    os.makedirs(craftable_dir, exist_ok=True)
    os.makedirs(items_dir, exist_ok=True)

    craftable_count = 0
    droppable_count = 0

    for item_id in all_items:
        surf = af.generate_item_icon(item_id)
        assert surf.get_size() == (24, 24), f"{item_id} size {surf.get_size()} != (24, 24)"
        assert surf.get_at((0, 23))[3] == 0, f"{item_id} bottom-left pixel (0, 23) has alpha > 0"

        # Check visibility
        vis = sum(1 for x in range(24) for y in range(24) if surf.get_at((x, y))[3] > 0)
        assert vis >= 50, f"{item_id} only has {vis} visible pixels (minimum 50 required)"

        if item_id in crafting_ids:
            target_path = os.path.join(craftable_dir, f"{item_id}.png")
            forbidden_path = os.path.join(items_dir, f"{item_id}.png")
            pygame.image.save(surf, target_path)
            if os.path.exists(forbidden_path):
                os.remove(forbidden_path)
            craftable_count += 1
        else:
            target_path = os.path.join(items_dir, f"{item_id}.png")
            forbidden_path = os.path.join(craftable_dir, f"{item_id}.png")
            pygame.image.save(surf, target_path)
            if os.path.exists(forbidden_path):
                os.remove(forbidden_path)
            droppable_count += 1

    print(f"Successfully exported {craftable_count} craftables to {craftable_dir}")
    print(f"Successfully exported {droppable_count} non-craftables to {items_dir}")

if __name__ == "__main__":
    export_culinary_sprites()
