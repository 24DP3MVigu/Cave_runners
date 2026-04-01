import os
import time
import sys

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
        try:
            choice = input(prompt).strip().lower()
            # Pārbaudām, vai ievade ir sarakstā (piem., "1", "2" vai "start")
            if choice in valid_options:
                return choice
            else:
                print(f"Nepareiza izvēle! Lūdzu, izvēlies: {', '.join(valid_options)}")
        except Exception as e:
            print(f"Notika kļūda: {e}. Mēģini vēlreiz.")

# --- 6. Speciāla Bosa funkcija (vieta tavam/komandas kodam) ---
def boss_battle(player):
    clear_screen()
    print("!!! UZMANĪBU !!!")
    print("Tu esi sasniedzis 10. istabu. Lielais Boss sēž savā tronī!")
    time.sleep(2)
    # Šeit vēlāk tiks izsaukta cīņas loģika no combat_engine.py
    # Pagaidām simulējam cīņu:
    return True # Atgriež True, ja uzvar

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
        
        choice = input(center_text('Tava izvēle: ')).strip().lower()
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
        "room_number": 1 # --- 4. Cīņu skaitītājs ---
    }

    print("Spēle CAVE RUNNER sākas!")
    time.sleep(1)

    # --- 1. Galvenais while cikls ---
    while player["hp"] > 0:
        clear_screen()

        # --- 6. 10. istabas pārbaude ---
        if player["room_number"] == 10:
            won = boss_battle(player)
            if won:
                print("APSVEICAM! Tu pieveici Bosu un izbēgi no alas!")
                break
            # If not won, assume game continues (or add logic to end game)
        else:
            print(f"--- ISTABA NR. {player['room_number']} ---")
            print(f"Tev pretī stājas monstrs!")
            # Šeit nāks: combat_result = run_battle(player, load_monster())
            time.sleep(1)
            print("Tu pieveici monstru!") # Simulācija

        # --- 5. Pēc uzvaras piedāvāt izvēlni ---
        print("\nKo darīsi tālāk?")
        print("1. Doties tālāk")
        print("2. Uzlaboties (Upgrade)")

        # --- 7. & 8. Izmanto drošo ievadi ---
        choice = get_player_choice("Tava izvēle (1 vai 2): ", ["1", "2"])

        if choice == "2":
            clear_screen()
            print("--- UPGRADE MENU ---")
            print("1. +20 HP")
            print("2. +5 Strength")
            upg = get_player_choice("Izvēlies uzlabojumu (1 vai 2): ", ["1", "2"])

            if upg == "1":
                player["max_hp"] += 20
                player["hp"] = player["max_hp"]
                print("Dzīvības palielinātas!")
            else:
                player["str"] += 5
                print("Spēks palielināts!")
            time.sleep(1)

        # Palielinām istabu skaitu pēc izvēles
        player["room_number"] += 1
        print("\nTu dodies uz nākamo istabu...")
        time.sleep(1.5)

    if player["hp"] <= 0:
        print("\nTu esi miris. Spēle beigusies.")

if __name__ == "__main__":
    start_game()