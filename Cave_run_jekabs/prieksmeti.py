"""
prieksmeti.py — Priekšmetu (inventāra) sistēma.

Šajā failā ir visas funkcijas, kas saistītas ar priekšmetu
izmantošanu, inventāra attēlošanu, kataloga pārlūkošanu
un priekšmetu izkritīšanu pēc cīņas.
"""

import os
import random
import time

from iestatijumi import (
    ITEMS, ITEMS_DIR, ITEM_ORDER, ITEM_ALIASES, LORE_NOTES,
    ATTACK_POTION_KEY, EXTRA_LIFE_KEY, TELEPORT_KEY, FLASHBANG_KEY,
    RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, WHITE, DIM,
)
from terminals import (
    get_terminal_width, center_text, center_prompt,
    color_text, print_centered, clear_screen,
)
from skanas import play_sound
from grafika import render_ascii_art
from boss import is_boss_room


# ============================================================
# Priekšmetu palīgfunkcijas
# ============================================================

def get_item_count(player, item_key):
    """Atgriež, cik vienību spēlētājam ir no norādītā priekšmeta."""
    return player.get('items', {}).get(item_key, 0)


def get_item_display_name(item_key):
    """Atgriež priekšmeta rādīšanas nosaukumu."""
    return ITEMS.get(item_key, {}).get('name', item_key)


def load_item_art(item_key):
    """Ielādē priekšmeta ASCII mākslu no Items mapes."""
    info = ITEMS.get(item_key, {})
    art_path = os.path.join(ITEMS_DIR, info.get('art_file', ''))
    try:
        with open(art_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'Nav mākslas priekš {info.get("name", item_key)}'


# ============================================================
# Priekšmetu izmantošanas funkcijas
# ============================================================

def use_flashbang(player, monster):
    """Izmanto 404 Flashbang — samazina pretinieka precizitāti un var likt izlaist gājienus."""
    count = get_item_count(player, FLASHBANG_KEY)
    if count <= 0:
        print_centered(color_text(f"Nav {ITEMS[FLASHBANG_KEY]['name']}.", RED, bold=True))
        return False

    player['items'][FLASHBANG_KEY] -= 1
    play_sound('404flash.mp3')
    print_centered(color_text("[!] 404 ERROR: Enemy's target coordinates not found!", YELLOW, bold=True))
    monster['accuracy'] = 0.4
    monster['accuracy_duration'] = 2
    print_centered(color_text("Enemy accuracy dropped severely for 2 turns.", MAGENTA))

    # 80% iespēja, ka pretinieks tiek satricināts
    if random.random() < 0.8:
        monster['flinch'] = 2
        print_centered(color_text("Enemy flinched and will skip its turn for 2 rounds!", MAGENTA, bold=True))
    else:
        print_centered(color_text("Enemy resisted the flinch but is still disoriented.", YELLOW))

    # 5% iespēja, ka flashbang ietekmē arī spēlētāju
    if random.random() < 0.05:
        player['blind_turns'] = 2
        player['accuracy'] = 0.7
        print_centered(color_text("Tu esi mazliet apmaldījies un tava redze pasliktinās!", RED, bold=True))
    return True


def use_attack_potion(player):
    """Izmanto Attack Potion — piešķir uzbrukuma bonusu nākamajam gājienam."""
    count = get_item_count(player, ATTACK_POTION_KEY)
    if count <= 0:
        print_centered(color_text("Nav Attack Potion tavā inventārā.", RED, bold=True))
        return False
    player['items'][ATTACK_POTION_KEY] -= 1
    player['attack_potion_turns'] = 1
    print_centered(color_text("Tu uzpildi savu ieroču spēku — nākamā istaba būs mēreni vieglāka!", MAGENTA, bold=True))
    play_sound('potions.mp3')
    return True


def use_extra_life(player):
    """Izmanto Extra Life — atjauno 50% no maksimālā HP."""
    count = get_item_count(player, EXTRA_LIFE_KEY)
    if count <= 0:
        print_centered(color_text("Nav Extra Life tavā inventārā.", RED, bold=True))
        return False
    player['items'][EXTRA_LIFE_KEY] -= 1
    heal_amount = max(1, int(player['max_hp'] * 0.5))
    previous_hp = player['hp']
    player['hp'] = min(player['max_hp'], player['hp'] + heal_amount)
    print_centered(color_text(f"Extra Life atjaunoja {player['hp'] - previous_hp} HP!", GREEN, bold=True))
    play_sound('potions.mp3')
    return True


def use_teleport(player, monster=None):
    """Izmanto Potion of Teleportion — pārvietojas uz nākamo istabu, izlaižot cīņu.
    Nedarbojas bosa istabās vai pret The Void."""
    count = get_item_count(player, TELEPORT_KEY)
    if count <= 0:
        print_centered(color_text("Nav Potion of Teleportion tavā inventārā.", RED, bold=True))
        return False
    cur_room = player.get('room_number', 1)
    # Aizliegt teleportāciju bosa istabā
    if is_boss_room(cur_room):
        print_centered(color_text('Teleportāciju nevar izmantot bosa istabā.', RED, bold=True))
        return False
    # Aizliegt teleportāciju pret The Void
    if monster is not None and str(monster.get('name', '')).strip().lower() == 'the void':
        print_centered(color_text('Teleportāciju nevar izmantot pret The Void.', RED, bold=True))
        return False
    player['items'][TELEPORT_KEY] -= 1
    play_sound('potions.mp3')
    # Pārvietot spēlētāju vienu istabu uz priekšu
    player['room_number'] = cur_room + 1
    if monster is not None:
        monster['hp'] = 0
        print_centered(color_text('Teleportācija izdevās! Tu pārvietojies uz nākamo istabu un monstrs pazuda.', CYAN, bold=True))
    else:
        print_centered(color_text('Tu izteleportējies uz nākamo istabu!', CYAN, bold=True))
    return True


# ============================================================
# Priekšmetu detalizēts skats un katalogs
# ============================================================

def show_item_detail(player, item_key, in_combat=False, monster=None):
    """Parāda detalizētu priekšmeta aprakstu ar mākslu un ļauj to izmantot."""
    clear_screen()
    item = ITEMS[item_key]
    print_centered(color_text(item['name'], YELLOW, bold=True))
    print_centered(color_text(item['description'], WHITE))
    print()
    print(render_ascii_art(load_item_art(item_key), max_width=min(get_terminal_width(), 60)))
    print()
    count = get_item_count(player, item_key)

    if count <= 0:
        print_centered(color_text("Nav šo priekšmetu inventārā.", RED, bold=True))
        print(center_text("Nospied Enter, lai atgrieztos."))
        input(center_prompt(''))
        return None

    # Flashbang var izmantot tikai kaujā
    if item_key == FLASHBANG_KEY and not in_combat:
        print_centered(color_text("Šo priekšmetu var izmantot tikai kaujā.", RED, bold=True))
        print(center_text("Nospied Enter, lai atgrieztos."))
        input(center_prompt(''))
        return None

    if item_key == ATTACK_POTION_KEY:
        if use_attack_potion(player):
            print(center_text("Nospied Enter, lai atgrieztos."))
            input(center_prompt(''))
            return 'used'
    elif item_key == EXTRA_LIFE_KEY:
        if use_extra_life(player):
            print(center_text("Nospied Enter, lai atgrieztos."))
            input(center_prompt(''))
            return 'used'
    elif item_key == TELEPORT_KEY:
        if not in_combat:
            print_centered(color_text("Potion of Teleportion var izmantot tikai kaujā.", RED, bold=True))
            print(center_text("Nospied Enter, lai atgrieztos."))
            input(center_prompt(''))
        else:
            if use_teleport(player, monster):
                print(center_text("Nospied Enter, lai turpinātu."))
                input(center_prompt(''))
                return 'teleported'
            else:
                print(center_text("Teleportācija neizdevās."))
                input(center_prompt(''))
    elif item_key == FLASHBANG_KEY:
        if in_combat:
            if use_flashbang(player, monster):
                print(center_text("Nospied Enter, lai turpinātu."))
                input(center_prompt(''))
                return 'used'
        else:
            print_centered(color_text("Šis priekšmets var tikt izmantots tikai kaujā.", RED, bold=True))
            print(center_text("Nospied Enter, lai atgrieztos."))
            input(center_prompt(''))
    return None


def show_items_catalog(player, in_combat=False, monster=None):
    """Parāda priekšmetu katalogu — spēlētājs var apskatīt un izmantot priekšmetus.
    Importē show_notes_archive no piezimes moduļa (novēršot cikliskus importus)."""
    from piezimes import show_notes_archive

    while True:
        clear_screen()
        print_centered(color_text('=== PRIEKŠMETU KATALOGS ===', YELLOW, bold=True))
        print()
        for index, item_key in enumerate(ITEM_ORDER, start=1):
            item = ITEMS[item_key]
            count = get_item_count(player, item_key)
            label = f"{index}. {item['name']} ({count} vienības)"
            print_centered(color_text(label, CYAN if count > 0 else RED))
            print_centered(color_text(f"   {item['description']}", DIM))
            print()
        note_count = player.get('notes_found', 0)
        print_centered(color_text(f"notes - Piezīmes ({note_count}/{len(LORE_NOTES)})", MAGENTA, bold=True))
        print_centered(color_text('   Atvērt atrasto piezīmju arhīvu un izlasīt tās vēlreiz.', DIM))
        print()
        print_centered(color_text("Ievadi numuru, priekšmeta nosaukumu vai 'notes'.", WHITE))
        print_centered(color_text("Raksti 'back' vai 'atpakaļ' lai atgrieztos.", DIM))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if choice in ('back', 'atpakaļ', 'atpakal'):
            return None
        if choice in ('notes', 'note', 'piezīmes', 'piezimes'):
            show_notes_archive(player)
            if in_combat:
                return None
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(ITEM_ORDER):
            item_key = ITEM_ORDER[int(choice) - 1]
        else:
            item_key = ITEM_ALIASES.get(choice)
        if not item_key or item_key not in ITEMS:
            print_centered(color_text('Nepareiza izvēle! Mēģini vēlreiz.', RED))
            time.sleep(1)
            continue
        result = show_item_detail(player, item_key, in_combat=in_combat, monster=monster)
        if result == 'teleported':
            return 'teleported'
        if result == 'used':
            return 'used'
        if in_combat:
            return None


# ============================================================
# Priekšmetu izkritīšana pēc cīņas
# ============================================================

def award_item_drops(player):
    """Nejauši piešķir priekšmetus spēlētājam pēc uzvaras cīņā."""
    for item_key, info in ITEMS.items():
        if random.random() < info.get('drop_chance', 0):
            player['items'][item_key] = player['items'].get(item_key, 0) + 1
            print_centered(color_text(
                f"{info['name']} nomesta! Tev tagad ir {player['items'][item_key]}.", CYAN
            ))
            time.sleep(1)


# ============================================================
# Inventāra pārskata attēlošana
# ============================================================

def show_inventory_status(player):
    """Parāda īsu inventāra pārskatu ar visiem priekšmetiem un piezīmju skaitu."""
    print_centered(color_text('=== INVENTĀRS ===', YELLOW, bold=True))
    for item_key in ITEM_ORDER:
        count = get_item_count(player, item_key)
        name = ITEMS[item_key]['name']
        description = ITEMS[item_key]['description']
        if count > 0:
            print_centered(color_text(f"{name}: {count} vienības", CYAN, bold=True))
            print_centered(color_text(f"   {description}", DIM))
        else:
            print_centered(color_text(f"{name}: 0 vienības", RED, bold=True))
            print_centered(color_text(f"   {description}", DIM))
    note_count = player.get('notes_found', 0)
    print_centered(color_text(f"Piezīmes: {note_count}/{len(LORE_NOTES)}", MAGENTA, bold=True))
    print()


# ============================================================
# Cīņas darbību izvēlne (action menu)
# ============================================================

def print_action_menu(player):
    """Attēlo formatētu cīņas darbību izvēlni ar priekšmetu skaitītājiem."""
    menu_width = min(80, max(50, get_terminal_width() - 16))
    top = '╔' + '═' * (menu_width - 2) + '╗'
    sep = '╟' + '─' * (menu_width - 2) + '╢'
    bot = '╚' + '═' * (menu_width - 2) + '╝'

    print()
    print_centered(color_text('★  TAVAS DARBĪBAS  ★', CYAN, bold=True))
    print_centered(top)
    print_centered(color_text(' attack ', GREEN, bold=True) + color_text(' - Uzbrukt pretiniekam', WHITE))
    print_centered(color_text('   ⚔ Spēcīgs sitiens, lai sagrautu pretinieku.', DIM))
    print_centered(sep)
    print_centered(color_text(' items ', BLUE, bold=True) + color_text(' - Atvērt inventāru un izmantot priekšmetus', WHITE))

    # Attēlot priekšmetu daudzumus
    item_count = sum(player.get('items', {}).values())
    if item_count > 0:
        item_lines = []
        for key in ITEM_ORDER:
            cnt = get_item_count(player, key)
            if cnt > 0:
                item_lines.append(f" {get_item_display_name(key)}: {cnt} vienības")
        if item_lines:
            for l in item_lines:
                print_centered(color_text('   ' + l, DIM))
    print_centered(color_text('   ✨ Izmanto priekšmetus, lai iegūtu pārsvaru kaujā.', DIM))
    print_centered(sep)
    print_centered(color_text(' quit ', RED, bold=True) + color_text(' - Pamest cīņu un spēli', WHITE))
    print_centered(color_text('   ⛔ Pamet kauju un atgriezies galvenajā izvēlnē.', DIM))
    print_centered(bot)
    print()
