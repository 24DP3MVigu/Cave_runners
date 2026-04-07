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


def color_text(text, color, bold=False):
    if not color:
        return str(text)
    prefix = f"{BOLD if bold else ''}{color}"
    return f"{prefix}{text}{RESET}"


def print_action_menu():
    menu_width = min(70, max(40, get_terminal_width() - 16))
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
    print_centered(color_text('   ✨ Atgūsti dzīvību vai izmanto īpašu spēku.', DIM))
    print_centered(sep)
    print_centered(color_text(' quit ', RED, bold=True) + color_text(' - Iziet no spēles', WHITE))
    print_centered(color_text('   ⛔ Pamet kauju un atgriezies galvenajā izvēlnē.', DIM))
    print_centered(bot)
    print()


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
    print("\n*** LEVEL UP! ***")
    player["level"] += 1
    player["xp_needed"] += 30  # Increase XP needed for next level
    points = 3

    # Big level-up banner (similar style to boss victory)
    print('\n' + '=' * get_terminal_width())
    print(center_text(f"APSVEICAM! Tu sasniedzi {player['level']} līmeni!"))
    print(center_text('Tu vari turpināt ceļu pa alu vai iziet.'))
    print('=' * get_terminal_width() + '\n')
    time.sleep(1.5)

    print(f"Tev ir {points} atribūtu punkti ko sadalīt.")

    while points > 0:
        print("\nIzvēlies, kur ieguldīt punktu:")
        print("attack - Uzbrukums (+1)")
        print("defense - Aizsardzība (+1)")
        print("max_health - Maksimālais HP (+5)")
        print("quit - Iziet no spēles")
        print(f"Atlikušie punkti: {points}")

        print(center_text("Tava izvēle:"))
        choice = input(center_prompt('> ')).strip().lower()

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
        print_action_menu()
        print_centered(color_text('Tava izvēle:', GREEN, bold=True))
        action = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()
        
        if action == "attack":
            dmg, crit = final_damage(player['str'], monster['defense'])
            monster['hp'] -= dmg
            msg = f"Tu uzbruki un nodarīji {dmg} damage"
            if crit:
                msg += " (kritiskais sitiens!)"
            print_centered(color_text(msg, GREEN))
        
        elif action == "defense":
            defending = True
            print_centered(color_text("Tu sagatavojies aizsardzībai.", YELLOW))
        
        elif action == "item":
            # Simple heal
            heal = 10
            player['hp'] = min(player['max_hp'], player['hp'] + heal)
            print_centered(color_text(f"Tu izmantoji priekšmetu un atguvi {heal} HP.", BLUE))
        
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
                dmg, crit = final_damage(monster['attack'], def_mod)
                player['hp'] -= dmg
                msg = f"{monster['name']} uzbruka un nodarīja {dmg} damage"
                if crit:
                    msg += " (kritiskais sitiens!)"
                print_centered(color_text(msg, RED))
                time.sleep(1)
    
    if player['hp'] > 0:
        print_centered(color_text(f"\nTu uzvareji {monster['name']}!", GREEN, bold=True))
        player['xp'] += monster['xp_reward']
        print_centered(color_text(f"Tu ieguvi {monster['xp_reward']} XP. Kopā XP: {player['xp']}", CYAN))
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
        "defense": 2
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

        print("\nKo darīsi tālāk?")
        if player['xp'] >= player['xp_needed']:
            print("1. Doties tālāk")
            print("2. Uzlaboties (Upgrade)")
            print("3. Iziet")
            choice = get_player_choice("Tava izvēle (1, 2 vai 3): ", ["1", "2", "3"])
            if choice == "2":
                level_up(player)
            elif choice == "3":
                break
        else:
            print("1. Doties tālāk")
            print("2. Iziet")
            choice = get_player_choice("Tava izvēle (1 vai 2): ", ["1", "2"])
            if choice == "2":
                break

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