using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// ScriptableObject representing weapons in Potaria with combat stats,
    /// affixes, and special weapon tags.
    /// </summary>
    [CreateAssetMenu(fileName = "NewWeaponItemData", menuName = "Potaria/Items/Weapon Item Data", order = 12)]
    public class WeaponItemData : ItemData
    {
        [Header("Weapon Combat Stats")]
        [SerializeField] private int attack = 10;
        [SerializeField] private int defense = 0;
        [SerializeField] private float critChance = 5.0f;
        [SerializeField] private float speed = 1.0f;
        [SerializeField] private int bonusHp = 0;
        [SerializeField] private int bonusMp = 0;
        [SerializeField] private float mpRegen = 0.0f;

        [Header("Affixes & Tags")]
        [SerializeField] private string specialTag = string.Empty;
        [SerializeField] private int affixSlots = 0;

        public int Attack { get => attack; set => attack = value; }
        public int Defense { get => defense; set => defense = value; }
        public float CritChance { get => critChance; set => critChance = value; }
        public float Speed { get => speed; set => speed = value; }
        public int BonusHp { get => bonusHp; set => bonusHp = value; }
        public int BonusMp { get => bonusMp; set => bonusMp = value; }
        public float MpRegen { get => mpRegen; set => mpRegen = value; }
        public string SpecialTag { get => specialTag; set => specialTag = value; }
        public int AffixSlots { get => affixSlots; set => affixSlots = value; }

        public override string GetFormattedTooltip()
        {
            var baseTooltip = base.GetFormattedTooltip();
            var combatStats = $"\n<color=#FF5959>ATK: +{attack}</color>";
            if (defense > 0) combatStats += $"  <color=#59A6FF>DEF: +{defense}</color>";
            if (critChance > 0) combatStats += $"  <color=#FFD700>CRIT: +{critChance:0.#}%</color>";
            if (speed != 0) combatStats += $"  <color=#59F273>SPD: +{speed:0.##}</color>";
            if (bonusHp > 0) combatStats += $"  <color=#4CD964>HP: +{bonusHp}</color>";
            if (bonusMp > 0) combatStats += $"  <color=#00D9FF>MP: +{bonusMp}</color>";
            if (affixSlots > 0) combatStats += $"\n<color=#B240E6>Affix Slots: {affixSlots}</color>";
            return $"{baseTooltip}{combatStats}";
        }
    }
}
