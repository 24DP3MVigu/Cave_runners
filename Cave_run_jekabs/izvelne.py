"""
izvelne.py — Galvenā izvēlne un spēles noteikumi.

Šajā failā ir galvenās izvēlnes attēlošana,
noteikumu ekrāns un navigācija starp tiem.
"""

import sys
import time

from iestatijumi import (
    CAVE_RUNNER_LOGO, START_BUTTON_ART, RULES_BUTTON_ART, QUIT_BUTTON_ART,
    YELLOW, GREEN, CYAN, MAGENTA, RED,
)
from terminals import (
    get_terminal_width, center_text, center_prompt,
    color_text, print_centered, clear_screen,
)
from skanas import stop_music
from grafika import render_ascii_art, render_side_by_side


# ============================================================
# Galvenā izvēlne
# ============================================================

def show_main_menu():
    """Parāda galveno izvēlni ar START, RULES un QUIT pogām.
    Gaida spēlētāja izvēli un atgriežas, kad izvēlēts 'start'."""
    stop_music()
    while True:
        clear_screen()
        print(render_ascii_art(CAVE_RUNNER_LOGO, allow_expand=True))
        print(render_side_by_side(START_BUTTON_ART, RULES_BUTTON_ART, QUIT_BUTTON_ART))
        print('\n')
        print_centered(color_text('Ievadi: start, rules vai quit', YELLOW, bold=True))
        print('\n' + '=' * get_terminal_width())
        print_centered(color_text('Tava izvēle:', GREEN, bold=True))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if choice == "start":
            return
        elif choice == "rules":
            show_rules()
        elif choice == "quit":
            print(center_text("Paldies par spēlēšanu!"))
            sys.exit(0)
        else:
            print(center_text("Nepareiza izvēle! Mēģini vēlreiz."))
            time.sleep(1)


# ============================================================
# Spēles noteikumu ekrāns
# ============================================================

def show_rules():
    """Parāda spēles noteikumus un gaida Enter, lai atgrieztos."""
    clear_screen()
    print(center_text(color_text('=== Spēles noteikumi ===', YELLOW, bold=True)))
    print('\n')
    print_centered('1. Tu esi alas skrējējs.')
    print_centered('2. Katrā istabā cīnies ar monstriem.')
    print_centered('3. Pēc uzvaras vari uzlabot spēku vai HP.')
    print_centered('4. Sasniedz 10. istabu, lai cīnītos ar bossu.')
    print_centered('5. Ja HP sasniedz 0, spēle beigusies.')
    print('\n')
    print(center_text('Nospied Enter, lai atgrieztos pie galvenās izvēlnes.'))
    input(center_prompt(''))
