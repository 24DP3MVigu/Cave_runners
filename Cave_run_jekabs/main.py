"""
main.py — Galvenais spēles ieejas punkts (Cave Runner).

Šis fails ir galvenais modulis, kas satur start_game() funkciju
un spēles galveno cilpu. Visa pārējā loģika ir sadalīta
atsevišķos failos ar latviskiem nosaukumiem.

Failu struktūra:
    iestatijumi.py  — Konstantes, ceļi, krāsu kodi, definīcijas
    terminals.py    — Termināļa palīgfunkcijas (centrēšana, formatēšana)
    skanas.py       — Skaņu un mūzikas sistēma
    grafika.py      — ASCII mākslas renderēšana un HP joslas
    bojajumi.py     — Bojājumu aprēķini
    monstri.py      — Monstru ielāde un ģenerēšana
    prieksmeti.py   — Priekšmetu (inventāra) sistēma
    piezimes.py     — Tradicionālo piezīmju sistēma
    kauja.py        — Cīņas cilpa un līmeņa paaugstināšana
    stasts.py       — Stāsta ievads un atmosfēras notikumi
    beigu_boss.py   — Beigu bosa (The Void) cīņa
    izvelne.py      — Galvenā izvēlne un noteikumi
    boss.py         — Bosu ģenerēšana un speciālās darbības
"""

import os
import sys
import time
import random
import traceback
import re
import shutil
import subprocess
import ctypes
from ctypes import wintypes

# --- UTF-8 kodējuma nodrošināšana konsolei ---
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# --- Importi no spēles moduļiem ---
from iestatijumi import (
    ATTACK_POTION_KEY, EXTRA_LIFE_KEY, TELEPORT_KEY, FLASHBANG_KEY,
    RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, WHITE, DIM,
    ITEMS, ITEMS_DIR, ITEM_ORDER, ITEM_ALIASES, LORE_NOTES,
    BASE_DIR, STORY_DIR, DEFAULT_TERMINAL_WIDTH, ANSI_ESCAPE,
)
from terminals import (
    get_terminal_width, center_text, center_prompt, center_ascii,
    color_text, print_centered, clear_screen, fade_in_lines,
    maximize_console,
)
from skanas import play_sound, play_music, stop_music
from grafika import render_ascii_art, display_hp_bar
from monstri import load_monster, MONSTERS
from prieksmeti import (
    show_items_catalog, get_item_count, get_item_display_name,
    load_item_art, use_flashbang, use_attack_potion, use_extra_life,
    use_teleport, show_item_detail, print_action_menu, award_item_drops,
)
from kauja import run_combat, level_up
from stasts import show_story_intro, show_scary_event
from beigu_boss import run_final_boss
from izvelne import show_main_menu
from boss import is_boss_room, generate_boss, boss_intro_text, boss_special_action
from piezimes import get_next_lore_note, get_collected_lore_notes, show_lore_note, show_notes_archive, maybe_drop_lore_note


def start_game():
    """Palaiž spēli — stāsta ievads, izvēlne, un galvenā spēles cilpa."""

    # --- Stāsta ievads un galvenā izvēlne ---
    show_story_intro()
    show_main_menu()
    play_music('main.mp3', loops=-1)

    # --- Spēlētāja sākotnējie parametri ---
    player = {
        "hp": 100,
        "max_hp": 100,
        "str": 10,                  #player stats
        "room_number": 1, # --- 4. Cīņu skaitītājs ---
        "level": 1,
        "xp": 0,
        "xp_needed": 20,
        "defense": 0,
        "accuracy": 1.0,
        "blind_turns": 0,
        "attack_potion_turns": 0,
        "boss_wins": 0,
        "final_boss_chance": 0.0,
        "final_boss_completed": False,
        "notes_found": 0,
        "items": {
            ATTACK_POTION_KEY: 0,
            EXTRA_LIFE_KEY: 0,
            TELEPORT_KEY: 0,
            FLASHBANG_KEY: 0,
        },
    }

    print("Spēle CAVE RUNNER sākas!")
    time.sleep(1)

    # --- Galvenais spēles cikls ---
    while player["hp"] > 0:
        clear_screen()

        # --- Bosa istabas pārbaude ---
        if is_boss_room(player["room_number"]):
            # Izvēlēties bosa veidni no LIELO BURTU nosaukumiem
            template = load_monster(player, boss=True)
            # Ģenerēt bosa statistiku
            generated = generate_boss(player, player["room_number"])
            # Apvienot ģenerēto ar veidnes vārdu un mākslu
            generated['name'] = template.get('name', generated.get('name'))
            generated['art'] = template.get('art', generated.get('art', f"Nav mākslas priekš {generated.get('name')}"))
            generated['max_hp'] = generated.get('hp', generated.get('max_hp', 0))
            generated['is_boss'] = True
            monster = generated

            # Bosa ievada baneris
            print('=' * get_terminal_width())
            print(center_text('!!! BOSS ENCOUNTER !!!'))
            print(center_text(boss_intro_text(monster)))
            print('=' * get_terminal_width())
            play_music(random.choice(['boss1.mp3', 'boss2.mp3', 'boss3.mp3']), loops=-1)
            time.sleep(1)

            won = run_combat(player, monster)
            stop_music()

            # Ja spēlētājs nomira kaujā
            if player.get('hp', 0) <= 0:
                print("Tu nomiri kaujā. Spēle beigusies.")
                break

            # Pēc bosa uzvaras — apsveikums un biedējošais notikums
            if won:
                player['boss_wins'] += 1
                if player['boss_wins'] == 1:
                    player['final_boss_chance'] = 0.01
                else:
                    player['final_boss_chance'] = min(1.0, player['final_boss_chance'] * 2)

                print('\n' + '=' * get_terminal_width())
                print(center_text('APSVEICAM! Tu pieveici Bosu!'))
                print(center_text('Tu vari turpināt ceļu pa alu vai iziet.'))
                print('=' * get_terminal_width() + '\n')
                time.sleep(2)

                show_scary_event()

                # Iespēja aktivizēt beigu bosa cīņu
                if not player.get('final_boss_completed', False):
                    chance_roll = random.random()
                    if chance_roll < player.get('final_boss_chance', 0.0):
                        print(center_text(color_text(
                            'A tear in the world opens... something ancient is stirring.', RED, bold=True
                        )))
                        time.sleep(2)
                        run_final_boss(player)
                        if player['hp'] <= 0:
                            break
                play_music('main.mp3', loops=-1)
        else:
            # --- Parastā istaba ---
            print(f"--- ISTABA NR. {player['room_number']} ---")
            monster = load_monster(player)
            print(f"Tu cīnies ar {monster['name']}!")
            print(render_ascii_art(monster['art']))
            time.sleep(1)
            combat_result = run_combat(player, monster)
            if combat_result == 'teleported':
                continue
            if not combat_result:
                break  # Spēlētājs zaudēja

        # --- Pēc-cīņas izvēlne ---
        # Pārbaudīt līmeņa paaugstināšanu
        while player['xp'] >= player['xp_needed']:
            level_up(player)

        print("\n")
        menu_width = min(72, max(50, get_terminal_width() - 20))
        top = '╔' + '═' * (menu_width - 2) + '╗'
        sep = '╟' + '─' * (menu_width - 2) + '╢'
        bot = '╚' + '═' * (menu_width - 2) + '╝'

        next_action = None
        while next_action is None:
            print_centered(color_text(top, CYAN))
            print_centered(color_text('★  KO DARĪSI TĀLĀK?  ★'.center(menu_width - 2), YELLOW, bold=True))
            print_centered(color_text(sep, CYAN))
            print_centered(color_text('1. Doties tālāk'.ljust(menu_width - 4), GREEN))
            if player['xp'] >= player['xp_needed']:
                print_centered(color_text('2. Uzlaboties (Upgrade)'.ljust(menu_width - 4), MAGENTA))
                print_centered(color_text('3. Iziet'.ljust(menu_width - 4), RED))
            else:
                print_centered(color_text('2. Iziet'.ljust(menu_width - 4), RED))
            print_centered(color_text('items - Apskatīt inventāru'.ljust(menu_width - 4), BLUE))
            print_centered(color_text(sep, CYAN))
            print_centered(color_text('Ievadi numuru vai "items".', WHITE, bold=True))
            print_centered(color_text('Tava izvēle:', GREEN, bold=True))
            print_centered(color_text(bot, CYAN))

            choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

            if choice == "1":
                next_action = 'continue'
            elif choice == "2" and player['xp'] >= player['xp_needed']:
                level_up(player)
                if player['hp'] <= 0:
                    next_action = 'exit'
                else:
                    continue
            elif choice == "2" and player['xp'] < player['xp_needed']:
                next_action = 'exit'
            elif choice == "3" and player['xp'] >= player['xp_needed']:
                next_action = 'exit'
            elif choice == 'items':
                result = show_items_catalog(player)
                if result == 'teleported':
                    next_action = 'teleported'
                else:
                    continue
            elif choice in ('void', 'tukšums', 'thevoid', 'summonvoid'):
                # Slepenā beigu bosa aktivizēšana
                print(center_text(color_text(
                    'Secret ritual activated... Tukšums answers.', RED, bold=True
                )))
                time.sleep(1.5)
                run_final_boss(player)
                if player['hp'] <= 0:
                    next_action = 'exit'
                else:
                    continue
            else:
                print(center_text("Nepareiza izvēle! Mēģini vēlreiz."))
                time.sleep(1)
                continue

        if next_action == 'exit':
            break
        if next_action == 'teleported':
            continue

        # Palielināt istabas numuru pēc izvēles
        player["room_number"] += 1
        print("\nTu dodies uz nākamo istabu...")
        time.sleep(1.5)

    # --- Spēle beigusies (Game Over) ---
    if player["hp"] <= 0:
        play_music('You_Died.mp3', loops=-1)
        clear_screen()
        gameover_path = os.path.join(os.path.dirname(__file__), '..', 'gameover.txt')
        try:
            with open(gameover_path, 'r', encoding='utf-8', errors='replace') as f:
                gameover_art = f.read()
            print(center_ascii(gameover_art))
        except Exception:
            print(center_text(color_text("GAME OVER", RED, bold=True)))

        while True:
            print(center_text("Vai vēlies spēlēt vēlreiz? (j/n)"))
            choice = input(center_prompt('> ')).strip().lower()
            if choice == 'j':
                start_game()
                return
            elif choice == 'n':
                print(center_text("Paldies par spēlēšanu!"))
                sys.exit(0)
            else:
                print(center_text("Nepareiza izvēle! Ievadi 'j' vai 'n'."))


# ============================================================
# Programmas ieejas punkts
# ============================================================

if __name__ == "__main__":
    try:
        start_game()
    except Exception:
        # Saglabāt avārijas žurnālu
        error_log_path = os.path.join(os.path.dirname(__file__), '..', 'game_crash.log')
        with open(error_log_path, 'a', encoding='utf-8') as log_file:
            log_file.write('=== Avārija konstatēta ===\n')
            log_file.write(traceback.format_exc())
            log_file.write('\n')
        print('Konstatēta avārija. Detaļas saglabātas game_crash.log failā.')
        print('Lūdzu nosūti šī faila saturu, ja spēle negaidīti aizveras.')