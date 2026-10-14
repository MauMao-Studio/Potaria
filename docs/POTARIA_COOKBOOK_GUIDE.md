# Potaria Culinary Master Catalog and Cooking Guide

## Overview
Cooking is a core survival and adventuring system in Potaria. Consuming prepared meals restores substantial health points (HP), enables high-tier sustain during boss encounters, and utilizes locally foraged, farmed, hunted, and fished ingredients. Recipes are crafted either in a cooking station (Furnace) or assembled directly by hand.

### Cooking Stations
* **Furnace (`station="furnace"`)**: The primary hearth station for simmering stews, frying fish, boiling broths, and baking bread. Requires charcoal or wood combustion.
* **By Hand (`station=None`)**: Direct crafting for cold desserts, fresh condiments, cured raw delicacies, and artisanal noodle kneading without thermal equipment.

---

## Authentic Filipino Cuisine
Signature traditional dishes featuring complex savory, sour, and aromatic flavor profiles.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Classic Chicken Adobo | `chicken_adobo` | 90 HP | Furnace | 1x Native Chicken Meat, 1x Toyo Soy Sauce, 1x Sukang Paombong Vinegar, 1x Bawang Garlic | Simmered native chicken in vinegar, soy sauce, garlic, and cracked pepper. Restores 90 HP. |
| Rich Pork Adobo | `pork_adobo` | 95 HP | Furnace | 1x Native Pork Cut, 1x Toyo Soy Sauce, 1x Sukang Paombong Vinegar, 1x Bawang Garlic | Tender pork cubes braised with garlic, bay leaves, and tangy soy vinegar sauce. Restores 95 HP. |
| Sinigang na Baboy | `sinigang` | 105 HP | Furnace | 1x Liempo Pork Belly, 1x Sampalok Tamarind, 1x Sibuyas Red Onion, 1x Talong Native Eggplant | Tamarind-sour savory soup with tender pork and crisp vegetables. Restores 105 HP. |
| Fiesta Kare-Kare | `kare_kare` | 115 HP | Furnace | 1x Bulalo Beef Shank, 1x Ground Peanut Butter, 1x Talong Native Eggplant, 1x Sitaw String Beans | Savory peanut stew with tender beef shank, eggplant, and string beans. Restores 115 HP. |
| Batangas Bulalo | `bulalo` | 120 HP | Furnace | 1x Bulalo Beef Shank, 1x Sibuyas Red Onion, 1x Paminta Peppercorns | Slow-simmered beef shank marrow soup with sweet corn and peppercorns. Restores 120 HP. |
| Tinolang Manok | `tinola` | 85 HP | Furnace | 1x Native Chicken Meat, 1x Luya Fresh Ginger, 1x Sibuyas Red Onion | Comforting native chicken soup infused with warming ginger and onions. Restores 85 HP. |
| Crispy Lechon Kawali | `lechon` | 110 HP | Furnace | 1x Liempo Pork Belly, 1x Bawang Garlic, 1x Sukang Paombong Vinegar | Deep-fried pork belly slab with blistering crackling skin and juicy meat. Restores 110 HP. |
| Pancit Guisado | `pancit_bihon` | 80 HP | Furnace | 1x Bihon Rice Noodles, 1x Native Pork Cut, 1x Bawang Garlic, 1x Sibuyas Red Onion | Stir-fried bihon noodles with savory meat slivers, garlic, and calamansi. Restores 80 HP. |
| Arroz Caldo with Egg | `arroz_caldo` | 75 HP | Furnace | 1x Native Chicken Meat, 1x Milagrosa White Rice, 1x Luya Fresh Ginger | Thick chicken and rice porridge topped with toasted garlic and boiled egg. Restores 75 HP. |
| Special Halo-Halo | `halo_halo` | 90 HP | By Hand | 1x Yelo Shaved Ice, 1x Sweet Condensed Milk, 1x Ube Halaya Jam | Towering shaved ice dessert with ube halaya, condensed milk, and sweet treats. Restores 90 HP. |
| Kalderetang Kambing | `kaldereta` | 110 HP | Furnace | 1x Native Goat Meat, 1x Sibuyas Red Onion, 1x Bawang Garlic, 1x Paminta Peppercorns | Hearty spiced stew of tender goat meat with tomatoes and sweet peppers. Restores 110 HP. |
| Balut with Rock Salt | `balut` | 65 HP | By Hand | 1x Itik Duck Egg, 1x Asin Sea Salt | Fertilized duck egg sipped hot with spiced vinegar and sea salt. Restores 65 HP. |
| Itlog na Maalat | `itlog_na_maalat` | 45 HP | By Hand | 1x Itik Duck Egg, 1x Asin Sea Salt | Cured red-dyed salted duck egg paired with fresh tomatoes. Restores 45 HP. |
| Garlic Sinangag Rice | `sinangag` | 50 HP | Furnace | 1x Milagrosa White Rice, 1x Bawang Garlic | Wok-fried rice tossed with golden toasted garlic and sea salt. Restores 50 HP. |
| Daing na Bangus | `daing_na_bangus` | 75 HP | Furnace | 1x Bangus, 1x Bawang Garlic, 1x Sukang Paombong Vinegar | Marinated split milkfish in garlic vinegar, fried to a golden crisp. Restores 75 HP. |
| Sinigang na Bangus | `sinigang_na_bangus` | 100 HP | Furnace | 1x Bangus, 1x Sampalok Tamarind, 1x Sibuyas Red Onion, 1x Talong Native Eggplant | Tamarind-sour soup with tender milkfish belly, eggplant, and onions. Restores 100 HP. |
| Ginataang Tilapia | `ginataang_tilapia` | 105 HP | Furnace | 1x Tilapia, 1x Gata Coconut Milk, 1x Luya Fresh Ginger | Fresh tilapia simmered in rich creamy coconut milk with ginger and spices. Restores 105 HP. |
| Kinilaw na Tanigue | `kinilaw_na_tanigue` | 110 HP | By Hand | 1x Tanigue, 1x Sukang Paombong Vinegar, 1x Calamansi Citrus, 1x Luya Fresh Ginger | Fresh Spanish mackerel cured in native vinegar, calamansi juice, ginger, and chili. Restores 110 HP and +15% Speed. |

---

## Fried, Smoked, and Steamed Fish
Fresh marine and freshwater catches cooked over embers to maximize healing value.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Inihaw na Bangus | `cooked_bangus` | 65 HP | Furnace | 1x Bangus | Charcoal-grilled milkfish stuffed with tomatoes and onions. Restores 65 HP. |
| Pritong Tilapia | `cooked_tilapia` | 50 HP | Furnace | 1x Tilapia | Crispy fried whole tilapia seasoned with sea salt. Restores 50 HP. |
| Pritong Galunggong | `cooked_galunggong` | 45 HP | Furnace | 1x Galunggong | Deep-fried round scad paired with spicy vinegar dipping. Restores 45 HP. |
| Sinigang na Maya-Maya | `cooked_maya_maya` | 80 HP | Furnace | 1x Maya-Maya | Tamarind-sour savory soup with red snapper. Restores 80 HP. |
| Kinilaw na Tanigue | `cooked_tanigue` | 90 HP | Furnace | 1x Tanigue | Citrus and coconut vinegar cured Spanish mackerel ceviche. Restores 90 HP. |
| Inihaw na Tambakol | `cooked_tambakol` | 85 HP | Furnace | 1x Tambakol | Flame-broiled yellowfin steaks basted in sweet soy glaze. Restores 85 HP. |
| Pasingaw na Lapu-Lapu | `cooked_lapu_lapu` | 110 HP | Furnace | 1x Lapu-Lapu | Ginger-steamed grouper dressed in sesame soy sauce. Restores 110 HP. |
| Adobong Hito | `cooked_hito` | 70 HP | Furnace | 1x Hito | Catfish simmered in garlic, vinegar, and black peppercorns. Restores 70 HP. |
| Pritong Dilis | `cooked_dilis` | 35 HP | Furnace | 1x Dilis | Glazed crunchy sweet-and-spicy dried anchovies. Restores 35 HP. |
| Pritong Dalagang Bukid | `cooked_dalagang_bukid` | 60 HP | Furnace | 1x Dalagang Bukid | Crispy pan-fried yellowtail fusilier with golden crust. Restores 60 HP. |

---

## Potato Specialities and Delicacies
Artisanal root-based dishes, energy-dense pastries, and restorative tuber salves.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Mashed Potato Meal | `mashed_potato` | 60 HP | Furnace | 2x Raw Potato, 1x Wood | Cooked at a furnace. Hearty creamy meal that restores +60 HP. |
| Golden French Fry | `golden_fry` | 100 HP | Furnace | 3x Raw Potato, 1x Gold Bar | Crispy golden fry seasoned with gold dust. Restores +100 HP. |
| Hearty Root Stew | `hearty_root_stew` | 60 HP | Furnace | 3x Raw Potato, 1x Glowing Mushroom, 1x Wood | Simmering rustic stew of cubed potatoes, glowing mushrooms, and savory wild herbs. Restores 60 Health. |
| Glazed Golden Tuber | `glazed_golden_tuber` | 100 HP | Furnace | 2x Raw Potato, 2x Gold Bar | Heirloom russet potato roasted in molten gold and clover nectar. Restores 100 Health and 30 Mana. |
| Smoked Spud Jerky | `smoked_spud_jerky` | 30 HP | Furnace | 2x Raw Potato, 1x Wood | Hickory-cured salted potato jerky crisps that provide quick sustenance during expeditions. |
| Gilded Russet | `gilded_russet` | 140 HP | Furnace | 3x Raw Potato, 3x Gold Bar | Supreme confection of candied royal root providing massive vitality recovery. |
| Oven-Baked Potato Loaf | `potato_bread` | 45 HP | Furnace | 3x Raw Potato, 1x Wood | Warm crusty hearth bread baked from wholesome potato flour. Restores 45 Health. |
| Sweet Tuber Pie | `sweet_tuber_pie` | 70 HP | Furnace | 2x Raw Potato, 2x Spud Sap, 1x Wood | Caramelized tuber pie baked to golden perfection with sweet forest sap. Restores 70 Health. |
| Herbal Salve | `herbal_salve` | 35 HP | By Hand | 1x Raw Potato, 1x Spud Sap | Quick-acting botanical poultice ground from mashed spud pulp and soothing sap. Restores 35 Health. |

---

## Fresh Catches (Raw Fishes)
Wild aquatic species caught with fishing rods across diverse biomes.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Bangus | `raw_bangus` | 15 HP | N/A (Harvested) | Caught with fishing rod in brackish estuaries and calm lagoons. | National silvery fish of Potaria, prized for its tender belly. Best cooked before eating. |
| Tilapia | `raw_tilapia` | 12 HP | N/A (Harvested) | Caught in freshwater rivers, inland lakes, and ponds. | Freshwater cichlid with hardy scales, thriving in inland streams. Cook over fire. |
| Galunggong | `raw_galunggong` | 10 HP | N/A (Harvested) | Caught in open sea waters and ocean shores. | Round scad, the beloved everyday staple fish with rich flavor. |
| Maya-Maya | `raw_maya_maya` | 20 HP | N/A (Harvested) | Caught around deep offshore coral drop-offs. | Vibrant red snapper found patrolling deep rocky reefs. |
| Tanigue | `raw_tanigue` | 25 HP | N/A (Harvested) | Prized game fish hooked in open ocean waters using advanced rods. | Sleek Spanish mackerel with firm, prized steaks. |
| Tambakol | `raw_tambakol` | 22 HP | N/A (Harvested) | Hooked in deep ocean currents with sturdy fishing tackle. | Yellowfin tuna relative with deep crimson flesh and powerful fins. |
| Lapu-Lapu | `raw_lapu_lapu` | 28 HP | N/A (Harvested) | Rare catch landed around rocky sea caves and deep ocean reefs. | Esteemed spotted reef grouper named after the brave chieftain warrior. |
| Hito | `raw_hito` | 16 HP | N/A (Harvested) | Hooked in muddy swamps, marshy pools, and murky riverbeds. | Whiskered freshwater catfish dwelling in muddy bottoms and waterways. |
| Dilis | `raw_dilis` | 8 HP | N/A (Harvested) | Netted or caught with light tackle along shallow coastal shores. | Tiny anchovies swimming in shimmering schools along shores. |
| Dalagang Bukid | `raw_dalagang_bukid` | 15 HP | N/A (Harvested) | Vibrant reef fish hooked near sunlit coral gardens. | Yellowtail fusilier with radiant crimson-gold scales. |

---

## Livestock, Poultry, and Dairy
Nutrient-rich animal cuts and farm goods harvested from native wildlife.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Native Chicken Meat | `raw_chicken` | 16 HP | N/A (Harvested) | Obtained from native free-range poultry in grassy meadows. | Fresh native poultry cut. Lean and flavorful, best stewed in adobo or tinola. |
| Native Pork Cut | `raw_pork` | 20 HP | N/A (Harvested) | Obtained from native wild boars and domesticated pigs. | Succulent cut of native black pig. Essential for classic pork adobo and sinigang. |
| Liempo Pork Belly | `pork_belly` | 25 HP | N/A (Harvested) | Choice cut harvested from prime livestock or rural butchers. | Layered fatty pork belly slab, prime cut for crispy lechon kawali. |
| Bulalo Beef Shank | `raw_beef` | 28 HP | N/A (Harvested) | Harvested from pastoral cattle in highland pasturelands. | Meaty beef shank bone with rich marrow center from native carabao. |
| Native Goat Meat | `raw_goat_meat` | 24 HP | N/A (Harvested) | Sourced from agile mountain goats navigating cliffside crags. | Lean, aromatic goat meat cut, traditional centerpiece for Kaldereta. |
| Itik Duck Egg | `duck_egg` | 12 HP | N/A (Harvested) | Gathered from riverside duck nesting grounds and farm coops. | Thick-shelled duck egg, key ingredient for Balut and Itlog na Maalat. |
| Fresh Carabao Milk | `carabao_milk` | 35 HP | N/A (Harvested) | Gently milked from docile carabaos resting near mud wallows. | Rich, creamy milk from Philippine water buffalo. High in butterfat. |

---

## Pantry, Spices, and Cooking Essentials
Foundational crops, milled grains, seasonings, and binding agents used across recipes.

| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |
|---|---|---|---|---|---|
| Raw Potato | `raw_potato` | 25 HP | N/A (Harvested) | Cultivated from Tilled Soil or harvested from wild Spud patches. | Crisp subterranean tuber. Right-click to consume for +25 HP or cook in a furnace. |
| Milagrosa White Rice | `rice` | Ingredient | N/A (Harvested) | Harvested from flooded paddy tiles or purchased from rural traders. | Fragrant polished grain. A meal in Potaria is never complete without rice. |
| Bawang Garlic | `garlic` | Ingredient | N/A (Harvested) | Foraged in lowland grassy meadows or cultivated in home gardens. | Pungent native garlic cloves. The aromatic foundation of Filipino cuisine. |
| Sibuyas Red Onion | `onion` | Ingredient | N/A (Harvested) | Cultivated from vegetable seeds or found in agricultural crates. | Sweet, vibrant red onion bulbs essential for sautéing. |
| Luya Fresh Ginger | `ginger` | Ingredient | N/A (Harvested) | Harvested from root patches in forest clearings and riverbanks. | Zesty, warming ginger root that infuses tinola and arroz caldo broth. |
| Sampalok Tamarind | `tamarind` | Ingredient | N/A (Harvested) | Gathered from tropical wild tamarind trees. | Tangy tamarind pods that give Sinigang its signature appetizing sourness. |
| Talong Native Eggplant | `eggplant` | 12 HP | N/A (Harvested) | Farmed in fertile soil patches or collected from wild flora. | Glossy purple tender eggplant, key vegetable for Sinigang and Tortang Talong. |
| Sitaw String Beans | `string_beans` | 12 HP | N/A (Harvested) | Cultivated along crop trellises or foraged in bushlands. | Crisp green yardlong beans harvested fresh from farm trellises. |
| Paminta Peppercorns | `black_pepper` | Ingredient | N/A (Harvested) | Harvested from pepper vines in deep forest groves. | Whole black peppercorns from aromatic spice groves. |
| Calamansi Citrus | `calamansi` | 10 HP | N/A (Harvested) | Picked from native citrus shrubs found near coastal settlements. | Tart and aromatic Philippine lime. Adds bright acidity to dipping sauces. |
| Toyo Soy Sauce | `soy_sauce` | Ingredient | N/A (Harvested) | Brewed condiment obtained from general goods traders or fermented cellars. | Fermented rich black soy sauce. Savory cornerstone of adobo. |
| Sukang Paombong Vinegar | `vinegar` | Ingredient | By Hand | 1x Spud Sap | Traditional cane and palm vinegar with sharp, clean tartness. |
| Asin Sea Salt | `salt` | Ingredient | Furnace | 2x Tangled Seaweed | Pure crystallized white sea salt harvested from coastal pans. |
| Yelo Shaved Ice | `shaved_ice` | Ingredient | By Hand | 1x Snow Block | Fine snowy ice flakes scooped to create the ultimate tropical cooling treat. |
| Sweet Condensed Milk | `condensed_milk` | 25 HP | Furnace | 1x Fresh Carabao Milk, 1x Spud Sap | Sweet, golden thick milk syrup poured lavishly over shaved ice desserts. |
| Ube Halaya Jam | `ube_halaya` | 35 HP | Furnace | 2x Raw Potato, 1x Sweet Condensed Milk, 1x Spud Sap | Decadent purple yam jam simmered slowly with butter and milk. |
| Bihon Rice Noodles | `pancit_noodles` | Ingredient | By Hand | 2x Milagrosa White Rice | Delicate sun-dried translucent rice noodles. Symbolizes long life and health. |
| Ground Peanut Butter | `peanut_butter` | 22 HP | Furnace | 2x Raw Potato, 1x Spud Sap, 1x Asin Sea Salt | Savory roasted peanut paste that thickens luscious Kare-Kare sauce. |
| Gata Coconut Milk | `coconut_milk` | 20 HP | By Hand | 2x Wood, 1x Spud Sap | Rich, velvety cream pressed from freshly grated mature coconut meat. |
| Spud Sap | `spud_sap` | Ingredient | N/A (Harvested) | Extracted by tapping mature wild tuber roots and sacred trees. | Sticky organic slime sap harvested from slimes. Essential for torches, arrows, and potions. |
| Tangled Seaweed | `seaweed` | Ingredient | N/A (Harvested) | Dived and foraged along shallow coastal waters and coral reefs. | Briny dark green kelp ribbons harvested from coastal waters. |
| Snow Block | `snow_block` | Ingredient | N/A (Harvested) | Quarried from the frosty peaks of the sub-zero alpine biome. | Packed powdery snow from the glacial tundra. |
| Wood | `wood` | Ingredient | N/A (Harvested) | Chopped from forest trees using any woodcutting axe. | Lumber harvested from surface trees. Right-click to place or craft into workbench. |
| Glowing Mushroom | `glowing_mushroom` | Ingredient | N/A (Harvested) | Harvested from bioluminescent deep cavern biomes. | Bioluminescent mushroom cap. Ingredient for Greater Healing Potions. |
| Gold Bar | `gold_bar` | Ingredient | Furnace | 3x Gold Ore | Pure gold ingot smelted from 3 gold ores. Used for high-tier swords and runes. |

---
