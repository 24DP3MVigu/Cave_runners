import os
import time
import sys
import csv
import random
import re
from boss import is_boss_room, generate_boss, boss_intro_text, boss_special_action

DEFAULT_TERMINAL_WIDTH = 80
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

# Base directory for data files (ensures script works when run from any cwd)
BASE_DIR = os.path.dirname(__file__)

def get_terminal_size():
    try:
        return os.get_terminal_size()
    except OSError:
        return os.terminal_size((DEFAULT_TERMINAL_WIDTH, 24))


def get_terminal_width():
    return get_terminal_size().columns


def strip_ansi(text):
    return ANSI_ESCAPE.sub('', str(text))


def center_prompt(text):
    raw = str(text)
    visible = strip_ansi(raw)
    width = get_terminal_width()
    if len(visible) >= width:
        return raw
    pad_left = (width - len(visible)) // 2
    return ' ' * pad_left + raw


def center_text(text):
    width = get_terminal_width()
    raw = str(text)
    visible = strip_ansi(raw)
    if len(visible) >= width:
        return raw
    pad_left = (width - len(visible)) // 2
    pad_right = width - len(visible) - pad_left
    return ' ' * pad_left + raw + ' ' * pad_right


def center_ascii(text):
    lines = text.split('\n')
    centered_lines = []
    width = get_terminal_width()
    for line in lines:
        if line:
            centered_lines.append(line.center(width))
        else:
            centered_lines.append(' ' * width)
    return '\n'.join(centered_lines)


def print_centered(text):
    for line in str(text).splitlines():
        print(center_text(line))


ATTACK_POTION_KEY = 'attack_potion'
EXTRA_LIFE_KEY = 'extra_life'
TELEPORT_KEY = 'potion_teleportation'
FLASHBANG_KEY = '404_flashbang'

ITEMS_DIR = os.path.join(BASE_DIR, 'Items')

ITEMS = {
    ATTACK_POTION_KEY: {
        'name': 'Attack Potion',
        'description': 'Pievieno papildu spēku nākamajai istabai. Darbojas vienu cīņu.',
        'art_file': 'Attack_Potion.txt',
        'drop_chance': 0.40,
        'combat_usable': False,
        'outside_usable': True,
    },
    EXTRA_LIFE_KEY: {
        'name': 'Extra Life',
        'description': 'Atjauno 50% no Tava maksimālā HP uzreiz.',
        'art_file': 'Extra_Life.txt',
        'drop_chance': 0.40,
        'combat_usable': False,
        'outside_usable': True,
    },
    TELEPORT_KEY: {
        'name': 'Potion of Teleportion',
        'description': 'Izmet tevi cauri nākamajai istabai. Nav efekta pret bosa istabām.',
        'art_file': 'Potion_of_teleportion.txt',
        'drop_chance': 0.20,
        'combat_usable': False,
        'outside_usable': True,
    },
    FLASHBANG_KEY: {
        'name': '404 Flashbang',
        'description': 'Piespiež ienaidnieku palaist garām 2 gājienus un samazina tā precizitāti.',
        'art_file': 'flashbang.txt',
        'drop_chance': 0.45,
        'combat_usable': True,
        'outside_usable': False,
    },
}

ITEM_ORDER = [
    ATTACK_POTION_KEY,
    EXTRA_LIFE_KEY,
    TELEPORT_KEY,
    FLASHBANG_KEY,
]

ITEM_ALIASES = {
    'attack potion': ATTACK_POTION_KEY,
    'attack': ATTACK_POTION_KEY,
    'potion': ATTACK_POTION_KEY,
    'extra life': EXTRA_LIFE_KEY,
    'life': EXTRA_LIFE_KEY,
    'extra': EXTRA_LIFE_KEY,
    'teleport': TELEPORT_KEY,
    'teleportation': TELEPORT_KEY,
    'potion teleportation': TELEPORT_KEY,
    'flashbang': FLASHBANG_KEY,
    '404 flashbang': FLASHBANG_KEY,
    '404': FLASHBANG_KEY,
}


def color_text(text, color, bold=False):
    if not color:
        return str(text)
    prefix = f"{BOLD if bold else ''}{color}"
    return f"{prefix}{text}{RESET}"


def get_item_count(player, item_key):
    return player.get('items', {}).get(item_key, 0)


def get_item_display_name(item_key):
    return ITEMS.get(item_key, {}).get('name', item_key)


def load_item_art(item_key):
    info = ITEMS.get(item_key, {})
    art_path = os.path.join(ITEMS_DIR, info.get('art_file', ''))
    try:
        with open(art_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'No art for {info.get("name", item_key)}'


def print_action_menu(player=None):
    player = player or {}
    menu_width = min(80, max(50, get_terminal_width() - 16))
    top = '╔' + '═' * (menu_width - 2) + '╗'
    sep = '╟' + '─' * (menu_width - 2) + '╢'
    bot = '╚' + '═' * (menu_width - 2) + '╝'

    print()
    print_centered(color_text('★  IZVĒLIES DARĪBU  ★', CYAN, bold=True))
    print_centered(top)
    print_centered(color_text(' attack ', CYAN, bold=True) + color_text(' - Uzbrukt', WHITE))
    print_centered(color_text('   ⚔ Spēcīgs sitiens, lai sagrautu pretinieku.', DIM))
    print_centered(sep)
    print_centered(color_text(' defense ', MAGENTA, bold=True) + color_text(' - Aizsargāties', WHITE))
    print_centered(color_text('   🛡 Paaugstini bruņojumu un samazini iegūto damage.', DIM))
    print_centered(sep)
    print_centered(color_text(' item ', BLUE, bold=True) + color_text(' - Izmantot priekšmetu', WHITE))
    for item_key in ITEM_ORDER:
        count = get_item_count(player, item_key)
        print_centered(color_text(f"   {ITEMS[item_key]['name']}: {count} vienības", DIM))
    print_centered(color_text('   ✨ Izmanto priekšmetus, lai iegūtu pārsvaru kaujā.', DIM))
    print_centered(sep)
    print_centered(color_text(' quit ', RED, bold=True) + color_text(' - Iziet no spēles', WHITE))
    print_centered(color_text('   ⛔ Pamet kauju un atgriezies galvenajā izvēlnē.', DIM))
    print_centered(bot)
    print()


def show_inventory_status(player):
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
    print()


def use_flashbang(player, monster):
    count = get_item_count(player, FLASHBANG_KEY)
    if count <= 0:
        print_centered(color_text(f"Nav {ITEMS[FLASHBANG_KEY]['name']}.", RED, bold=True))
        return False

    player['items'][FLASHBANG_KEY] -= 1
    print_centered(color_text("[!] 404 ERROR: Enemy's target coordinates not found!", YELLOW, bold=True))
    monster['accuracy'] = 0.4
    monster['accuracy_duration'] = 2
    print_centered(color_text("Enemy accuracy dropped severely for 2 turns.", MAGENTA))

    if random.random() < 0.8:
        monster['flinch'] = 2
        print_centered(color_text("Enemy flinched and will skip its turn for 2 rounds!", MAGENTA, bold=True))
    else:
        print_centered(color_text("Enemy resisted the flinch but is still disoriented.", YELLOW))

    if random.random() < 0.05:
        player['blind_turns'] = 2
        player['accuracy'] = 0.7
        print_centered(color_text("Tu esi mazliet apmaldījies un tava redze pasliktinās!", RED, bold=True))
    return True


def use_attack_potion(player):
    count = get_item_count(player, ATTACK_POTION_KEY)
    if count <= 0:
        print_centered(color_text("Nav Attack Potion tavā inventārā.", RED, bold=True))
        return False
    player['items'][ATTACK_POTION_KEY] -= 1
    player['attack_potion_turns'] = 1
    print_centered(color_text("Tu uzpildi savu ieroču spēku — nākamā istaba būs mēreni vieglāka!", MAGENTA, bold=True))
    return True


def use_extra_life(player):
    count = get_item_count(player, EXTRA_LIFE_KEY)
    if count <= 0:
        print_centered(color_text("Nav Extra Life tavā inventārā.", RED, bold=True))
        return False
    player['items'][EXTRA_LIFE_KEY] -= 1
    heal_amount = max(1, int(player['max_hp'] * 0.5))
    previous_hp = player['hp']
    player['hp'] = min(player['max_hp'], player['hp'] + heal_amount)
    print_centered(color_text(f"Extra Life atjaunoja {player['hp'] - previous_hp} HP!", GREEN, bold=True))
    return True


def use_teleport(player):
    count = get_item_count(player, TELEPORT_KEY)
    if count <= 0:
        print_centered(color_text("Nav Potion of Teleportion tavā inventārā.", RED, bold=True))
        return False
    if is_boss_room(player['room_number']):
        print_centered(color_text("Potion of Teleportion nedarbojas bosa istabā.", RED, bold=True))
        return False
    player['items'][TELEPORT_KEY] -= 1
    player['room_number'] += 1
    print_centered(color_text("Tu izteleportējies uz nākamo istabu!", CYAN, bold=True))
    return True


def show_item_detail(player, item_key, in_combat=False, monster=None):
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
        if in_combat:
            print_centered(color_text("Potion of Teleportion nav izmantojama kaujā.", RED, bold=True))
            print(center_text("Nospied Enter, lai atgrieztos."))
            input(center_prompt(''))
        elif use_teleport(player):
            print(center_text("Nospied Enter, lai turpinātu."))
            input(center_prompt(''))
            return 'teleported'
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
        print_centered(color_text("Ievadi numuru vai priekšmeta nosaukumu, lai apskatītu/darbotos ar to.", WHITE))
        print_centered(color_text("Raksti 'back' vai 'atpakaļ' lai atgrieztos.", DIM))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()
        if choice in ('back', 'atpakaļ', 'atpakal'):
            return None
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


def award_item_drops(player):
    for item_key, info in ITEMS.items():
        if random.random() < info.get('drop_chance', 0):
            player['items'][item_key] = player['items'].get(item_key, 0) + 1
            print_centered(color_text(f"{info['name']} nomesta! Tev tagad ir {player['items'][item_key]}.", CYAN))
            time.sleep(1)


def scale_ascii_art(text, max_width=None, max_height=None, allow_expand=False):
    lines = text.splitlines()
    if not lines:
        return text

    lines = [line.rstrip('\n') for line in lines]
    orig_w = max(len(line) for line in lines)
    orig_h = len(lines)

    if orig_w == 0 or orig_h == 0:
        return text

    if max_width is None:
        max_width = get_terminal_width()
    if max_height is None:
        max_height = get_terminal_size().lines

    if allow_expand and max_width > orig_w and max_width >= orig_w * 1.3:
        expand_factor = int(max_width / orig_w)
        expand_factor = max(2, min(expand_factor, 3))
        scaled_lines = []
        for line in lines:
            expanded_line = ''.join(ch * expand_factor for ch in line)
            for _ in range(expand_factor):
                scaled_lines.append(expanded_line)
        return '\n'.join(scaled_lines)

    if orig_w <= max_width:
        return '\n'.join(lines)

    target_w = max(1, int(max_width))
    target_h = max(1, int(round(orig_h * target_w / orig_w)))
    scaled = []
    for row_index in range(target_h):
        src_row = min(orig_h - 1, int(row_index * orig_h / target_h))
        row = lines[src_row].ljust(orig_w)
        new_row_chars = []
        for col_index in range(target_w):
            src_col = min(orig_w - 1, int(col_index * orig_w / target_w))
            new_row_chars.append(row[src_col])
        scaled.append(''.join(new_row_chars))
    return '\n'.join(scaled)


def render_ascii_art(text, max_width=None, allow_expand=False):
    scaled = scale_ascii_art(text, max_width=max_width, allow_expand=allow_expand)
    return center_ascii(scaled)


def display_hp_bar(current, max_hp, label="HP", centered=False):
    percentage = current / max_hp if max_hp > 0 else 0
    bar_length = 20
    filled = int(percentage * bar_length)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    if percentage > 0.6:
        color = '\033[92m'  # green
    elif percentage > 0.3:
        color = '\033[93m'  # yellow
    else:
        color = '\033[91m'  # red
    
    reset = '\033[0m'
    line = f"{label}: {color}{bar}{reset} {current}/{max_hp}"
    if centered:
        print(line.center(get_terminal_width()))
    else:
        print(line)

# Damage calculation functions
def calculate_damage(attacker_attack, defender_defense):
    damage = attacker_attack - (defender_defense / 2)
    damage = max(1, int(damage))
    return damage

def calculate_critical(damage, crit_chance=0.15):
    if random.random() < crit_chance:
        return damage * 2, True
    return damage, False

def final_damage(attacker_attack, defender_defense):
    base_damage = calculate_damage(attacker_attack, defender_defense)
    dmg, crit = calculate_critical(base_damage)
    return dmg, crit

# Load monsters
MONSTERS = []
with open(os.path.join(os.path.dirname(__file__), 'monsters.csv'), 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        MONSTERS.append({
            'name': row['name'],
            'hp': int(row['hp']),
            'attack': int(row['attack']),
            'defense': int(row['defense']),
            'xp_reward': int(row['xp_reward'])
        })

def load_monster():
    monster = random.choice(MONSTERS).copy()  # Copy to avoid modifying original
    monster['max_hp'] = monster['hp']  # Store initial HP for bar display
monsters_csv = os.path.join(BASE_DIR, 'monsters.csv')
try:
    with open(monsters_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                MONSTERS.append({
                    'name': row['name'],
                    'hp': int(row['hp']),
                    'attack': int(row['attack']),
                    'defense': int(row['defense']),
                    'xp_reward': int(row['xp_reward'])
                })
            except Exception:
                # Skip malformed rows
                continue
except FileNotFoundError:
    print(f"Error: monsters.csv not found at {monsters_csv}")
    sys.exit(1)
except Exception as e:
    print(f"Error loading monsters.csv: {e}")
    sys.exit(1)

def load_monster(boss: bool = False):
    """Return a monster template.

    - If boss=True, select only monsters whose `name` is ALL CAPS (used for boss ASCII art).
    - If boss=False, select only monsters not in all caps.
    If no candidates found, fall back to the full list.
    """
    if boss:
        candidates = [m for m in MONSTERS if m.get('name', '').isupper()]
    else:
        candidates = [m for m in MONSTERS if not m.get('name', '').isupper()]

    if not candidates:
        candidates = MONSTERS

    monster = random.choice(candidates).copy()  # Copy to avoid modifying original
    monster['accuracy'] = 1.0
    monster['accuracy_duration'] = 0
    monster['flinch'] = 0
    monster['accuracy'] = 1.0
    monster['accuracy_duration'] = 0
    monster['flinch'] = 0
    # Load ASCII art if exists
    art_path = os.path.join(BASE_DIR, 'Monstri', monster['name'])
    try:
        with open(art_path, 'r', encoding='utf-8') as f:
            monster['art'] = f.read()
    except FileNotFoundError:
        monster['art'] = f'No ASCII art for {monster["name"]}'
    # Ensure a max_hp field for HP bar display
    monster['max_hp'] = monster.get('hp', 0)
    return monster

def level_up(player):
    player["level"] += 1
    player["xp_needed"] += 30  # Increase XP needed for next level
    points = 3

    # Big level-up banner with polished layout
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
    print(center_text(color_text('Tu vari turpināt ceļu pa alu vai iziet.', WHITE)))
    print(center_text(color_text(border_bot, CYAN)))
    print()
    time.sleep(2)

    print(center_text(color_text(f"Tev ir {points} atribūtu punkti ko sadalīt.", MAGENTA, bold=True)))
    print(center_text(color_text('Izvēlies rūpīgi — katrs punkts padara tevi spēcīgāku.', DIM)))
    print()

    while points > 0:
        print()
        print(center_text(color_text('Izvēlies, kur ieguldīt punktu:', CYAN, bold=True)))
        print(center_text(color_text('attack', YELLOW, bold=True) + color_text(' - Uzbrukums (+1)', WHITE)))
        print(center_text(color_text('defense', MAGENTA, bold=True) + color_text(' - Aizsardzība (+1)', WHITE)))
        print(center_text(color_text('max_health', BLUE, bold=True) + color_text(' - Maksimālais HP (+5)', WHITE)))
        print(center_text(color_text('quit', RED, bold=True) + color_text(' - Iziet no spēles', WHITE)))
        print(center_text(color_text(f'Atlikušie punkti: {points}', GREEN, bold=True)))
        print()

        print(center_text(color_text('Tava izvēle:', GREEN, bold=True)))
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if choice == "attack":
            player["str"] += 1
            points -= 1
            print("Uzbrukums palielināts!")
        elif choice == "defense":
            player["defense"] += 1
            points -= 1
            print("Aizsardzība palielināta!")
        elif choice == "max_health":
            player["max_hp"] += 5
            player["hp"] = player["max_hp"]  # Heal to full
            points -= 1
            print("Maksimālais HP palielināts!")
        elif choice == "quit" or choice == "iziet":
            print("Tu izlēmi iziet no spēles.")
            player['hp'] = 0  # Force game over
            return
        else:
            print("Nepareiza izvēle!")

def run_combat(player, monster):
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
        
        if action == "attack":
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
        
        elif action == "item":
            result = show_items_catalog(player, in_combat=True, monster=monster)
            if result == 'used':
                time.sleep(1)
                continue
            if result == 'teleported':
                print_centered(color_text('Teleportācija ziemā? Šeit nav pieejama.', RED))
                time.sleep(1)
                continue
            print_centered(color_text("Atgriežamies pie kaujas izvēles.", DIM))
            time.sleep(1)
            continue
        
        elif action == "quit" or action == "iziet":
            print_centered(color_text("Tu izlēmi iziet no spēles.", RED, bold=True))
            player['hp'] = 0  # Force game over
            return False
        
        else:
            print_centered(color_text("Nepareiza izvēle! Pamēģini vēlreiz.", RED))
            time.sleep(1)
            continue
        
        time.sleep(1)
        
        # Monster (or boss) turn
        if monster['hp'] > 0:
            def_mod = player.get('defense', 0)
            if defending:
                def_mod += 5  # Bonus defense when defending
                defending = False

            if monster.get('is_boss'):
                action = boss_special_action(monster, player)
                # Show action text when available
                if action.get('text'):
                    print_centered(color_text(action['text'], MAGENTA, bold=True))

                if action['type'] in ('attack', 'special'):
                    # Boss special/attack provides direct damage value
                    dmg = int(action.get('value', 0))
                    player['hp'] -= dmg
                    print_centered(color_text(f"{monster['name']} nodarīja {dmg} damage.", RED, bold=True))
                elif action['type'] == 'defend':
                    # Temporary buff: add to boss defense for next turn
                    buff = int(action.get('value', 0))
                    monster['defense'] = monster.get('defense', 0) + buff
                    print_centered(color_text(f"{monster['name']} aizsardzība pieauga par {buff} (pagaidu).", YELLOW))
                time.sleep(1)
            else:
                if monster.get('flinch', 0) > 0:
                    print_centered(color_text(f"{monster['name']} flinched and skipped its turn!", MAGENTA))
                    monster['flinch'] -= 1
                    if monster['flinch'] == 0:
                        print_centered(color_text(f"{monster['name']} recovers from the confusion.", GREEN))
                    time.sleep(1)
                else:
                    if monster.get('accuracy', 1.0) < 1.0 and random.random() > monster.get('accuracy', 1.0):
                        print_centered(color_text(f"{monster['name']} failed to find your position and missed!", MAGENTA))
                    else:
                        dmg, crit = final_damage(monster['attack'], def_mod)
                        player['hp'] -= dmg
                        msg = f"{monster['name']} uzbruka un nodarīja {dmg} damage"
                        if crit:
                            msg += " (kritiskais sitiens!)"
                        print_centered(color_text(msg, RED))
                    if monster.get('accuracy_duration', 0) > 0:
                        monster['accuracy_duration'] -= 1
                        if monster['accuracy_duration'] == 0:
                            monster['accuracy'] = 1.0
                            print_centered(color_text(f"{monster['name']} regains its aim.", GREEN))
                    time.sleep(1)
    
    if player['hp'] > 0:
        if player.get('attack_potion_turns', 0) > 0:
            player['attack_potion_turns'] = 0
            print_centered(color_text('Tava Attack Potion spēka ietekme ir beigusies.', DIM))
        print_centered(color_text(f"\nTu uzvareji {monster['name']}!", GREEN, bold=True))
        player['xp'] += monster['xp_reward']
        print_centered(color_text(f"Tu ieguvi {monster['xp_reward']} XP. Kopā XP: {player['xp']}", CYAN))
        award_item_drops(player)
        return True
    else:
        print_centered(color_text(f"\nTu zaudēji pret {monster['name']}.", RED, bold=True))
        return False

# ASCII Art for main menu
CAVE_RUNNER_LOGO = r'''
                                                                                                                         
                                                                                                                         
                                                        ███████████                                                      
                                                 ███████          ███████                                                 
                                              █████          ███        █████                                             
                                           █████        ████████████       █████                                          
                                         ████      ███████████████████████    ████                                        
                                       ███        █████████     ████████████     ███                                      
                                      ███    █   ████████      █  ██████ █████    ███                                     
                                    ████    ███ █████████  ███     █████   ████    ████                                   
                                   ████    █████████████   ████   █████    ████    █████                                  
                                  ████    ████████████████        █████ ██ █████     ████                                 
                                 ███    ██████████████  ████     ███████ ████████    ████                                 
                                 ██    ██████████████      ██ █████████  █████████   █ ███                                
                                ███    ████████████    █  █  █ █  ████  ███████████     ███                               
                               ███     ███████████████ ███     █     ██  ███████████     ██                               
                               ███   ████████████      ██     █████████ ████████████      ██                              
                              ████    ██████████████████     █████████ ██████████████     ██                              
                              ████     ██████████████████      ██████████████████████     ███                             
                              ███      █████████    █ █  ███     ████████████████████     ███                             
                              ██       █████████    █     ████    ██████████████████      ███                             
                             ███         ████████████████████████  █████████████████       ██                             
                             ███          ██████████████████████      ███████████          ███                            
                             ███           ██████████████████████  █████████████           ███                            
                                                                                                                         
          ████████    █ ██   ███    ███ ████████      ██ ████   ██   ███  ███   ███  ██    ██  ██ █████  ██ ████         
          ███   ██    █████   ███   ██  ███           ██   ███  ██   ███   ███  ███ █ ███  ██  ██       ███   ███        
          ██         ███ ██    ██  ███  ███████       ██   ███  ██   ███  █████ ███ ██ ██  ██  ██████   ███   ███        
          ██         ██  ███   ██████   ███████       ██ ████   ██   ███  ██ ███ ██ ███ ██ ██  ███████  ███ ████         
          ██    ██  ███ █████   ██ █    ███           ██  ███   ██   ███  ██  ███ █ ███  ████  ██       ███  ███         
          ████ ███  ██     ██   ███     ████████      ██   ███  ███ ███   ██   ███  ███   ██   ██ █████ ███   ███        
                                                                                                                         
                                                                                                                         
                                                                                                                         
                                                                                                                         
                                                                
'''

# --- 3. Implementēt clear_screen() funkciju ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- 7. & 8. Funkcija izvēlēm ar kļūdu apstrādi (try/except) ---
def get_player_choice(prompt, valid_options):
    while True:
        print(center_text(prompt))
        choice = input(center_prompt('> ')).strip().lower()
        # Pārbaudām, vai ievade ir sarakstā (piem., "1", "2" vai "start")
        if choice in valid_options:
            return choice
        else:
            print(f"Nepareiza izvēle! Lūdzu, izvēlies: {', '.join(valid_options)}")

def show_rules():
    clear_screen()
    print(center_text("=== Spēles noteikumi ==="))
    print(center_text("1. Tu esi alas skrējējs."))
    print(center_text("2. Katrā istabā cīnies ar monstriem."))
    print(center_text("3. Pēc uzvaras vari uzlabot spēku vai HP."))
    print(center_text("4. Sasniedz 10. istabu, lai cīnītos ar bossu."))
    print(center_text("5. Ja HP sasniedz 0, spēle beigusies."))
    print("\n" + center_text("Nospied Enter, lai atgrieztos pie galvenā izvēlnes."))
    input(center_prompt(''))

def show_main_menu():
    while True:
        clear_screen()
        print(render_ascii_art(CAVE_RUNNER_LOGO, allow_expand=True))
        
        print('\n' + '=' * get_terminal_width())
        print_centered(color_text('Izvēlies opciju:', YELLOW, bold=True))
        print_centered(color_text('START - Sākt spēli', CYAN))
        print_centered(color_text('RULES - Skatīt noteikumus', MAGENTA))
        print_centered(color_text('QUIT - Iziet', RED))
        print('=' * get_terminal_width())
        
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

def start_game():
    show_main_menu()
    
    # --- 2. Mainīgie spēlētāja stāvoklim ---
    player = {
        "hp": 100,
        "max_hp": 100,
        "str": 10,
        "room_number": 1, # --- 4. Cīņu skaitītājs ---
        "level": 1,
        "xp": 0,
        "xp_needed": 20,
        "defense": 2,
        "accuracy": 1.0,
        "blind_turns": 0,
        "attack_potion_turns": 0,
        "items": {
            ATTACK_POTION_KEY: 0,
            EXTRA_LIFE_KEY: 0,
            TELEPORT_KEY: 0,
            FLASHBANG_KEY: 0,
        }
    }

    print("Spēle CAVE RUNNER sākas!")
    time.sleep(1)

    # --- 1. Galvenais while cikls ---
    while player["hp"] > 0:
        clear_screen()

        # --- 6. 10. istabas pārbaude ---
        if player["room_number"] == 10:
            monster = {'name': 'Boss', 'hp': 50, 'max_hp': 50, 'attack': 10, 'xp_reward': 20, 'defense': 5}  # Special boss
        # --- 6. Boss room check ---
        if is_boss_room(player["room_number"]):
            # Choose a boss template from ALL-CAPS names and load its art
            template = load_monster(boss=True)
            # Generate boss stats (now based on base boss index, no player multipliers)
            generated = generate_boss(player, player["room_number"])
            # Merge generated stats with the template name and art
            generated['name'] = template.get('name', generated.get('name'))
            generated['art'] = template.get('art', generated.get('art', f"No ASCII art for {generated.get('name')}") )
            # Ensure max_hp present for HP bar display
            generated['max_hp'] = generated.get('hp', generated.get('max_hp', 0))
            generated['is_boss'] = True
            monster = generated
            # Big boss intro banner
            print('=' * get_terminal_width())
            print(center_text('!!! BOSS ENCOUNTER !!!'))
            print(center_text(boss_intro_text(monster)))
            print('=' * get_terminal_width())
            time.sleep(1)
            won = run_combat(player, monster)
            # If player died during boss, end the run
            if player.get('hp', 0) <= 0:
                print("Tu nomiri kaujā. Spēle beigusies.")
                break
            # On boss victory, show a larger congratulatory banner but allow continuing
            if won:
                print('\n' + '=' * get_terminal_width())
                print(center_text('APSVEICAM! Tu pieveici Bosu!'))
                print(center_text('Tu vari turpināt ceļu pa alu vai iziet.'))
                print('=' * get_terminal_width() + '\n')
                time.sleep(2)
        else:
            print(f"--- ISTABA NR. {player['room_number']} ---")
            monster = load_monster()
            print(f"Tu cīnies ar {monster['name']}!")
            print(render_ascii_art(monster['art']))
            time.sleep(1)
            combat_result = run_combat(player, monster)
            if not combat_result:
                break  # Player died

        # --- 5. Pēc uzvaras piedāvāt izvēlni ---
        # Check for level up
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
            else:
                print(center_text("Nepareiza izvēle! Mēģini vēlreiz."))
                time.sleep(1)
                continue

        if next_action == 'exit':
            break
        if next_action == 'teleported':
            continue

        # Palielinām istabu skaitu pēc izvēles
        player["room_number"] += 1
        print("\nTu dodies uz nākamo istabu...")
        time.sleep(1.5)

    if player["hp"] <= 0:
        gameover_path = os.path.join(os.path.dirname(__file__), '..', 'gameover.txt')
        try:
            with open(gameover_path, 'r') as f:
                gameover_art = f.read()
            print(center_ascii(gameover_art))
        except FileNotFoundError:
            print(center_text("GAME OVER"))
        
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

if __name__ == "__main__":
    start_game()