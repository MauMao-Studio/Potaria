using UnityEngine;

namespace Potaria.Data
{
    public enum EquipSlot
    {
        Helmet,
        Chestplate,
        Greaves,
        Boots,
        Accessory,
        Ring,
        Amulet
    }

    /// <summary>
    /// ScriptableObject representing wearable equipment and armor pieces in Potaria.
    /// Can belong to an EquipmentSetData.
    /// </summary>
    [CreateAssetMenu(fileName = "NewEquipmentItemData", menuName = "Potaria/Items/Equipment Item Data", order = 13)]
    public class EquipmentItemData : ItemData
    {
        [Header("Equipment Slot")]
        [SerializeField] private EquipSlot equipSlot = EquipSlot.Chestplate;
        [SerializeField] private string setId = string.Empty;

        [Header("Defense & Attributes")]
        [SerializeField] private int defense = 5;
        [SerializeField] private int attack = 0;
        [SerializeField] private float critChance = 0.0f;
        [SerializeField] private float speed = 0.0f;
        [SerializeField] private int bonusHp = 10;
        [SerializeField] private int bonusMp = 0;
        [SerializeField] private float mpRegen = 0.0f;

        [Header("Affixes")]
        [SerializeField] private int affixSlots = 0;

        public EquipSlot EquipSlot { get => equipSlot; set => equipSlot = value; }
        public string SetId { get => setId; set => setId = value; }
        public int Defense { get => defense; set => defense = value; }
        public int Attack { get => attack; set => attack = value; }
        public float CritChance { get => critChance; set => critChance = value; }
        public float Speed { get => speed; set => speed = value; }
        public int BonusHp { get => bonusHp; set => bonusHp = value; }
        public int BonusMp { get => bonusMp; set => bonusMp = value; }
        public float MpRegen { get => mpRegen; set => mpRegen = value; }
        public int AffixSlots { get => affixSlots; set => affixSlots = value; }

        public override string GetFormattedTooltip()
        {
            var baseTooltip = base.GetFormattedTooltip();
            var equipDetails = $"\n<color=#A0A0A0>Slot: {equipSlot}</color>";
            if (!string.IsNullOrEmpty(setId))
            {
                equipDetails += $"\n<color=#FFD700>Set: {setId}</color>";
            }
            if (defense > 0) equipDetails += $"\n<color=#59A6FF>DEF: +{defense}</color>";
            if (attack > 0) equipDetails += $"  <color=#FF5959>ATK: +{attack}</color>";
            if (bonusHp > 0) equipDetails += $"  <color=#4CD964>HP: +{bonusHp}</color>";
            if (bonusMp > 0) equipDetails += $"  <color=#00D9FF>MP: +{bonusMp}</color>";
            if (critChance > 0) equipDetails += $"  <color=#FFD700>CRIT: +{critChance:0.#}%</color>";
            if (speed != 0) equipDetails += $"  <color=#59F273>SPD: +{speed:0.##}</color>";
            if (affixSlots > 0) equipDetails += $"\n<color=#B240E6>Affix Slots: {affixSlots}</color>";
            return $"{baseTooltip}{equipDetails}";
        }
    }
}
