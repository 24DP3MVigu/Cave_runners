import os
import time
import sys
import csv
import random
import re
import shutil
import ctypes
import traceback
from ctypes import wintypes

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

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
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STORY_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'Story'))

# Sound effects and music folder
SOUND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'sound_efffects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'sound_effects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(os.getcwd(), 'sound_efffects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(os.getcwd(), 'sound_effects_and_music'))

SOUND_CACHE = {}
SOUND_ENABLED = False
CURRENT_MUSIC = None
AUDIO_BACKEND = None
MCI_SEND_STRING = None

if os.name == 'nt':
    try:
        winmm = ctypes.WinDLL('winmm')
        MCI_SEND_STRING = winmm.mciSendStringW
        MCI_SEND_STRING.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, wintypes.HWND]
        MCI_SEND_STRING.restype = wintypes.UINT
        AUDIO_BACKEND = 'mci'
        SOUND_ENABLED = True
    except Exception:
        AUDIO_BACKEND = None

if not SOUND_ENABLED:
    try:
        import pygame
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        pygame.mixer.init()
        AUDIO_BACKEND = 'pygame'
        SOUND_ENABLED = True
    except Exception:
        SOUND_ENABLED = False


def mci_send_string(command):
    if MCI_SEND_STRING is None:
        return False
    try:
        return MCI_SEND_STRING(command, None, 0, None) == 0
    except Exception:
        return False


def get_mci_type(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.wav':
        return 'waveaudio'
    return 'mpegvideo'


def mci_open(path, alias):
    mci_send_string(f'close {alias}')
    file_type = get_mci_type(path)
    return mci_send_string(f'open "{path}" type {file_type} alias {alias}')


def load_sound_asset(filename):
    if not SOUND_ENABLED:
        return None
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return None
    try:
        if filename not in SOUND_CACHE:
            SOUND_CACHE[filename] = pygame.mixer.Sound(path)
        return SOUND_CACHE[filename]
    except Exception:
        return None


def play_sound(filename, loops=0):
    if not SOUND_ENABLED:
        return
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return

    if AUDIO_BACKEND == 'mci':
        alias = 'sfx'
        if not mci_open(path, alias):
            return
        if loops == -1:
            mci_send_string(f'play {alias} repeat')
        else:
            mci_send_string(f'play {alias}')
        return

    sound = load_sound_asset(filename)
    if sound:
        try:
            sound.play(loops=loops)
        except Exception:
            pass


def play_music(filename, loops=-1):
    global CURRENT_MUSIC
    if not SOUND_ENABLED:
        return
    path = os.path.join(SOUND_DIR, filename)
    if not os.path.isfile(path):
        return

    if AUDIO_BACKEND == 'mci':
        alias = 'music'
        if CURRENT_MUSIC == filename:
            if loops == -1:
                mci_send_string(f'play {alias} repeat')
            else:
                mci_send_string(f'play {alias}')
            return
        if not mci_open(path, alias):
            return
        if loops == -1:
            mci_send_string(f'play {alias} repeat')
        else:
            mci_send_string(f'play {alias}')
        CURRENT_MUSIC = filename
        return

    try:
        if CURRENT_MUSIC == filename and pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops=loops)
        CURRENT_MUSIC = filename
    except Exception:
        pass


def stop_music():
    global CURRENT_MUSIC
    if not SOUND_ENABLED:
        return
    if AUDIO_BACKEND == 'mci':
        mci_send_string('stop music')
        mci_send_string('close music')
        CURRENT_MUSIC = None
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    CURRENT_MUSIC = None

STORY_PAGES = [
    {
        'art_file': 'first_image.txt',
        'lines': [
            'Sen cilvēki dzīvoja',
            'mierīgi uz virsmas.',
            'Dziļi zem zemes gulēja',
            'plaši, nebeidzami tīkli',
        ],
    },
    {
        'art_file': 'picture_two.txt',
        'lines': [
            'Šīs senās alas bija mājvieta dīvainiem un spēcīgiem briesmoņiem.',
            'Tie bija izauguši tumsā gadu tūkstošiem paaudzēs.',
        ],
    },
    {
        'art_file': 'third_image.txt',
        'lines': [
            'Ziņkāres un mantkārības vadīti, cilvēki devās dziļi alās.',
            'Liktenīgajos tuneļos starp abām rasēm izcēlās liels karš.',
        ],
    },
    {
        'art_file': 'fourth_image.txt',
        'lines': [
            'Pēc daudzām kaujām cilvēki ar varenu maģiju aizzīmogoja alu dziļākās un bīstamākās vietas.',
            'Taču alas... tās bija patiesi bezgalīgas.',
        ],
    },
    {
        'art_file': 'fifth_image.txt',
        'lines': [
            'Daudzus gadus vēlāk... Leģendas vēsta par Bezgalīgajām alām.',
            'Tikai drosmīgākie karotāji — Alu skrējēji (Cave Runners) — uzdrošinās tajās ieiet.',
        ],
    },
    {
        'art_file': 'sixth_image.txt',
        'lines': [
            'Cīnies ar briesmoņiem un kļūsti spēcīgāks, virzoties cauri telpām.',
            'Katrā desmitajā telpā tevi gaida varens boss, lai pārbaudītu tavu spēku.',
        ],
    },
    {
        'art_file': 'seventh_image.txt',
        'lines': [
            'Un ja tu pierādīsi, ka esi cienīgs... vai pietiekami muļķis...',
            'Tu vari pamodināt Tukšumu — patieso bezdibeņa sargu.',
        ],
    },
]


def get_terminal_size():
    try:
        return shutil.get_terminal_size(fallback=(DEFAULT_TERMINAL_WIDTH, 24))
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
    for line in str(text).splitlines():
        print(center_text(line))


def maximize_console():
    if os.name == 'nt':
        os.system('mode con: cols=160 lines=48')
    else:
        # Attempt to expand the terminal on UNIX-like systems.
        sys.stdout.write('\x1b[8;48;160t')
        sys.stdout.flush()


def load_story_art(filename):
    art_path = os.path.join(STORY_DIR, filename)
    try:
        with open(art_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return f'[{filename} not found]'


def fade_in_lines(lines, char_delay=0.01, line_delay=0.15):
    for line in lines:
        display = ''
        for ch in line:
            display += ch
            print(center_text(display), end='\r', flush=True)
            time.sleep(char_delay)
        print(center_text(display))
        time.sleep(line_delay)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_story_page(page_index, page):
    clear_screen()
    art = load_story_art(page['art_file'])
    print(center_ascii(art))
    print('\n')
    fade_in_lines(page['lines'])
    print('\n' + center_text('[Nospied Enter, lai turpinātu]'))
    input(center_prompt(''))


def show_fullscreen_prompt():
    maximize_console()
    clear_screen()
    term_size = get_terminal_size()
    blank_lines = max(0, (term_size.lines - 4) // 2)
    print('\n' * blank_lines)
    print(center_text('Make sure the game is FULL SCREEN.'))
    print(center_text('Press Enter to start.'))
    input(center_prompt(''))
    clear_screen()


def show_story_intro():
    stop_music()
    play_music('before_epic_intro.mp3', loops=-1)
    show_fullscreen_prompt()
    for idx, page in enumerate(STORY_PAGES, start=1):
        show_story_page(idx, page)
        if idx == len(STORY_PAGES):
            play_music('epic_intro.mp3', loops=-1)
    clear_screen()


def print_action_menu(player):
    # Render a boxed, image-like menu for actions
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
    # show item counts inline
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
        'drop_chance': 0.30,
        'combat_usable': False,
        'outside_usable': True,
    },
    EXTRA_LIFE_KEY: {
        'name': 'Extra Life',
        'description': 'Atjauno 50% no Tava maksimālā HP uzreiz.',
        'art_file': 'Extra_Life.txt',
        'drop_chance': 0.37,  
        'combat_usable': False,
        'outside_usable': True,
    },
    TELEPORT_KEY: {
        'name': 'Potion of Teleportion',
        'description': 'Izmet tevi cauri citai istabai, izmanto ja pretinieks šķiet par grūtu. Nav efekta pret bosa istabām.',
        'art_file': 'Potion_of_teleportion.txt',
        'drop_chance': 0.15,
        'combat_usable': True,
        'outside_usable': False,
    },
    FLASHBANG_KEY: {
        'name': '404 Flashbang',
        'description': 'Piespiež ienaidnieku palaist garām 2 gājienus un samazina tā precizitāti.',
        'art_file': 'flashbang.txt',
        'drop_chance': 0.50,  
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

FINAL_BOSS_DIR = os.path.join(BASE_DIR, 'final_boss_fight')
FINAL_BOSS_ARTS = {
    1: 'standing_up.txt',
    2: 'armored_enhanced_standing.txt',
    3: 'bloodysmilezoomed.txt',
    4: 'Sitting_interaction.txt',
}


def load_final_boss_art(filename):
    art_path = os.path.join(FINAL_BOSS_DIR, filename)
    try:
        with open(art_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'No art for {filename}'


def render_final_boss_art(phase):
    filename = FINAL_BOSS_ARTS.get(phase, 'standing_up.txt')
    return render_ascii_art(load_final_boss_art(filename), max_width=min(get_terminal_width(), 90), allow_expand=True)


def final_boss_dialogue(lines, delay=0.06):
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


def run_final_boss(player):
    if player.get('final_boss_completed'):
        return

    stop_music()

    play_music('theme1.mp3', loops=-1)

    clear_screen()
    final_boss_dialogue([
        'Something wakes in the deepest dark...',
        'You can feel "Void" stir beneath the earth.\n',
        'The Void: "Another fool dares disturb my hunger."\n',
        'Cave Runner: "I came to end you, not to run."\n',
        'The Void: "Then take your last breath, mortal."',
    ])

    print(render_final_boss_art(1))
    print('\n')
    print(center_text(color_text('MERCY or CHALLENGE?', YELLOW, bold=True)))
    print(center_text(color_text('Type "mercy" to surrender, or "challenge" to fight.', WHITE)))

    while True:
        choice = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()
        if choice == 'mercy':
            stop_music()
            play_sound('mercy.mp3')
            clear_screen()
            print(center_text(color_text('Your defiance fades as Tukšums swallows your hope...', RED, bold=True)))
            time.sleep(2)
            print(center_text(color_text('GAME OVER', RED, bold=True)))
            time.sleep(2)
            sys.exit(0)
        elif choice == 'challenge':
            break
        else:
            print(center_text('Nepareiza izvēle! Izvēlies "mercy" vai "challenge".'))

    boss = {
        'name': 'The Void',
        'hp': 1,
        'max_hp': 400,
        'attack': 44,
        'defense': 15,
        # other branch used hp=180,max_hp=180,attack=60,defense=25
        'phase': 1,
        'is_boss': True,
    }
    stop_music()

    play_music('theme2.mp3', loops=-1)
    time.sleep(1)

    defending = False
    while player['hp'] > 0 and boss['hp'] > 0:
        clear_screen()
        print_centered(color_text('!!! FINAL BOSS: THE VOID !!!', RED, bold=True))
        print(render_final_boss_art(boss['phase']))
        display_hp_bar(player['hp'], player['max_hp'], 'Tavs HP', centered=True)
        display_hp_bar(boss['hp'], boss['max_hp'], "The Void HP", centered=True)
        print_centered(color_text(f"Spēks: {player['str']} | Aizsardzība: {player.get('defense', 0)}", MAGENTA))
        print_action_menu(player)
        print_centered(color_text('Tava izvēle:', GREEN, bold=True))
        action = input(color_text(center_prompt('> '), GREEN, bold=True)).strip().lower()

        if action == 'attack':
            attack_bonus = 5 if player.get('attack_potion_turns', 0) > 0 else 0
            dmg, crit = final_damage(player['str'] + attack_bonus, boss['defense'])
            boss['hp'] -= dmg
            msg = f"Tu uzbruki un nodarīji {dmg} damage"
            if crit:
                msg += " (kritiskais sitiens!)"
            if attack_bonus > 0:
                msg += " (Attack Potion bonus!)"
            print_centered(color_text(msg, GREEN))
            play_sound('void_attack.mp3')
            if player.get('attack_potion_turns', 0) > 0:
                print_centered(color_text('Attack Potion efektu joprojām izmanto kaujas laikā.', DIM))
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
            print_centered(color_text('Tu izlēmi pamest kauju. Tukšums to patiesi novērtē.', RED, bold=True))
            player['hp'] = 0
            break
        else:
            print_centered(color_text('Nepareiza izvēle! Pamēģini vēlreiz.', RED))
            time.sleep(1)
            continue

        time.sleep(1)

        if boss['hp'] <= 120 and boss['phase'] == 1:
            boss['phase'] = 2
            boss['attack'] += 4
            boss['defense'] += 3
            print_centered(color_text('Tukšums sakustas. Tas kļūst spēcīgāks un cietāks.', RED, bold=True))
            play_sound('messages.mp3')
            time.sleep(2)
        elif boss['hp'] <= 60 and boss['phase'] == 2:
            boss['phase'] = 3
            boss['attack'] += 6
            boss['defense'] += 2
            print_centered(color_text('The Void uzspridzina realitāti. Saule pazūd.', RED, bold=True))
            play_sound('messages.mp3')
            time.sleep(2)

        if boss['hp'] > 0:
            def_mod = player.get('defense', 0)
            if defending:
                def_mod += 6
                defending = False

            if boss['phase'] == 3 and random.random() < 0.35:
                carve = int(boss['attack'] * 1.4)
                player['hp'] -= carve
                print_centered(color_text(f'The Void tears through your armor for {carve} damage!', RED, bold=True))
            else:
                dmg, crit = final_damage(boss['attack'], def_mod)
                player['hp'] -= dmg
                msg = f'The Void uzbruka un nodarīja {dmg} damage'
                if crit:
                    msg += ' (kritiskais sitiens!)'
                print_centered(color_text(msg, RED))
            play_sound('enemy_hit.mp3')
            if player.get('hp', 0) <= 0:
                break
            time.sleep(1)

    stop_music()
    if player['hp'] > 0 and boss['hp'] <= 0:
        play_music('victory.mp3', loops=-1)
        clear_screen()
        print_centered(color_text('Tukšums izjūk. Gaisma atgriežas.', GREEN, bold=True))
        time.sleep(2)
        print_centered(color_text('Tev izdevās. Bet atceries: Tukšums gaida atkal.', YELLOW))
        print_centered(color_text('Apsveicu! Tu esi uzvarējis alas pavēlnieku.', CYAN, bold=True))
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
    play_sound('404flash.mp3')
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
    play_sound('potions.mp3')
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
    play_sound('potions.mp3')
    return True


def use_teleport(player, monster=None):
    count = get_item_count(player, TELEPORT_KEY)
    if count <= 0:
        print_centered(color_text("Nav Potion of Teleportion tavā inventārā.", RED, bold=True))
        return False
    cur_room = player.get('room_number', 1)
    # Disallow teleportation only if currently in a boss room
    if is_boss_room(cur_room):
        print_centered(color_text('Teleportāciju nevar izmantot bosa istabā.', RED, bold=True))
        return False
    # Disallow teleportation during the final VOID boss fight as well
    if monster is not None and str(monster.get('name', '')).strip().lower() == 'the void':
        print_centered(color_text('Teleportāciju nevar izmantot pret The Void.', RED, bold=True))
        return False
    player['items'][TELEPORT_KEY] -= 1
    play_sound('potions.mp3')
    # Move the player forward one room (work as a combat skip special attack)
    player['room_number'] = cur_room + 1
    if monster is not None:
        monster['hp'] = 0
        print_centered(color_text('Teleportācija izdevās! Tu pārvietojies uz nākamo istabu un monstrs pazuda.', CYAN, bold=True))
    else:
        print_centered(color_text('Tu izteleportējies uz nākamo istabu!', CYAN, bold=True))
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
        # Teleportation device is only usable during combat and functions as a skip/special
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

def load_monster(player, boss: bool = False):
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
    
    # Scale monster stats based on boss wins (only for regular monsters)
    if not boss and player.get('boss_wins', 0) > 0:
        scale_factor = 1 + 0.9 * player['boss_wins']  # branch A used 0.67, branch B used 1
        monster['hp'] = int(monster['hp'] * scale_factor)
        monster['attack'] = int(monster['attack'] * scale_factor)
        monster['defense'] = int(monster['defense'] * scale_factor)
    
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
    player["xp_needed"] += 40  # other branch used 43
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
    play_sound('upgrade.mp3')
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
        
        elif action == "item" or action == 'items':
            result = show_items_catalog(player, in_combat=True, monster=monster)
            if result == 'used':
                time.sleep(1)
                continue
            if result == 'teleported':
                return 'teleported'
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
                    play_sound('enemy_hit.mp3')
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
                        play_sound('enemy_hit.mp3')
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


def show_scary_event():
    stop_music()
    clear_screen()
    play_music('messages.mp3', loops=-1)
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

START_BUTTON_ART = r'''
________  _________  ________  ________  _________   
|\   ____\|\___   ___\\   __  \|\   __  \|\___   ___\ 
\ \  \___|\|___ \  \_\ \  \|\  \ \  \|\  \|___ \  \_| 
 \ \_____  \   \ \  \ \ \   __  \ \   _  _\   \ \  \  
  \|____|\  \   \ \  \ \ \  \ \  \ \  \\  \|   \ \  \ 
    ____\_\  \   \ \__\ \ \__\ \__\ \__\\ _\    \ \__\
   |\_________\   \|__|  \|__|\|__|\|__|\|__|    \|__|
   \|_________|
'''

RULES_BUTTON_ART = r'''
________  ___  ___  ___       _______   ________      
|\   __  \|\  \|\  \|\  \     |\  ___ \ |\   ____\     
\ \  \|\  \ \  \\\  \ \  \    \ \   __/|\ \  \___|_    
 \ \   _  _\ \  \\\  \ \  \    \ \  \_|/_\ \_____  \   
  \ \  \\  \\ \  \\\  \ \  \____\ \  \_|\ \|____|\  \  
   \ \__\\ _\\ \_______\ \_______\ \_______\____\_\  \ 
    \|__|\|__|\|_______|\|_______|\|_______|\_________\
                                           \|_________|
'''

QUIT_BUTTON_ART = r'''
________  ___  ___  ___  _________   
|\   __  \|\  \|\  \|\  \|\___   ___\ 
\ \  \|\  \ \  \\\  \ \  \|___ \  \_| 
 \ \  \\\  \ \  \\\  \ \  \   \ \  \  
  \ \  \\\  \ \  \\\  \ \  \   \ \  \ 
   \ \_____  \ \_______\ \__\   \ \__\
    \|___| \__\|_______|\|__|    \|__|
          \|__|
'''


def render_side_by_side(*arts, spacing=6):
    columns = [art.splitlines() for art in arts]
    max_lines = max(len(col) for col in columns)
    for col in columns:
        col += [''] * (max_lines - len(col))
    widths = [max(len(line) for line in col) for col in columns]
    combined = []
    pad = ' ' * spacing
    for rows in zip(*columns):
        padded = [row.ljust(width) for row, width in zip(rows, widths)]
        combined.append(pad.join(padded))
    return center_ascii('\n'.join(combined))


def show_main_menu():
    stop_music()
    while True:
        clear_screen()
        print(render_ascii_art(CAVE_RUNNER_LOGO, allow_expand=True))
        print(render_side_by_side(START_BUTTON_ART, RULES_BUTTON_ART, QUIT_BUTTON_ART))
        print('\n')
        # Optional plain text labels from the other branch:
        # print(center_text(color_text('START', CYAN, bold=True).ljust(26) + ' ' * 6 + color_text('RULES', MAGENTA, bold=True).center(24) + ' ' * 6 + color_text('QUIT', RED, bold=True).rjust(18)))
        # print('\n')
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


def show_rules():
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


def start_game():
    show_story_intro()
    show_main_menu()
    play_music('main.mp3', loops=-1)
    
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
        "boss_wins": 0,
        "final_boss_chance": 0.0,
        "final_boss_completed": False,
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
            template = load_monster(player, boss=True)
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
            play_music(random.choice(['boss1.mp3', 'boss2.mp3', 'boss3.mp3']), loops=-1)
            time.sleep(1)
            won = run_combat(player, monster)
            stop_music()
            # If player died during boss, end the run
            if player.get('hp', 0) <= 0:
                print("Tu nomiri kaujā. Spēle beigusies.")
                break
            # On boss victory, show a larger congratulatory banner, then scary event
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
                if not player.get('final_boss_completed', False):
                    chance_roll = random.random()
                    if chance_roll < player.get('final_boss_chance', 0.0):
                        print(center_text(color_text('A tear in the world opens... something ancient is stirring.', RED, bold=True)))
                        time.sleep(2)
                        run_final_boss(player)
                        if player['hp'] <= 0:
                            break
                play_music('main.mp3', loops=-1)
        else:
            print(f"--- ISTABA NR. {player['room_number']} ---")
            monster = load_monster(player)
            print(f"Tu cīnies ar {monster['name']}!")
            print(render_ascii_art(monster['art']))
            time.sleep(1)
            combat_result = run_combat(player, monster)
            if combat_result == 'teleported':
                continue
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
            elif choice in ('void', 'tukšums', 'thevoid', 'summonvoid'):
                print(center_text(color_text('Secret ritual activated... Tukšums answers.', RED, bold=True)))
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

        # Palielinām istabu skaitu pēc izvēles
        player["room_number"] += 1
        print("\nTu dodies uz nākamo istabu...")
        time.sleep(1.5)

    if player["hp"] <= 0:
        play_music('You_Died.mp3', loops=-1)
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
    try:
        start_game()
    except Exception:
        error_log_path = os.path.join(os.path.dirname(__file__), '..', 'game_crash.log')
        with open(error_log_path, 'a', encoding='utf-8') as log_file:
            log_file.write('=== Crash detected ===\n')
            log_file.write(traceback.format_exc())
            log_file.write('\n')
        print('A crash was detected. Details have been written to game_crash.log.')
        print('Please send the contents of that file if the game closes unexpectedly.')