using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Potaria.Localization
{
    /// <summary>
    /// Global localization system for Potaria.
    /// Provides zero-allocation lookup, multi-language support (English 'en' and Filipino 'fil'),
    /// hot-reloading, and instant language toggle via hotkey or script.
    /// </summary>
    public static class LocalizationManager
    {
        public const string LANG_EN = "en";
        public const string LANG_FIL = "fil";

        private static string s_currentLanguage = LANG_EN;
        private static readonly Dictionary<string, string> s_strings = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        private static bool s_isInitialized = false;

        public static event Action OnLanguageChanged;

        public static string CurrentLanguage => s_currentLanguage;

        public static string CurrentLanguageDisplayName => s_currentLanguage switch
        {
            LANG_FIL => "Filipino / Tagalog",
            _ => "English"
        };

        static LocalizationManager()
        {
            EnsureInitialized();
        }

        public static void EnsureInitialized()
        {
            if (s_isInitialized && s_strings.Count > 0) return;
            LoadLanguage(s_currentLanguage);
            s_isInitialized = true;
        }

        public static void SetLanguage(string langCode)
        {
            if (string.IsNullOrEmpty(langCode)) langCode = LANG_EN;
            langCode = langCode.ToLowerInvariant().Trim();
            if (langCode != LANG_EN && langCode != LANG_FIL)
            {
                langCode = LANG_EN;
            }

            s_currentLanguage = langCode;
            LoadLanguage(s_currentLanguage);
            OnLanguageChanged?.Invoke();
        }

        public static void ToggleLanguage()
        {
            SetLanguage(s_currentLanguage == LANG_EN ? LANG_FIL : LANG_EN);
        }

        public static string Get(string key, string fallback = "")
        {
            EnsureInitialized();
            if (string.IsNullOrEmpty(key)) return fallback;

            if (s_strings.TryGetValue(key, out var val))
            {
                return val;
            }

            return string.IsNullOrEmpty(fallback) ? key : fallback;
        }

        public static string GetFormat(string key, params object[] args)
        {
            string pattern = Get(key, key);
            try
            {
                return string.Format(pattern, args);
            }
            catch
            {
                return pattern;
            }
        }

        private static void LoadLanguage(string langCode)
        {
            s_strings.Clear();

            // 1. Try loading from Resources/Localization/{langCode}
            TextAsset textAsset = Resources.Load<TextAsset>($"Localization/{langCode}");
            string jsonText = null;

            if (textAsset != null)
            {
                jsonText = textAsset.text;
            }
            else
            {
                // Fallback to direct file read if running in Editor or standalone path
                string filePath = Path.Combine(Application.dataPath, "Resources", "Localization", $"{langCode}.json");
                if (File.Exists(filePath))
                {
                    jsonText = File.ReadAllText(filePath);
                }
            }

            if (!string.IsNullOrEmpty(jsonText))
            {
                ParseSimpleJson(jsonText, s_strings);
            }

            // Always ensure core fallback defaults exist in case JSON was partial
            PopulateHardcodedFallbacks(langCode, s_strings);
        }

        private static void ParseSimpleJson(string json, Dictionary<string, string> dict)
        {
            // Lightweight robust JSON key-value parser for string:string
            string[] lines = json.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var rawLine in lines)
            {
                string line = rawLine.Trim();
                if (!line.Contains(":") || line.StartsWith("{") || line.StartsWith("}")) continue;

                int colonIdx = line.IndexOf(':');
                if (colonIdx <= 0) continue;

                string rawKey = line.Substring(0, colonIdx).Trim().Trim('"', ',');
                string rawVal = line.Substring(colonIdx + 1).Trim().Trim('"', ',');

                // Remove trailing comma if present
                if (rawVal.EndsWith(",")) rawVal = rawVal.Substring(0, rawVal.Length - 1).Trim().Trim('"');

                if (!string.IsNullOrEmpty(rawKey))
                {
                    dict[rawKey] = rawVal;
                }
            }
        }

        private static void PopulateHardcodedFallbacks(string langCode, Dictionary<string, string> dict)
        {
            bool isFil = (langCode == LANG_FIL);

            void SetDefault(string k, string enVal, string filVal)
            {
                if (!dict.ContainsKey(k)) dict[k] = isFil ? filVal : enVal;
            }

            SetDefault("hud.life", "Life: {0} / {1} (Lv.{2})", "Buhay: {0} / {1} (Antas {2})");
            SetDefault("hud.mp", "MP: {0} / {1}", "Diwa: {0} / {1}");
            SetDefault("hud.level", "Lv.{0}", "Antas {0}");
            SetDefault("hud.day", "DAY", "ARAW");
            SetDefault("hud.night", "NIGHT", "GABI");
            SetDefault("hud.radar", "[M] RADAR", "[M] RADAR");
            SetDefault("hud.clock_format", "{0}:{1:D2} {2} {3}", "{0}:{1:D2} {2} {3}");
            SetDefault("hud.lang_prompt", "[L] Lang: {0}", "[L] Wika: {0}");

            SetDefault("skill.q.abbr", "SWI", "BIL");
            SetDefault("skill.q.name", "Swift Strike", "Mabilis na Taga");
            SetDefault("skill.f.abbr", "CEL", "LAN");
            SetDefault("skill.f.name", "Celestial Surge", "Daluyong ng Langit");
            SetDefault("skill.v.abbr", "POW", "LAK");
            SetDefault("skill.v.name", "Power Burst", "Pagsabog ng Lakas");
            SetDefault("skill.r.abbr", "WHI", "PUT");
            SetDefault("skill.r.name", "Celestial Reversal", "Liwanag ng Langit");

            SetDefault("mob.green_slime", "Green Slime", "Berdeng Putik");
            SetDefault("mob.purple_slime", "Purple Slime", "Lilang Putik");
            SetDefault("mob.zombie", "Surface Zombie", "Bangkay sa Ibabaw");
            SetDefault("mob.demon_eye", "Night Gazer", "Maninilip sa Gabi");
        }
    }
}
