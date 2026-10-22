# Potaria - Android Packaging and Compatibility Guide

## 1. Target Android Version & Compatibility Matrix

Potaria is configured to target Android 11 through the latest Android releases:

- Minimum SDK: API Level 30 (Android 11)
- User Device: Android 12 (API Level 31/32)
- Target SDK: API Level 34 (Android 14) / API Level 35 (Android 15)
- Architecture Support: `arm64-v8a` (modern 64-bit devices) and `armeabi-v7a` (32-bit legacy devices)

### Supported Android Versions
- Android 11 (API 30) - Full support
- Android 12 / 12L (API 31 / 32) - Full support (User test device)
- Android 13 (API 33) - Full support
- Android 14 (API 34) - Full support
- Android 15 (API 35) - Full support

Targeting API Level 30+ satisfies modern Android security policies, Scoped Storage requirements, and Google Play Store submission guidelines while covering over 92% of active Android devices worldwide.

---

## 2. Multi-Aspect Ratio and Viewport Scaling Architecture

Android smartphones feature varied screen aspect ratios:
- 16:9 (Standard HD / QHD, e.g. 1920x1080)
- 18:9 (2:1, e.g. 2160x1080)
- 19:9 / 19.5:9 (Waterdrop / punch-hole displays, e.g. 2340x1080)
- 20:9 (Modern smartphones, e.g. 2400x1080)
- 21:9 (Ultrawide cinematic phones, e.g. 2520x1080)

### How Potaria Solves Screen Distortion
1. **Fixed Virtual Reference Resolution**: The entire internal engine renders to a reference 1280x720 canvas (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).
2. **Aspect Ratio Preservation with Letterbox / Pillarbox**: The hardware abstraction layer (`SurfaceRenderer` and `GLRenderer`) applies uniform scale factor `min(scale_x, scale_y)` and centers the viewport.
3. **Mathematical Touch Coordinate Translation (`window_to_virtual_pos`)**: Every touch event received by Android is remapped back to virtual (1280, 720) canvas coordinates:
   - Offsets for pillarbox (left/right black bars) and letterbox (top/bottom bars) are subtracted.
   - Coordinates are normalized and scaled.
   - Result: Button hitboxes, virtual joystick, inventory slots, and touch targets never drift or misalign regardless of device screen dimensions.

---

## 3. Touchscreen Controls Architecture

Potaria includes a native on-screen touch controller (`src/ui/touch_controller.py`):
- **Virtual Left Joystick**: Dynamic thumb tracking with travel limiting.
- **Action Cluster (Bottom-Right)**: Jump, Attack/Mine, Dash, and Quick Potion/Heal with high-contrast icons and tactile depression animations.
- **Quick Skill Radial Arc**: Direct triggers for learned skills (hotkeys Q, F, V, R) with visual cooldown sweeps.
- **Top Bar Utility Buttons**: Backpack [E], Character Paperdoll [C], and Menu [ESC].
- **Direct World Touch**: Tap directly on blocks or water to mine, place, till soil, water farmland, or harvest crops.
- **Minimum Target Size**: All touch buttons meet or exceed the recommended 48x48 pixel touch footprint for mobile ergonomics.

---

## 4. Building the Android APK

### One-Click Automated Build Command (Ubuntu / VirtualBox)
On a fresh Ubuntu terminal inside VirtualBox, run this single compound command to install git and all dependencies, clone the repository, configure the environment, and compile the APK:

```bash
sudo apt update && sudo apt install -y git curl && ([ -d Potaria ] || git clone https://github.com/MauMao-Studio/Potaria.git) && cd Potaria && git pull && chmod +x scripts/build_apk_ubuntu.sh && ./scripts/build_apk_ubuntu.sh
```

### Manual Prerequisites
- Python 3.10+ or Python 3.11
- OpenJDK 17
- Build tools: `autoconf`, `automake`, `libtool`, `libltdl-dev`, `autopoint`, `gettext`, `pkg-config`, `cmake`, `ccache`
- Android SDK (API 30 through 34) and Android NDK (r25b or r26b)
- Buildozer (`pip install buildozer`) or python-for-android (`p4a`)

### Build Command
Run the buildozer pipeline inside the project directory:

```bash
buildozer android debug
```

Or for release build:

```bash
buildozer android release
```

The resulting package will be generated inside the `bin/` directory:
- `bin/Potaria-1.1.0-arm64-v8a-debug.apk`

### Installing and Running on Device
Connect the Android device via USB with USB Debugging enabled:

```bash
adb install -r bin/Potaria-1.1.0-arm64-v8a-debug.apk
```

Or run directly with logcat monitoring:

```bash
buildozer android deploy run logcat
```

---

## 5. Unity 6 LTS Android Build Pipeline (Current Active Engine)

With the engine transition to **Unity 6 LTS (v6000.0.58f1)**, Android packaging is streamlined into Unity's enterprise-grade native compilation pipeline:

### Advantages of the Unity 6 Android Pipeline:
- **IL2CPP Compilation**: Converts C# into native C++ code compiled ahead-of-time (AOT) by the Android NDK, delivering console-grade CPU performance and high framerates (60 to 120 FPS).
- **Google Play App Bundle (.aab)**: Generates optimized `.aab` packages ready for the Google Play Console with dynamic feature delivery and asset packs.
- **Native Touch & Input System**: Touch events are processed with hardware sub-frame accuracy, eliminating touch input lag.
- **Universal Render Pipeline (URP 2D)**: Hardware-accelerated rendering utilizing Vulkan or OpenGL ES 3.2 with dynamic resolution scaling.
- **Zero Recipe / C-Extension Mismatches**: Completely eliminates Python C-extension build issues (`python-for-android`, `sdl2`, `cython` build mismatches).

### How to Build APK or AAB in Unity 6:
1. Open the project in **Unity 6000.0.58f1**.
2. Go to **File -> Build Settings** (`Ctrl + Shift + B`).
3. Select **Android** in the platform list and click **Switch Platform**.
4. Click **Player Settings...**:
   - **Company Name**: `MauMao Studio`
   - **Product Name**: `Potaria`
   - **Package Name**: `com.maumao.potaria`
   - **Minimum API Level**: `Android 11.0 (API Level 30)`
   - **Target API Level**: `Android 14.0 / 15.0 (API Level 34 / 35)`
   - **Scripting Backend**: `IL2CPP`
   - **Target Architectures**: Check `ARMv7` and `ARM64`
5. To generate an APK for direct testing, click **Build** and choose an output path (e.g. `Builds/Android/Potaria.apk`).
6. To generate a Google Play Store submission package, check **Build App Bundle (Google Play)** and click **Build**.

*(Note: The Buildozer and python-for-android instructions in Section 4 are preserved for building the legacy Pygame engine on the `pygame-engine` branch).*
