"""
beigu_boss.py — Beigu bosa (The Void / Tukšums) cīņas sistēma.

Šajā failā ir visa loģika, kas saistīta ar beigu bosa cīņu —
dialogi, fāzu pārejas, cīņas cilpa un uzvara/zaudējums.
"""

import os
import sys
import random
import time

from iestatijumi import (
    FINAL_BOSS_DIR, FINAL_BOSS_ARTS,
    RED, GREEN, YELLOW, CYAN, MAGENTA, WHITE, DIM,
)
from terminals import (
    get_terminal_width, center_text, center_prompt,
    color_text, print_centered, clear_screen, center_ascii,
)
from skanas import play_sound, play_music, stop_music
from grafika import render_ascii_art, display_hp_bar
from prieksmeti import show_items_catalog, print_action_menu
from bojajumi import final_damage
from stasts import load_story_art


# ============================================================
# Beigu bosa mākslas ielāde un renderēšana
# ============================================================

def load_final_boss_art(filename):
    """Ielādē beigu bosa ASCII mākslu no final_boss_fight mapes."""
    art_path = os.path.join(FINAL_BOSS_DIR, filename)
    try:
        with open(art_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'Nav mākslas priekš {filename}'


def render_final_boss_art(phase):
    """Renderē beigu bosa mākslu atbilstoši pašreizējai fāzei."""
    filename = FINAL_BOSS_ARTS.get(phase, 'standing_up.txt')
    return render_ascii_art(
        load_final_boss_art(filename),
        max_width=min(get_terminal_width(), 90),
        allow_expand=True,
    )


# ============================================================
# Beigu bosa dialoga animācija
# ============================================================

def final_boss_dialogue(lines, delay=0.06):
    """Parāda beigu bosa dialoga rindas ar teksta animāciju."""
    clear_screen()
    print('\n' * 2)
    for line in lines:
        display = ''
        for ch in line:
            display += ch
            sys.stdout.write(center_text(display) + '\r')
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(0.7)
    print()
    time.sleep(1)


# ============================================================
# Beigu bosa cīņas cilpa
# ============================================================

def run_final_boss(player):
    """Izpilda pilnu beigu bosa (The Void) cīņu ar fāzu pārejām.
    Ja spēlētājs jau ir uzvarējis, nedara neko."""
    if player.get('final_boss_completed'):
        return

    stop_music()
    play_music('theme1.mp3', loops=-1)

    # --- Ievada dialogs ---
    clear_screen()
    final_boss_dialogue([
        'Kaut kas mostas visdziļākajā tumsā...',
        'Tu jūti, kā "Tukšums" sakustas zem zemes.\n',
        'Tukšums: "Vēl viens muļķis iedrošinās traucēt manu izsalkumu."\n',
        'Alas Skrējējs: "Es atnācu tevi iznīcināt, nevis bēgt."\n',
        'Tukšums: "Tad ieelpo pēdējo reizi, mirstīgais."',
    ])

    print(render_final_boss_art(1))
    print('\n')
    print(center_text(color_text('ŽĒLASTĪBA vai IZAICINĀJUMS?', YELLOW, bold=True)))
    print(center_text(color_text('Raksti "mercy" lai padotos, vai "challenge" lai cīnītos.', WHITE)))

    # --- Izvēle: padevēšanās vai cīņa ---
    while True:
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()
        if choice == 'mercy':
            stop_music()
            play_sound('mercy.mp3')
            clear_screen()
            print(center_text(color_text(
                'Tava pretestība izgaist, kamēr Tukšums aprij tavu cerību...', RED, bold=True
            )))
            time.sleep(2)
            print(center_text(color_text('SPĒLE BEIGUSIES', RED, bold=True)))
            time.sleep(2)
            sys.exit(0)
        elif choice == 'challenge':
            break
        else:
            print(center_text('Nepareiza izvēle! Izvēlies "mercy" vai "challenge".'))

    # --- Beigu bosa statistika ---
    boss = {
        'name': 'Tukšums',
        'hp': 400,
        'max_hp': 400,
        'attack': 45,
        'defense': 25,
        'phase': 1,
        'is_boss': True,
    }
    stop_music()
    play_music('theme2.mp3', loops=-1)
    time.sleep(1)

    # --- Cīņas cilpa ---
    defending = False
    while player['hp'] > 0 and boss['hp'] > 0:
        clear_screen()
        print_centered(color_text('!!! BEIGU BOSS: TUKŠUMS !!!', RED, bold=True))
        print(render_final_boss_art(boss['phase']))
        display_hp_bar(player['hp'], player['max_hp'], 'Tavs HP', centered=True)
        display_hp_bar(boss['hp'], boss['max_hp'], "Tukšuma HP", centered=True)
        print_centered(color_text(
            f"Spēks: {player['str']} | Aizsardzība: {player.get('defense', 0)}", MAGENTA
        ))
        print_action_menu(player)
        print_centered(color_text('Tava izvēle:', GREEN, bold=True))
        action = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        # --- Spēlētāja gājiens ---
        if action == 'attack':
            attack_bonus = 5 if player.get('attack_potion_turns', 0) > 0 else 0
            dmg, crit = final_damage(player['str'] + attack_bonus, boss['defense'])
            boss['hp'] -= dmg
            msg = f"Tu uzbruki un nodarīji {dmg} bojājumus"
            if crit:
                msg += " (kritiskais sitiens!)"
            if attack_bonus > 0:
                msg += " (Uzbrukuma dziras bonuss!)"
            print_centered(color_text(msg, GREEN))
            play_sound('attack.mp3')
            if player.get('attack_potion_turns', 0) > 0:
                print_centered(color_text('Uzbrukuma dziras efekts joprojām darbojas.', DIM))
            if player.get('blind_turns', 0) > 0:
                player['blind_turns'] -= 1
                if player['blind_turns'] == 0:
                    player['accuracy'] = 1.0
                    print_centered(color_text('Tava redze atgriežas normālā stāvoklī.', GREEN))
        elif action == 'defense':
            defending = True
            print_centered(color_text('Tu sagatavojies aizsardzībai.', YELLOW))
        elif action in ('item', 'items'):
            result = show_items_catalog(player, in_combat=True, monster=boss)
            if result == 'used':
                time.sleep(1)
                continue
            if result == 'teleported':
                print_centered(color_text('Šeit nav kur izvēlēties paslēpties.', RED))
                time.sleep(1)
                continue
            continue
        elif action in ('quit', 'iziet'):
            print_centered(color_text(
                'Tu izlēmi pamest kauju. Tukšums to patiesi novērtē.', RED, bold=True
            ))
            player['hp'] = 0
            break
        else:
            print_centered(color_text('Nepareiza izvēle! Pamēģini vēlreiz.', RED))
            time.sleep(1)
            continue

        time.sleep(1)

        # --- Fāzu pārejas ---
        if boss['hp'] <= 250 and boss['phase'] == 1:
            boss['phase'] = 2
            boss['max_hp'] += 170
            boss['attack'] += 25
            boss['defense'] += 20
            print_centered(color_text('Tukšums sakustas. Tas kļūst spēcīgāks!', RED, bold=True))
            time.sleep(2)
        elif boss['hp'] <= 120 and boss['phase'] == 2:
            boss['phase'] = 3
            boss['max_hp'] += 100
            boss['attack'] += 30
            boss['defense'] += 15
            print_centered(color_text('Tukšums saplēš realitāti. Saule pazūd!', RED, bold=True))
            time.sleep(2)

        # --- Bosa gājiens ---
        if boss['hp'] > 0:
            def_mod = player.get('defense', 0)
            if defending:
                def_mod += 6
                defending = False

            if boss['phase'] == 3 and random.random() < 0.35:
                # Speciālais 3. fāzes uzbrukums — caur aizsardzību
                carve = int(boss['attack'] * 1.4)
                player['hp'] -= carve
                print_centered(color_text(
                    f'Tukšums izplēš tavu bruņojumu un nodara {carve} bojājumus!', RED, bold=True
                ))
            else:
                dmg, crit = final_damage(boss['attack'], def_mod)
                player['hp'] -= dmg
                msg = f'Tukšums uzbruka un nodarīja {dmg} bojājumus'
                if crit:
                    msg += ' (kritiskais sitiens!)'
                print_centered(color_text(msg, RED))
            play_sound('void_attack.mp3')
            if player.get('hp', 0) <= 0:
                break
            time.sleep(1)

    # --- Cīņas beigas ---
    stop_music()
    if player['hp'] > 0 and boss['hp'] <= 0:
        # Uzvara!
        stop_music()
        play_music('victory.mp3', loops=-1)
        clear_screen()
        print_centered(color_text('Tukšums izjūk. Gaisma atgriežas.', GREEN, bold=True))
        time.sleep(2)
        print_centered(color_text('Tev izdevās. Bet atceries — Tukšums vienmēr gaida...', YELLOW))
        print_centered(color_text('Apsveicam! Tu esi uzvarējis Alas Pavēlnieku!', CYAN, bold=True))
        print()
        print(center_ascii(load_story_art('End_screen.txt')))
        player['final_boss_completed'] = True
        player['final_boss_chance'] = 0.0
        player['boss_wins'] = 0
        print()
        print_centered(color_text('Spied ENTER, lai izietu.', MAGENTA, bold=True))
        input()
        sys.exit(0)
    elif player['hp'] <= 0:
        print_centered(color_text('Tavs ceļš beidzās Tukšuma priekšā.', RED, bold=True))
        time.sleep(2)
    player = player or {}
