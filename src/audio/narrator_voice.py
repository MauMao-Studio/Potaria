"""
Potaria - Cinematic Narrator Voice Engine
Synthesizes deep, mythic, resonant storytelling voice tracks for the cutscene lore:
recounting the Golden Age of Sol-Rho, the Celestial Keystone, The Sundering,
the Nether Titans, and the Chosen Tuber Spud.

Supports:
1. Google Gemini API (gemini-3.8-flash-tts) via google-genai SDK when GEMINI_API_KEY is present.
2. High-quality pure Python procedural speech formant synthesizer fallback (100% offline zero-breakage).
Developer: Kurados
"""

import os
import wave
import math
import struct
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_target_dir(d):
    """Resolves relative asset paths to absolute paths anchored at project root."""
    if os.path.isabs(d):
        return d
    return os.path.join(PROJECT_ROOT, d)


# Full Act-level composite texts (guarantees narrator_scene1.wav .. narrator_scene4.wav on disk)
NARRATOR_SCENE_TEXTS = {
    "narrator_scene1": (
        "In the dawn before memory, the Root Realm of Potaria flourished under the boundless warmth of the Celestial Keystone."
    ),
    "narrator_scene2": (
        "Yet harmony was shattered in an instant. A cosmic cataclysm struck from the void—the Celestial Keystone fractured into radiant shards! "
        "The skies darkened with ominous storm clouds, while subterranean fissures bled boiling molten magma and creeping purple corruption."
    ),
    "narrator_scene3": (
        "From the elemental rifts arose three colossal Nether Titans, claiming the shattered celestial shards to bend the biomes to their will. "
        "Ignis Colossus seized the volcanic deeps, Cryo-Spud froze the northern peaks, and Lord Malus entrenched in the Nether Dungeon."
    ),
    "narrator_scene4": (
        "When all hope seemed withered beneath the corrupt soil, an ancient prophecy stirred within the sacred earth... "
        "Take up your tools, courageous Spud. Explore the boundless world, master forgotten skills, defeat the Titans, and restore Potaria!"
    ),
}

# Individual dialogue entry lines for synchronous in-game cutscene playback without dialogue bleed
NARRATOR_ENTRY_TEXTS = {
    "narrator_scene1": (
        "In the dawn before memory, the Root Realm of Potaria flourished under the boundless warmth of the Celestial Keystone."
    ),
    "narrator_scene2_1": (
        "Yet harmony was shattered in an instant. A cosmic cataclysm struck from the void—the Celestial Keystone fractured into radiant shards!"
    ),
    "narrator_scene2_2": (
        "The skies darkened with ominous storm clouds, while subterranean fissures bled boiling molten magma and creeping purple corruption."
    ),
    "narrator_scene3_1": (
        "From the elemental rifts arose three colossal Nether Titans, claiming the shattered celestial shards to bend the biomes to their will."
    ),
    "narrator_scene3_2": (
        "Ignis Colossus seized the volcanic deeps, Cryo-Spud froze the northern peaks, and Lord Malus entrenched in the Nether Dungeon."
    ),
    "narrator_scene4_1": (
        "When all hope seemed withered beneath the corrupt soil, an ancient prophecy stirred within the sacred earth..."
    ),
    "narrator_scene4_2": (
        "Take up your tools, courageous Spud. Explore the boundless world, master forgotten skills, defeat the Titans, and restore Potaria!"
    ),
}

# Scene & dialogue entry key aliases for flexible lookup
SCENE_KEY_ALIASES = {
    # Scene 1
    "1": "narrator_scene1",
    1: "narrator_scene1",
    "scene_1": "narrator_scene1",
    "scene_1_golden_age": "narrator_scene1",
    "narrator_scene1": "narrator_scene1",
    "entry_0": "narrator_scene1",
    0: "narrator_scene1",

    # Scene 2
    "2": "narrator_scene2",
    2: "narrator_scene2",
    "scene_2": "narrator_scene2",
    "scene_2_cataclysm": "narrator_scene2",
    "narrator_scene2": "narrator_scene2",
    "narrator_scene2_1": "narrator_scene2_1",
    "narrator_scene2_2": "narrator_scene2_2",
    "scene_2_1": "narrator_scene2_1",
    "scene_2_2": "narrator_scene2_2",
    "entry_3": "narrator_scene2_1",
    3: "narrator_scene2_1",
    "entry_4": "narrator_scene2_2",
    4: "narrator_scene2_2",

    # Scene 3
    "3": "narrator_scene3",
    3: "narrator_scene3",
    "scene_3": "narrator_scene3",
    "scene_3_titans": "narrator_scene3",
    "narrator_scene3": "narrator_scene3",
    "narrator_scene3_1": "narrator_scene3_1",
    "narrator_scene3_2": "narrator_scene3_2",
    "scene_3_1": "narrator_scene3_1",
    "scene_3_2": "narrator_scene3_2",
    "entry_6": "narrator_scene3_1",
    6: "narrator_scene3_1",
    "entry_8": "narrator_scene3_2",
    8: "narrator_scene3_2",

    # Scene 4
    "4": "narrator_scene4",
    4: "narrator_scene4",
    "scene_4": "narrator_scene4",
    "scene_4_chosen_tuber": "narrator_scene4",
    "narrator_scene4": "narrator_scene4",
    "narrator_scene4_1": "narrator_scene4_1",
    "narrator_scene4_2": "narrator_scene4_2",
    "scene_4_1": "narrator_scene4_1",
    "scene_4_2": "narrator_scene4_2",
    "entry_9": "narrator_scene4_1",
    9: "narrator_scene4_1",
    "entry_12": "narrator_scene4_2",
    12: "narrator_scene4_2",
}


def normalize_scene_key(scene_id):
    """Normalizes any scene name, integer, or identifier to standard narrator track key."""
    if scene_id in SCENE_KEY_ALIASES:
        return SCENE_KEY_ALIASES[scene_id]
    s_str = str(scene_id).lower().strip()
    if s_str in SCENE_KEY_ALIASES:
        return SCENE_KEY_ALIASES[s_str]
    for alias, key in SCENE_KEY_ALIASES.items():
        if str(alias).lower() == s_str:
            return key
    if "scene_2_1" in s_str or "entry_3" in s_str:
        return "narrator_scene2_1"
    if "scene_2_2" in s_str or "entry_4" in s_str:
        return "narrator_scene2_2"
    if "scene_3_1" in s_str or "entry_6" in s_str:
        return "narrator_scene3_1"
    if "scene_3_2" in s_str or "entry_8" in s_str:
        return "narrator_scene3_2"
    if "scene_4_1" in s_str or "entry_9" in s_str:
        return "narrator_scene4_1"
    if "scene_4_2" in s_str or "entry_12" in s_str:
        return "narrator_scene4_2"
    if "1" in s_str or "golden" in s_str:
        return "narrator_scene1"
    if "2" in s_str or "cataclysm" in s_str:
        return "narrator_scene2"
    if "3" in s_str or "titan" in s_str:
        return "narrator_scene3"
    if "4" in s_str or "chosen" in s_str or "spud" in s_str:
        return "narrator_scene4"
    return "narrator_scene1"


def save_wav_file(filepath, samples, sample_rate=22050):
    """Writes normalized mono/stereo floating point samples (-1.0 to 1.0) as 16-bit stereo WAV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    buf = bytearray()
    for s in samples:
        s_clamped = max(-1.0, min(1.0, float(s)))
        ival = int(s_clamped * 32767.0)
        # Duplicate to stereo left and right channels
        buf += struct.pack("<hh", ival, ival)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(buf))


def synthesize_procedural_narrator_track(text, sample_rate=22050):
    """
    Synthesizes deep, mythic, resonant cinematic storyteller narration.
    Uses formant glottal pulse modeling (baritone F0 ~78-85Hz), vowel resonant filters,
    sub-bass chest rumble (40Hz), and a stereo cathedral delay/reverb tail.
    """
    sr = sample_rate
    rng = random.Random(hash(text) & 0xFFFFFFFF)
    words = text.split()
    samples = []

    base_f0 = 78.0  # Deep resonant baritone/bass

    vowel_formants = {
        'a': (720, 1240, 2600),
        'e': (490, 1820, 2750),
        'i': (310, 2250, 2900),
        'o': (440, 840, 2400),
        'u': (340, 740, 2300),
    }

    # Delay line buffers for mythic cathedral hall reverb
    delays = [int(sr * d) for d in (0.024, 0.043, 0.068, 0.095)]
    delay_bufs = [[0.0] * d for d in delays]
    delay_ptrs = [0] * len(delays)
    phase = 0.0

    for w_idx, word in enumerate(words):
        clean_w = ''.join(c for c in word.lower() if c.isalnum())
        if not clean_w:
            continue

        vowels = [c for c in clean_w if c in vowel_formants]
        if not vowels:
            vowels = ['o']

        # Syllabic pacing: ~0.13 - 0.16s per syllable with rhythmic cadence
        syl_dur = 0.135
        word_stress = 1.0 + 0.10 * math.sin(w_idx * 1.35)

        for syl_idx, v in enumerate(vowels):
            f1_t, f2_t, f3_t = vowel_formants.get(v, (450, 900, 2500))
            dur = syl_dur * word_stress * rng.uniform(0.92, 1.10)
            syl_samples = int(dur * sr)

            # Prosodic pitch contour: gentle arch across the sentence
            rel_w = w_idx / max(1, len(words) - 1)
            pitch_curve = math.sin(rel_w * math.pi) * 7.5 - (rel_w * 5.0)
            cur_f0 = base_f0 + pitch_curve + rng.uniform(-1.0, 1.0)

            for i in range(syl_samples):
                t_syl = i / syl_samples
                # Natural human vocal vibrato (4.6 Hz) & chest tremor
                vibrato = math.sin(i * 2.0 * math.pi * 4.6 / sr) * 1.25
                inst_f0 = cur_f0 + vibrato
                phase += 2.0 * math.pi * inst_f0 / sr

                # Glottal pulse: asymmetric vocal cord wave rich in low harmonics
                glot = (
                    math.sin(phase) * 0.70 +
                    math.sin(2.0 * phase) * 0.42 +
                    math.sin(3.0 * phase) * 0.28 +
                    math.sin(4.0 * phase) * 0.16 +
                    math.sin(5.0 * phase) * 0.10
                )

                # Formant resonances excited by glottal stream
                p1 = 2.0 * math.pi * f1_t * (i / sr)
                p2 = 2.0 * math.pi * f2_t * (i / sr)
                p3 = 2.0 * math.pi * f3_t * (i / sr)
                formant_mix = (
                    math.sin(p1) * 0.45 +
                    math.sin(p2) * 0.30 +
                    math.sin(p3) * 0.15
                )

                # Sub-bass chest resonance (39Hz)
                sub_bass = math.sin(phase * 0.5) * 0.26

                # Subtle vocal air / breath texture
                air = rng.uniform(-0.04, 0.04)

                # Syllabic envelope with smooth attack and decay
                env = (math.sin(t_syl * math.pi) ** 1.25)

                raw_sample = ((glot * (1.0 + formant_mix * 0.75) + sub_bass) * 0.70 + air) * env

                # Cathedral hall reverberation feed
                rev_sum = 0.0
                for d_idx in range(len(delays)):
                    d_buf = delay_bufs[d_idx]
                    d_ptr = delay_ptrs[d_idx]
                    echo = d_buf[d_ptr]
                    d_buf[d_ptr] = raw_sample * 0.25 + echo * 0.38
                    delay_ptrs[d_idx] = (d_ptr + 1) % delays[d_idx]
                    rev_sum += echo

                final_val = raw_sample * 0.75 + rev_sum * 0.25
                samples.append(final_val)

        # Pause between words and punctuation marks
        if word.endswith(('.', '!', '?')):
            pause_dur = 0.32
        elif word.endswith((',', ';', ':')):
            pause_dur = 0.18
        else:
            pause_dur = 0.05

        pause_samples = int(pause_dur * sr)
        for _ in range(pause_samples):
            rev_sum = 0.0
            for d_idx in range(len(delays)):
                d_buf = delay_bufs[d_idx]
                d_ptr = delay_ptrs[d_idx]
                echo = d_buf[d_ptr]
                d_buf[d_ptr] = echo * 0.38
                delay_ptrs[d_idx] = (d_ptr + 1) % delays[d_idx]
                rev_sum += echo
            samples.append(rev_sum * 0.25)

    # Normalize amplitude
    max_amp = max((abs(s) for s in samples), default=1.0)
    if max_amp > 0.001:
        samples = [s / max_amp * 0.88 for s in samples]

    return samples


def generate_narrator_voices_with_gemini(api_key=None, target_dirs=("assets/cutscene", "assets/story"), track_dict=None):
    """
    Attempts to generate high-fidelity cinematic narrator voice tracks using the Gemini API
    with model 'gemini-3.8-flash-tts' via the official google-genai SDK or standard urllib REST.
    Follows gemini-api-dev skill guidelines.
    Returns True if generation succeeds, False if API key is missing or an error occurs.
    """
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_key:
        return False

    resolved_dirs = [resolve_target_dir(d) for d in target_dirs]
    tracks_to_generate = track_dict if track_dict is not None else NARRATOR_SCENE_TEXTS

    # 1. Attempt official google-genai SDK first
    try:
        import base64
        from google import genai

        client = genai.Client(api_key=resolved_key)
        for scene_key, text in tracks_to_generate.items():
            interaction = client.interactions.create(
                model="gemini-3.8-flash-tts",
                input=[{
                    "type": "user_input",
                    "content": [{
                        "type": "text",
                        "text": text,
                        "annotations": [{
                            "type": "speech_metadata",
                            "style": "deep, mythic, cinematic storyteller voice recounting an ancient legend with resonance and gravitas",
                        }],
                    }],
                }],
                response_format={"type": "audio"},
                generation_config={
                    "speech_config": [
                        {"voice": "Fenrir"},
                    ]
                },
            )
            if not interaction.output_audio or not interaction.output_audio.data:
                return False

            wav_data = base64.b64decode(interaction.output_audio.data)
            for d in resolved_dirs:
                os.makedirs(d, exist_ok=True)
                fn = os.path.join(d, f"{scene_key}.wav")
                with open(fn, "wb") as f:
                    f.write(wav_data)

        print("[NarratorVoice] Successfully generated cutscene narrator tracks via Google Gemini TTS!")
        return True

    except Exception as sdk_err:
        # 2. Zero-dependency REST API Fallback via standard library urllib
        try:
            import json
            import urllib.request
            import base64

            rest_url = "https://generativelanguage.googleapis.com/v1beta/interactions"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": resolved_key,
            }

            for scene_key, text in tracks_to_generate.items():
                payload = {
                    "model": "gemini-3.8-flash-tts",
                    "input": [{
                        "type": "user_input",
                        "content": [{
                            "type": "text",
                            "text": text,
                            "annotations": [{
                                "type": "speech_metadata",
                                "style": "deep, mythic, cinematic storyteller voice recounting an ancient legend with resonance and gravitas",
                            }],
                        }],
                    }],
                    "response_format": {
                        "type": "audio",
                        "mime_type": "audio/wav",
                    },
                    "generation_config": {
                        "speech_config": [
                            {"voice": "Fenrir"},
                        ]
                    },
                }

                req = urllib.request.Request(rest_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    audio_b64 = None
                    if "output_audio" in resp_data and "data" in resp_data["output_audio"]:
                        audio_b64 = resp_data["output_audio"]["data"]
                    elif "steps" in resp_data:
                        for step in resp_data.get("steps", []):
                            if step.get("type") == "model_output":
                                for c in step.get("content", []):
                                    if c.get("type") == "audio" and "data" in c:
                                        audio_b64 = c["data"]
                                        break
                    if not audio_b64:
                        return False
                    wav_data = base64.b64decode(audio_b64)
                    for d in resolved_dirs:
                        os.makedirs(d, exist_ok=True)
                        fn = os.path.join(d, f"{scene_key}.wav")
                        with open(fn, "wb") as f:
                            f.write(wav_data)

            print("[NarratorVoice] Successfully generated cutscene narrator tracks via Gemini REST API!")
            return True

        except Exception as rest_err:
            print(f"[NarratorVoice] Gemini TTS notice: {sdk_err}. Falling back to authentic procedural voice synthesis.")
            return False


def ensure_narrator_audio_assets(target_dirs=("assets/cutscene", "assets/story"), force_regenerate=False, sample_rate=22050):
    """
    Ensures that all narrator cutscene WAV files exist on disk (both 4 scene acts and dialogue segments).
    If GEMINI_API_KEY is present, tries Gemini TTS first; otherwise or on failure,
    synthesizes them procedurally so the game is 100% playable offline out of the box.
    Returns a dictionary mapping scene key -> file path.
    """
    scene_keys = ["narrator_scene1", "narrator_scene2", "narrator_scene3", "narrator_scene4"]
    segment_keys = [
        "narrator_scene2_1", "narrator_scene2_2",
        "narrator_scene3_1", "narrator_scene3_2",
        "narrator_scene4_1", "narrator_scene4_2"
    ]
    all_keys = scene_keys + segment_keys

    resolved_dirs = [resolve_target_dir(d) for d in target_dirs]
    primary_dir = resolved_dirs[0] if resolved_dirs else resolve_target_dir("assets/cutscene")

    # Check if files already exist in primary directory
    all_exist = True
    if not force_regenerate:
        for k in all_keys:
            p = os.path.join(primary_dir, f"{k}.wav")
            if not os.path.isfile(p) or os.path.getsize(p) < 1000:
                all_exist = False
                break
        if all_exist:
            # Also ensure replicated to secondary target dirs
            for other_dir in resolved_dirs[1:]:
                os.makedirs(other_dir, exist_ok=True)
                for k in all_keys:
                    src_p = os.path.join(primary_dir, f"{k}.wav")
                    dst_p = os.path.join(other_dir, f"{k}.wav")
                    if not os.path.isfile(dst_p) and os.path.isfile(src_p):
                        try:
                            with open(src_p, "rb") as sf, open(dst_p, "wb") as df:
                                df.write(sf.read())
                        except Exception:
                            pass
            return {k: os.path.join(primary_dir, f"{k}.wav") for k in all_keys}

    # Attempt Gemini API generation if key is present
    if os.environ.get("GEMINI_API_KEY"):
        success = generate_narrator_voices_with_gemini(target_dirs=resolved_dirs)
        if success:
            return {k: os.path.join(primary_dir, f"{k}.wav") for k in all_keys}

    # Authentic Procedural Audio Synthesis Fallback
    print("[NarratorVoice] Synthesizing procedural mythic cutscene narrator voice tracks...")
    results = {}

    all_tracks = dict(NARRATOR_SCENE_TEXTS)
    all_tracks.update(NARRATOR_ENTRY_TEXTS)

    for track_key, text in all_tracks.items():
        samples = synthesize_procedural_narrator_track(text, sample_rate=sample_rate)
        primary_path = os.path.join(primary_dir, f"{track_key}.wav")
        save_wav_file(primary_path, samples, sample_rate=sample_rate)
        results[track_key] = primary_path

        # Write to secondary directories as well
        for other_dir in resolved_dirs[1:]:
            other_path = os.path.join(other_dir, f"{track_key}.wav")
            save_wav_file(other_path, samples, sample_rate=sample_rate)

    print("[NarratorVoice] All cutscene narrator tracks synthesized and saved to disk.")
    return results
