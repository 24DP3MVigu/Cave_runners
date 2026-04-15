"""
skanas.py — Skaņu un mūzikas sistēma.

Šajā failā ir visa audio loģika: MCI (Windows), pygame
atbalsts, un PowerShell fallback skaņu atskaņošanai.
"""

import os
import subprocess
import ctypes
from ctypes import wintypes

from iestatijumi import SOUND_DIR

# ============================================================
# Audio stāvokļa mainīgie (globāli šim modulim)
# ============================================================
SOUND_CACHE = {}
SOUND_ENABLED = False
CURRENT_MUSIC = None
AUDIO_BACKEND = None
MCI_SEND_STRING = None
_pygame = None  # Atsauce uz pygame moduli, ja tas ir pieejams

# ============================================================
# Audio inicializācija — mēģina MCI (Windows), tad pygame
# ============================================================
if os.name == 'nt':
    try:
        winmm = ctypes.WinDLL('winmm')
        MCI_SEND_STRING = winmm.mciSendStringW
        MCI_SEND_STRING.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, wintypes.HWND]
        MCI_SEND_STRING.restype = wintypes.UINT
        AUDIO_BACKEND = 'mci'
        SOUND_ENABLED = True
    except Exception:
        AUDIO_BACKEND = None

if not SOUND_ENABLED:
    try:
        import pygame as _pg
        _pg.mixer.pre_init(44100, -16, 2, 4096)
        _pg.init()
        _pg.mixer.init()
        _pygame = _pg
        AUDIO_BACKEND = 'pygame'
        SOUND_ENABLED = True
    except Exception:
        SOUND_ENABLED = False


# ============================================================
# MCI palīgfunkcijas (Windows audio)
# ============================================================

def mci_send_string(command):
    """Nosūta MCI komandu Windows audio sistēmai."""
    if MCI_SEND_STRING is None:
        return False
    try:
        return MCI_SEND_STRING(command, None, 0, None) == 0
    except Exception:
        return False


def get_mci_type(path):
    """Nosaka MCI faila tipu pēc paplašinājuma."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.wav':
        return 'waveaudio'
    return 'mpegvideo'


def mci_open(path, alias):
    """Atver audio failu ar MCI, vispirms aizverot iepriekšējo ar to pašu aizstājvārdu."""
    mci_send_string(f'close {alias}')
    file_type = get_mci_type(path)
    return mci_send_string(f'open "{path}" type {file_type} alias {alias}')


# ============================================================
# Skaņu ielādes un atskaņošanas funkcijas
# ============================================================

def load_sound_asset(filename):
    """Ielādē skaņas failu ar pygame (kešo atmiņā)."""
    if not SOUND_ENABLED or _pygame is None:
        return None
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return None
    try:
        if filename not in SOUND_CACHE:
            SOUND_CACHE[filename] = _pygame.mixer.Sound(path)
        return SOUND_CACHE[filename]
    except Exception:
        return None


def play_sound(filename, loops=0):
    """Atskaņo skaņas efektu. Mēģina MCI, tad PowerShell fallback, tad pygame."""
    if not SOUND_ENABLED:
        return
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return

    if AUDIO_BACKEND == 'mci':
        alias = 'sfx'
        if mci_open(path, alias):
            if loops == -1:
                mci_send_string(f'play {alias} repeat')
            else:
                mci_send_string(f'play {alias}')
            return
        # Ja MCI neizdodas — PowerShell/WMPlayer fallback
        try:
            subprocess.Popen([
                'powershell',
                '-NoProfile',
                '-Command',
                f"$p = New-Object -ComObject WMPlayer.OCX.7; $p.URL = '{path}'; $p.controls.play(); while ($p.playState -ne 1) {{ Start-Sleep -Milliseconds 100 }}"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return

    sound = load_sound_asset(filename)
    if sound:
        try:
            sound.play(loops=loops)
        except Exception:
            pass


def play_music(filename, loops=-1):
    """Atskaņo fona mūziku. Ja tā pati dziesma jau skan, neko nedara."""
    global CURRENT_MUSIC
    if not SOUND_ENABLED:
        return
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return

    if AUDIO_BACKEND == 'mci':
        alias = 'music'
        if CURRENT_MUSIC == filename:
            if loops == -1:
                mci_send_string(f'play {alias} repeat')
            else:
                mci_send_string(f'play {alias}')
            return
        if not mci_open(path, alias):
            return
        if loops == -1:
            mci_send_string(f'play {alias} repeat')
        else:
            mci_send_string(f'play {alias}')
        CURRENT_MUSIC = filename
        return

    try:
        if CURRENT_MUSIC == filename and _pygame.mixer.music.get_busy():
            return
        _pygame.mixer.music.load(path)
        _pygame.mixer.music.play(loops=loops)
        CURRENT_MUSIC = filename
    except Exception:
        pass


def stop_music():
    """Aptur pašreizējo fona mūziku."""
    global CURRENT_MUSIC
    if not SOUND_ENABLED:
        return
    if AUDIO_BACKEND == 'mci':
        mci_send_string('stop music')
        mci_send_string('close music')
        CURRENT_MUSIC = None
        return
    try:
        _pygame.mixer.music.stop()
    except Exception:
        pass
    CURRENT_MUSIC = None
