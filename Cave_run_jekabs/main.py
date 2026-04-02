import os
import time
import sys
import csv
import random

try:
    TERMINAL_WIDTH = os.get_terminal_size().columns
except OSError:
    TERMINAL_WIDTH = 80  # Default fallback

def center_text(text):
    return text.center(TERMINAL_WIDTH)

def center_ascii(text):
    lines = text.split('\n')
    centered_lines = []
    for line in lines:
        line = line.rstrip()
        if line:
            centered_lines.append(line.center(TERMINAL_WIDTH))
        else:
            centered_lines.append('')
    return '\n'.join(centered_lines)

def display_hp_bar(current, max_hp, label="HP"):
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
    print(f"{label}: {color}{bar}{reset} {current}/{max_hp}")

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
    # Load ASCII art if exists
    try:
        with open(os.path.join(os.path.dirname(__file__), 'Monstri', monster["name"]), 'r', encoding='utf-8') as f:
            monster['art'] = f.read()
    except FileNotFoundError:
        monster['art'] = f'No ASCII art for {monster["name"]}'
    return monster

def level_up(player):
    print("\n*** LEVEL UP! ***")
    player["level"] += 1
    player["xp_needed"] += 30  # Increase XP needed for next level
    points = 3

    print(f"Tu sasniedzi {player['level']} līmeni!")
    print(f"Tev ir {points} atribūtu punkti ko sadalīt.")

    while points > 0:
        print("\nIzvēlies, kur ieguldīt punktu:")
        print("attack - Uzbrukums (+1)")
        print("defense - Aizsardzība (+1)")
        print("max_health - Maksimālais HP (+5)")
        print("quit - Iziet no spēles")
        print(f"Atlikušie punkti: {points}")

        print(center_text("Tava izvēle:"))
        choice = input('> ').strip().lower()

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
        print(f"--- Cīņa ar {monster['name']} ---")
        display_hp_bar(player['hp'], player['max_hp'], "Tavs HP")
        print(f"Spēks: {player['str']} | Aizsardzība: {player.get('defense', 0)}")
        display_hp_bar(monster['hp'], monster['max_hp'], f"{monster['name']} HP")
        print(f"Uzbrukums: {monster['attack']}")
        print(monster['art'])
        print("\nIzvēlies darbību:")
        print("attack - Uzbrukt")
        print("defense - Aizsargāties")
        print("item - Izmantot priekšmetu")
        print("quit - Iziet no spēles")
        
        action = input("Tava izvēle: ").strip().lower()
        
        if action == "attack":
            dmg, crit = final_damage(player['str'], monster['defense'])
            monster['hp'] -= dmg
            msg = f"Tu uzbruki un nodarīji {dmg} damage"
            if crit:
                msg += " (kritiskais sitiens!)"
            print(msg)
        
        elif action == "defense":
            defending = True
            print("Tu sagatavojies aizsardzībai.")
        
        elif action == "item":
            # Simple heal
            heal = 10
            player['hp'] = min(player['max_hp'], player['hp'] + heal)
            print(f"Tu izmantoji priekšmetu un atguvi {heal} HP.")
        
        elif action == "quit" or action == "iziet":
            print("Tu izlēmi iziet no spēles.")
            player['hp'] = 0  # Force game over
            return False
        
        else:
            print("Nepareiza izvēle! Pamēģini vēlreiz.")
            time.sleep(1)
            continue
        
        time.sleep(1)
        
        # Monster turn
        if monster['hp'] > 0:
            def_mod = player.get('defense', 0)
            if defending:
                def_mod += 5  # Bonus defense when defending
                defending = False
            dmg, crit = final_damage(monster['attack'], def_mod)
            player['hp'] -= dmg
            msg = f"{monster['name']} uzbruka un nodarīja {dmg} damage"
            if crit:
                msg += " (kritiskais sitiens!)"
            print(msg)
            time.sleep(1)
    
    if player['hp'] > 0:
        print(f"\nTu uzvareji {monster['name']}!")
        player['xp'] += monster['xp_reward']
        print(f"Tu ieguvi {monster['xp_reward']} XP. Kopā XP: {player['xp']}")
        return True
    else:
        print(f"\nTu zaudēji pret {monster['name']}.")
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
        choice = input('> ').strip().lower()
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
    input()

def show_main_menu():
    while True:
        clear_screen()
        print(CAVE_RUNNER_LOGO)
        
        print('\n' + '=' * TERMINAL_WIDTH)
        print(center_text('Izvēlies opciju:'))
        print(center_text('START - Sākt spēli'))
        print(center_text('RULES - Skatīt noteikumus'))
        print(center_text('QUIT - Iziet'))
        print('=' * TERMINAL_WIDTH)
        
        print(center_text('Tava izvēle:'))
        choice = input('> ').strip().lower()
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
            won = run_combat(player, monster)
            if won:
                print("APSVEICAM! Tu pieveici Bosu un izbēgi no alas!")
                break
            # If not won, continue or end, but since combat handles death, perhaps break if lost
        else:
            print(f"--- ISTABA NR. {player['room_number']} ---")
            monster = load_monster()
            print(f"Tu cīnies ar {monster['name']}!")
            print(monster['art'])
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
            choice = input('> ').strip().lower()
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