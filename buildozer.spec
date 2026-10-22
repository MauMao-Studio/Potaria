[app]

# (str) Title of your application
title = Potaria

# (str) Package name
package.name = potaria

# (str) Package domain (needed for android/ios packaging)
package.domain = com.maumao.potaria

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,wav,ogg,json,ttf,txt

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, tools, scripts, .pytest_cache, __pycache__, .git

# (list) List of exclusions using pattern matching
source.exclude_patterns = *.pyc, *.docx, *.pdf, *.mp4

# (str) Application versioning
version = 1.1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame-ce

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/branding/game_icon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/branding/presplash_black.png

# (string) Presplash background color (for android toolchain)
android.presplash_color = #000000

# (str) Supported orientation (one of landscape, sensorLandscape, portrait, sensorPortrait, all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen to the user
fullscreen = 1

# (string) Prescale the window to match the physical resolution
android.prescale = 1

# (int) Target Android API level (34 = Android 14)
android.api = 34

# (int) Minimum Android API level (21 = Android 5.0+, fully supports Android 12, 13, 14, 15)
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API level
android.ndk_api = 21

# (str) Extra command line arguments to pass when invoking pythonforandroid.toolchain
p4a.extra_args = --allow-minsdk-ndkapi-mismatch

# (list) Android architectures to build for
android.archs = arm64-v8a

# (list) Permissions
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# (bool) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.wakelock = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
