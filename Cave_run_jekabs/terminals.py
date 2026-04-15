"""
terminals.py — Termināļa palīgfunkcijas.

Šajā failā ir visas funkcijas, kas saistītas ar teksta
formatēšanu, centrēšanu, krāsošanu un termināļa pārvaldīšanu.
"""

import os
import sys
import time
import shutil

from iestatijumi import (
    DEFAULT_TERMINAL_WIDTH, ANSI_ESCAPE,
    RESET, BOLD,
)


# ============================================================
# Termināļa izmēra noteikšana
# ============================================================

def get_terminal_size():
    """Atgriež termināļa izmēru (kolonnas, rindas)."""
    try:
        return shutil.get_terminal_size(fallback=(DEFAULT_TERMINAL_WIDTH, 24))
    except OSError:
        return os.terminal_size((DEFAULT_TERMINAL_WIDTH, 24))


def get_terminal_width():
    """Atgriež termināļa platumu kolonnās."""
    return get_terminal_size().columns


# ============================================================
# Teksta formatēšanas funkcijas
# ============================================================

def strip_ansi(text):
    """Noņem ANSI escape kodus no teksta (lai iegūtu redzamo garumu)."""
    return ANSI_ESCAPE.sub('', str(text))


def color_text(text, color, bold=False):
    """Iekrāso tekstu ar norādīto ANSI krāsu. Ja bold=True, pievieno treknrakstu."""
    if not color:
        return str(text)
    prefix = f"{BOLD if bold else ''}{color}"
    return f"{prefix}{text}{RESET}"


def center_prompt(text):
    """Centrē ievades uzvedni (prompt) termināļa vidū."""
    raw = str(text)
    visible = strip_ansi(raw)
    width = get_terminal_width()
    if len(visible) >= width:
        return raw
    pad_left = (width - len(visible)) // 2
    return ' ' * pad_left + raw


def center_text(text):
    """Centrē vienu teksta rindu termināļa vidū ar atstarpēm abās pusēs."""
    width = get_terminal_width()
    raw = str(text)
    visible = strip_ansi(raw)
    if len(visible) >= width:
        return raw
    pad_left = (width - len(visible)) // 2
    pad_right = width - len(visible) - pad_left
    return ' ' * pad_left + raw + ' ' * pad_right


def center_ascii(text):
    """Centrē vairāku rindu ASCII mākslu termināļa vidū."""
    lines = text.split('\n')
    centered_lines = []
    width = get_terminal_width()
    for line in lines:
        if not line:
            centered_lines.append(' ' * width)
            continue
        visible = strip_ansi(line)
        if len(visible) >= width:
            centered_lines.append(line)
            continue
        pad_left = (width - len(visible)) // 2
        centered_lines.append(' ' * pad_left + line)
    return '\n'.join(centered_lines)


def print_centered(text):
    """Izdrukā tekstu centrēti — katru rindu atsevišķi."""
    for line in str(text).splitlines():
        print(center_text(line))


# ============================================================
# Ekrāna pārvaldīšanas funkcijas
# ============================================================

def maximize_console():
    """Palielina konsoles logu līdz noteiktam izmēram."""
    if os.name == 'nt':
        os.system('mode con: cols=160 lines=48')
    else:
        sys.stdout.write('\x1b[8;48;160t')
        sys.stdout.flush()


def clear_screen():
    """Notīra konsoles ekrānu."""
    os.system('cls' if os.name == 'nt' else 'clear')


# ============================================================
# Teksta animācija
# ============================================================

def fade_in_lines(lines, char_delay=0.01, line_delay=0.15):
    """Animē teksta rindas — parāda katru simbolu pakāpeniski (fade-in efekts)."""
    for line in lines:
        display = ''
        for ch in line:
            display += ch
            print(center_text(display), end='\r', flush=True)
            time.sleep(char_delay)
        print(center_text(display))
        time.sleep(line_delay)
