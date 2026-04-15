"""
stasts.py — Stāsta ievads un atmosfēras notikumi.

Šajā failā ir funkcijas stāsta lapu rādīšanai,
pilnekrāna uzvednes parādīšanai un biedējošo notikumu ģenerēšanai.
"""

import os
import sys
import time
import random

from iestatijumi import STORY_DIR, STORY_PAGES, RED, WHITE
from terminals import (
    get_terminal_size, get_terminal_width, strip_ansi,
    center_text, center_ascii, center_prompt,
    color_text, maximize_console, clear_screen, fade_in_lines,
)
from skanas import play_sound, play_music, stop_music


# ============================================================
# Stāsta mākslas ielāde no faila
# ============================================================

def load_story_art(filename):
    """Ielādē ASCII mākslu no Story mapes pēc faila nosaukuma."""
    art_path = os.path.join(STORY_DIR, filename)
    try:
        with open(art_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return f'[{filename} nav atrasts]'


# ============================================================
# Stāsta lapu rādīšana
# ============================================================

def show_story_page(page):
    """Parāda vienu stāsta lapu ar ASCII mākslu un teksta animāciju."""
    clear_screen()
    art = load_story_art(page['art_file'])
    print(center_ascii(art))
    print('\n')
    fade_in_lines(page['lines'])
    print('\n' + center_text('[Nospied Enter, lai turpinātu]'))
    input(center_prompt(''))


def show_fullscreen_prompt():
    """Parāda uzvedni, lai lietotājs ieslēgtu pilnekrāna režīmu."""
    maximize_console()
    clear_screen()
    term_size = get_terminal_size()
    blank_lines = max(0, (term_size.lines - 4) // 2)
    print('\n' * blank_lines)
    print(center_text('Make sure the game is FULL SCREEN.'))
    print(center_text('Press Enter to start.'))
    input(center_prompt(''))
    clear_screen()


# ============================================================
# Stāsta ievada secība
# ============================================================

def show_story_intro():
    """Parāda pilnu stāsta ievadu — visas lapas secīgi, pēc tam atskaņo skaņu."""
    stop_music()
    play_music('before_epic_intro.mp3', loops=-1)
    show_fullscreen_prompt()
    for page in STORY_PAGES:
        show_story_page(page)
    stop_music()
    play_sound('boomsound.mp3')
    clear_screen()


# ============================================================
# Biedējošais notikums (pēc bosa uzvaras)
# ============================================================

def show_scary_event():
    """Parāda biedējošu starpscēnu ar ziņojumu un skaņu efektiem."""
    stop_music()
    clear_screen()
    play_music('messages.mp3', loops=-1)

    # Izvēlēties nejaušu biedējošu ziņojumu
    messages = [
        "You feel an evil presence watching you..",
        "You feel vibrations from deep below...",
        "You feel a quaking from deep underground...",
        "Impending doom approaches...",
    ]
    text = random.choice(messages)

    width = get_terminal_width()
    blank_lines = max(0, (get_terminal_size().lines - 6) // 2)
    print('\n' * blank_lines)

    # Animēt tekstu pa vienam simbolam
    for i in range(1, len(text) + 1):
        fragment = center_text(text[:i])
        padding = max(0, width - len(strip_ansi(fragment)))
        sys.stdout.write(fragment + ' ' * padding + '\r')
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write('\n\n')
    sys.stdout.flush()

    time.sleep(1.5)
    print(center_text(color_text('The shadows are closing in...', RED, bold=True)))
    time.sleep(1.5)
    print(center_text(color_text('Nospied Enter, lai turpinātu.', WHITE, bold=True)))
    input(center_prompt(''))
    stop_music()
    clear_screen()
