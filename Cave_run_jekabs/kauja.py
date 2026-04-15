"""
kauja.py — Cīņas sistēma un līmeņa paaugstināšana.

Šajā failā ir galvenā cīņas cilpa (run_combat),
kā arī līmeņa paaugstināšanas (level_up) funkcija.
"""

import random
import time

from iestatijumi import (
    RED, GREEN, YELLOW, MAGENTA, CYAN, DIM,
)
from terminals import (
    get_terminal_width, center_text, center_prompt,
    color_text, print_centered, clear_screen,
)
from skanas import play_sound, play_music, stop_music
from grafika import display_hp_bar, render_ascii_art
from prieksmeti import show_items_catalog, print_action_menu, award_item_drops
from piezimes import maybe_drop_lore_note
from bojajumi import final_damage
from boss import boss_special_action


# ============================================================
# Cīņas cilpa — spēlētājs pret monstru
# ============================================================

def run_combat(player, monster):
    """Izpilda pilnu cīņu starp spēlētāju un monstru.
    Atgriež True ja spēlētājs uzvarēja, False ja zaudēja,
    vai 'teleported' ja izmantoja teleportāciju."""
    defending = False

    while player['hp'] > 0 and monster['hp'] > 0:
        clear_screen()
        print_centered(f"--- Cīņa ar {monster['name']} ---")
        display_hp_bar(player['hp'], player['max_hp'], "Tavs HP", centered=True)
        print_centered(f"Spēks: {player['str']} | Aizsardzība: {player.get('defense', 0)}")
        display_hp_bar(monster['hp'], monster['max_hp'], f"{monster['name']} HP", centered=True)
        print_centered(color_text(f"Uzbrukums: {monster['attack']}", MAGENTA, bold=True))
        print(render_ascii_art(monster['art']))
        print_action_menu(player)
        print_centered(color_text('Tava izvēle:', GREEN, bold=True))
        action = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        # --- Spēlētāja gājiens ---
        if action == "attack":
            # Pārbaudīt, vai spēlētājs ir apmaldīts (accuracy < 1.0)
            if player.get('accuracy', 1.0) < 1.0 and random.random() > player.get('accuracy', 1.0):
                print_centered(color_text("Tu palaidi garām, jo tevi apžilbināja informācijas mākoņi!", RED))
            else:
                attack_bonus = 5 if player.get('attack_potion_turns', 0) > 0 else 0
                dmg, crit = final_damage(player['str'] + attack_bonus, monster['defense'])
                monster['hp'] -= dmg
                msg = f"Tu uzbruki un nodarīji {dmg} damage"
                if crit:
                    msg += " (kritiskais sitiens!)"
                if attack_bonus > 0:
                    msg += " (Attack Potion bonus!)"
                print_centered(color_text(msg, GREEN))
                play_sound('attack.mp3')
            if player.get('attack_potion_turns', 0) > 0:
                print_centered(color_text('Attack Potion efektu joprojām izmanto kaujas laikā.', DIM))
            if player.get('blind_turns', 0) > 0:
                player['blind_turns'] -= 1
                if player['blind_turns'] == 0:
                    player['accuracy'] = 1.0
                    print_centered(color_text("Tava redze atgriežas normālā stāvoklī.", GREEN))

        elif action == "defense":
            defending = True
            print_centered(color_text("Tu sagatavojies aizsardzībai.", YELLOW))

        elif action in ("item", "items"):
            result = show_items_catalog(player, in_combat=True, monster=monster)
            if result == 'used':
                time.sleep(1)
                continue
            if result == 'teleported':
                return 'teleported'
            print_centered(color_text("Atgriežamies pie kaujas izvēles.", DIM))
            time.sleep(1)
            continue

        elif action in ("quit", "iziet"):
            print_centered(color_text("Tu izlēmi iziet no spēles.", RED, bold=True))
            player['hp'] = 0
            return False

        else:
            print_centered(color_text("Nepareiza izvēle! Pamēģini vēlreiz.", RED))
            time.sleep(1)
            continue

        time.sleep(1)

        # --- Monstru gājiens ---
        if monster['hp'] > 0:
            def_mod = player.get('defense', 0)
            if defending:
                def_mod += 5  # Aizsardzības bonuss
                defending = False

            if monster.get('is_boss'):
                # Bosa speciālā darbība
                action_result = boss_special_action(monster, player)
                if action_result.get('text'):
                    print_centered(color_text(action_result['text'], MAGENTA, bold=True))

                if action_result['type'] in ('attack', 'special'):
                    dmg = int(action_result.get('value', 0))
                    player['hp'] -= dmg
                    print_centered(color_text(f"{monster['name']} nodarīja {dmg} damage.", RED, bold=True))
                    play_sound('enemy_hit.mp3')
                elif action_result['type'] == 'defend':
                    buff = int(action_result.get('value', 0))
                    monster['defense'] = monster.get('defense', 0) + buff
                    print_centered(color_text(
                        f"{monster['name']} aizsardzība pieauga par {buff} (pagaidu).", YELLOW
                    ))
                time.sleep(1)
            else:
                # Parastā monstra gājiens
                if monster.get('flinch', 0) > 0:
                    print_centered(color_text(
                        f"{monster['name']} flinched and skipped its turn!", MAGENTA
                    ))
                    monster['flinch'] -= 1
                    if monster['flinch'] == 0:
                        print_centered(color_text(
                            f"{monster['name']} recovers from the confusion.", GREEN
                        ))
                    time.sleep(1)
                else:
                    if (monster.get('accuracy', 1.0) < 1.0
                            and random.random() > monster.get('accuracy', 1.0)):
                        print_centered(color_text(
                            f"{monster['name']} failed to find your position and missed!", MAGENTA
                        ))
                    else:
                        dmg, crit = final_damage(monster['attack'], def_mod)
                        player['hp'] -= dmg
                        msg = f"{monster['name']} uzbruka un nodarīja {dmg} damage"
                        if crit:
                            msg += " (kritiskais sitiens!)"
                        print_centered(color_text(msg, RED))
                        play_sound('enemy_hit.mp3')
                    if monster.get('accuracy_duration', 0) > 0:
                        monster['accuracy_duration'] -= 1
                        if monster['accuracy_duration'] == 0:
                            monster['accuracy'] = 1.0
                            print_centered(color_text(
                                f"{monster['name']} regains its aim.", GREEN
                            ))
                    time.sleep(1)

    # --- Cīņas beigas ---
    if player['hp'] > 0:
        if player.get('attack_potion_turns', 0) > 0:
            player['attack_potion_turns'] = 0
            print_centered(color_text('Tava Attack Potion spēka ietekme ir beigusies.', DIM))
        print_centered(color_text(f"\nTu uzvareji {monster['name']}!", GREEN, bold=True))
        player['xp'] += monster['xp_reward']
        print_centered(color_text(
            f"Tu ieguvi {monster['xp_reward']} XP. Kopā XP: {player['xp']}", CYAN
        ))
        award_item_drops(player)
        maybe_drop_lore_note(player, monster)
        return True
    else:
        print_centered(color_text(f"\nTu zaudēji pret {monster['name']}.", RED, bold=True))
        return False


# ============================================================
# Līmeņa paaugstināšana (Level Up)
# ============================================================

def level_up(player):
    """Paaugstina spēlētāja līmeni un ļauj sadalīt atribūtu punktus."""
    player["level"] += 1
    player["xp_needed"] += 40
    points = 3

    # Līmeņa paaugstināšanas baneris
    width = get_terminal_width()
    box_width = min(80, max(50, width - 10))
    border_top = '╔' + '═' * (box_width - 2) + '╗'
    border_mid = '╠' + '═' * (box_width - 2) + '╣'
    border_bot = '╚' + '═' * (box_width - 2) + '╝'

    print()
    print(center_text(color_text(border_top, CYAN)))
    print(center_text(color_text('★ ' + 'LEVEL UP!'.center(box_width - 6) + ' ★', YELLOW, bold=True)))
    print(center_text(color_text(border_mid, CYAN)))
    print(center_text(color_text(f"APSVEICAM! Tu sasniedzi {player['level']} līmeni!", GREEN, bold=True)))
    print(center_text(color_text('Tu vari turpināt ceļu pa alu vai iziet.', MAGENTA)))
    print(center_text(color_text(border_bot, CYAN)))
    print()
    play_sound('upgrade.mp3')
    time.sleep(2)

    print(center_text(color_text(f"Tev ir {points} atribūtu punkti ko sadalīt.", MAGENTA, bold=True)))
    print(center_text(color_text('Izvēlies rūpīgi — katrs punkts padara tevi spēcīgāku.', DIM)))
    print()

    while points > 0:
        print()
        print(center_text(color_text('Izvēlies, kur ieguldīt punktu:', CYAN, bold=True)))
        print(center_text(color_text('attack', YELLOW, bold=True) + color_text(' - Uzbrukums (+1)', MAGENTA)))
        print(center_text(color_text('defense', MAGENTA, bold=True) + color_text(' - Aizsardzība (+1)', MAGENTA)))
        print(center_text(color_text('max_health', CYAN, bold=True) + color_text(' - Maksimālais HP (+5)', MAGENTA)))
        print(center_text(color_text('quit', RED, bold=True) + color_text(' - Iziet no spēles', MAGENTA)))
        print(center_text(color_text(f'Atlikušie punkti: {points}', GREEN, bold=True)))
        print()

        print(center_text(color_text('Tava izvēle:', GREEN, bold=True)))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if choice == "attack":
            play_sound('atrb_up.mp3')
            player["str"] += 1
            points -= 1
            print("Uzbrukums palielināts!")
        elif choice == "defense":
            play_sound('atrb_up.mp3')
            player["defense"] += 1
            points -= 1
            print("Aizsardzība palielināta!")
        elif choice == "max_health":
            play_sound('atrb_up.mp3')
            player["max_hp"] += 5
            points -= 1
            print("Maksimālais HP palielināts!")
        elif choice in ("quit", "iziet"):
            print("Tu izlēmi iziet no spēles.")
            player['hp'] = 0
            return
        else:
            print("Nepareiza izvēle!")
