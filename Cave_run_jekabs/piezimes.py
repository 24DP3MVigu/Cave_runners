"""
piezimes.py — Tradicionālo piezīmju (lore notes) sistēma.

Šajā failā ir funkcijas piezīmju izkritīšanai, attēlošanai
un arhīva pārlūkošanai.
"""

import random
import time

from iestatijumi import (
    LORE_NOTES, LORE_DROP_BASE_CHANCE, LORE_DROP_ROOM_BONUS, LORE_DROP_MAX_CHANCE,
    CYAN, YELLOW, MAGENTA, RED, GREEN, WHITE, DIM,
)
from terminals import (
    get_terminal_width, center_text, center_prompt,
    color_text, print_centered, clear_screen,
)
from skanas import play_music, stop_music


# ============================================================
# Piezīmju palīgfunkcijas
# ============================================================

def get_next_lore_note(player):
    """Atgriež nākamo piezīmi, kas jāatrod, vai None, ja nav pieejama.
    Pārbauda spēlētāja progresu un minimālo istabas numuru."""
    found_count = player.get('notes_found', 0)
    if found_count >= len(LORE_NOTES):
        return None, found_count
    note = LORE_NOTES[found_count]
    if player.get('room_number', 1) < note['min_room']:
        return None, found_count
    return note, found_count


def get_collected_lore_notes(player):
    """Atgriež sarakstu ar visām līdz šim atrastajām piezīmēm."""
    found_count = max(0, min(player.get('notes_found', 0), len(LORE_NOTES)))
    return LORE_NOTES[:found_count]


# ============================================================
# Piezīmju attēlošana
# ============================================================

def show_lore_note(player, note, note_index, archive=False):
    """Parāda vienu piezīmi ar dekoratīvu rāmi, mūziku un teksta animāciju."""
    clear_screen()
    stop_music()
    play_music('messages.mp3', loops=-1)

    width = min(88, max(58, get_terminal_width() - 8))
    top = '╔' + '═' * (width - 2) + '╗'
    sep = '╠' + '═' * (width - 2) + '╣'
    bot = '╚' + '═' * (width - 2) + '╝'

    print()
    print(center_text(color_text(top, CYAN)))
    heading = 'ATRASTA PIEZĪME' if not archive else 'PIEZĪMJU ARHĪVS'
    print(center_text(color_text(heading.center(width - 2), YELLOW, bold=True)))
    print(center_text(color_text(sep, CYAN)))
    print(center_text(color_text(note['title'], MAGENTA, bold=True)))
    print(center_text(color_text(f"Autors: {note['author']}", DIM)))
    print()
    for line in note['text']:
        print(center_text(color_text(line, WHITE)))
        time.sleep(0.45)
    print()

    # Pēdējai piezīmei — papildu biedējošs teksts
    if note_index == len(LORE_NOTES) - 1:
        print(center_text(color_text('Papīrs ir mitrs. Pirms mirkļa tas vēl nebija.', RED, bold=True)))
    else:
        print(center_text(color_text(f"Piezīme {note_index + 1}/{len(LORE_NOTES)}", DIM)))

    print(center_text(color_text(bot, CYAN)))
    print()
    prompt_text = ('Nospied Enter, lai turpinātu.' if not archive
                   else 'Nospied Enter, lai atgrieztos pie piezīmēm.')
    print(center_text(color_text(prompt_text, GREEN, bold=True)))
    input(center_prompt(''))
    stop_music()
    play_music('main.mp3', loops=-1)


# ============================================================
# Piezīmju arhīvs
# ============================================================

def show_notes_archive(player):
    """Parāda visu atrasto piezīmju sarakstu ar iespēju tās izlasīt vēlreiz."""
    while True:
        clear_screen()
        collected_notes = get_collected_lore_notes(player)

        print_centered(color_text('=== PIEZĪMJU ARHĪVS ===', YELLOW, bold=True))
        print()

        if not collected_notes:
            print_centered(color_text('Tu vēl neesi atradis nevienu piezīmi.', RED, bold=True))
            print()
            print_centered(color_text('Nospied Enter, lai atgrieztos.', GREEN, bold=True))
            input(center_prompt(''))
            return

        for index, note in enumerate(collected_notes, start=1):
            print_centered(color_text(f"{index}. {note['title']}", MAGENTA, bold=True))
            print_centered(color_text(f"   {note['author']}", DIM))
            print()

        print_centered(color_text('Ievadi piezīmes numuru, lai to izlasītu vēlreiz.', WHITE))
        print_centered(color_text("Raksti 'back' vai 'atpakaļ', lai atgrieztos.", DIM))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if choice in ('back', 'atpakaļ', 'atpakal'):
            return
        if not choice.isdigit():
            print_centered(color_text('Nepareiza izvēle! Mēģini vēlreiz.', RED))
            time.sleep(1)
            continue

        note_number = int(choice)
        if not 1 <= note_number <= len(collected_notes):
            print_centered(color_text('Tādas piezīmes nav. Mēģini vēlreiz.', RED))
            time.sleep(1)
            continue

        show_lore_note(player, collected_notes[note_number - 1], note_number - 1, archive=True)


# ============================================================
# Piezīmju izkritīšana pēc cīņas
# ============================================================

def maybe_drop_lore_note(player, monster):
    """Pēc uzvaras pār parastu monstru — iespējams izkrīt nākamā piezīme.
    Bojām (bosiem) piezīmes neizkrīt."""
    if monster.get('is_boss'):
        return

    note, note_index = get_next_lore_note(player)
    if note is None:
        return

    # Aprēķināt izkritīšanas iespēju atkarībā no istabas numura
    drop_chance = min(
        LORE_DROP_MAX_CHANCE,
        LORE_DROP_BASE_CHANCE + player.get('room_number', 1) * LORE_DROP_ROOM_BONUS
    )
    if random.random() >= drop_chance:
        return

    player['notes_found'] = note_index + 1
    print_centered(color_text(
        'Tu atradi saplēstu piezīmi no cita alas skrējēja...', YELLOW, bold=True
    ))
    time.sleep(1.5)
    show_lore_note(player, note, note_index)
