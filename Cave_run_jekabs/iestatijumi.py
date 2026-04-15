"""
iestatijumi.py — Spēles iestatījumi un konstantes.

Šajā failā ir definētas visas spēles konstantes: krāsu kodi,
ceļi uz resursiem, priekšmetu definīcijas, stāsta lapas,
tradicionālās piezīmes un galvenās izvēlnes ASCII māksla.
"""

import os
import re

# ============================================================
# Bāzes direktorija — nodrošina, ka ceļi darbojas no jebkuras vietas
# ============================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STORY_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'Story'))

# ============================================================
# Skaņu efektu un mūzikas mape (mēģina vairākus nosaukumus)
# ============================================================
SOUND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'sound_efffects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'sound_effects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(os.getcwd(), 'sound_efffects_and_music'))
if not os.path.isdir(SOUND_DIR):
    SOUND_DIR = os.path.normpath(os.path.join(os.getcwd(), 'sound_effects_and_music'))

# ============================================================
# Termināļa noklusējuma platums
# ============================================================
DEFAULT_TERMINAL_WIDTH = 80

# ============================================================
# ANSI escape kodu regulārā izteiksme (teksta attīrīšanai)
# ============================================================
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

# ============================================================
# Termināļa krāsu kodi
# ============================================================
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

# ============================================================
# Priekšmetu atslēgas (lietojamas kā vārdnīcas atslēgas)
# ============================================================
ATTACK_POTION_KEY = 'attack_potion'
EXTRA_LIFE_KEY = 'extra_life'
TELEPORT_KEY = 'potion_teleportation'
FLASHBANG_KEY = '404_flashbang'

# ============================================================
# Priekšmetu resursu mape
# ============================================================
ITEMS_DIR = os.path.join(BASE_DIR, 'Items')

# ============================================================
# Priekšmetu definīcijas — nosaukumi, apraksti, izkritīšanas iespējas
# ============================================================
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
        'drop_chance': 0.39,
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

# Priekšmetu secība (kā tie tiek rādīti katalogā)
ITEM_ORDER = [
    ATTACK_POTION_KEY,
    EXTRA_LIFE_KEY,
    TELEPORT_KEY,
    FLASHBANG_KEY,
]

# Priekšmetu pseidonīmi — atvieglo ievadi konsolē
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

# ============================================================
# Tradicionālās piezīmes (lore notes) — stāsta elementi
# ============================================================
LORE_NOTES = [
    {
        'title': 'Piezīme 1: Virve vēl silta',
        'author': 'M. Eglis, kartogrāfs',
        'min_room': 2,
        'text': [
            'Ja kāds šo atrod, tad ala zem vecajiem kara ceļiem ir īsta.',
            'Mēs iegājām sešatā. Katru pagriezienu iezīmējām ar sarkanu virvi un sveču taukiem.',
            'Sākumā viss bija viegli. Radības bēga no lāpu gaismas, un no dziļuma nāca silts caurvējš.',
            'Zem šiem tuneļiem ir aprakta pilsēta. Es to zinu. Es dzirdu durvis aizveramies tur, kur durvju nemaz nav.',
            'Ja līdz rītausmai neatgriezīšos, pasaki Elīnai, ka man bija taisnība - mums bija jāiet dziļāk.',
        ],
    },
    {
        'title': 'Piezīme 2: Neuzticies atbalsīm',
        'author': 'Seržants Veils',
        'min_room': 4,
        'text': [
            'Neuzticies atbalsīm.',
            'Mēs kliedzām, lai izmērītu kambaru dziļumu, bet skaņa, kas atgriezās, kavējās un bija nepareiza.',
            'Tā atbildēja ar vārdiem. Vispirms ar manējo. Pēc tam ar kareivju vārdiem, kas jau sen krituši virszemē.',
            'Rikis aizgāja balsij, kas skanēja tieši kā viņa māte. Mēs atradām tikai viņa laternu, vēl joprojām šūpojoties.',
            'Virve ir pārgriezta gludi. Nekas šeit neplēš. Tas izvēlas.',
        ],
    },
    {
        'title': 'Piezīme 3: Akmenī ir zobi',
        'author': 'I. Krūmiņš, racējs',
        'min_room': 6,
        'text': [
            'Es domāju, ka skrāpēšana sienās ir ūdens spiediens.',
            'Tā nav. Dažās vietās sienas ir mīkstas. Un siltas. Kad cirtu ar cirtni, akmens asiņoja melns un tunelis nodrebēja.',
            'Mēs smējāmies, jo bailes padara cilvēkus par idiotiem.',
            'Kaut kas dziļāk iesmējās pretī.',
            'Ja redzi klintī rievas kā nagus, kas vilkti no iekšpuses, griezies atpakaļ, pirms tas iemācās tavu soli.',
        ],
    },
    {
        'title': 'Piezīme 4: Mēs saskaitījām septiņus',
        'author': 'L. Silarajs',
        'min_room': 9,
        'text': [
            'Pēc šķelšanās pie applūdušajām kāpnēm mēs bijām palikuši tikai pieci.',
            'Pie nākamā ugunskura uz sienas saskaitījām septiņas ēnas.',
            'Neviens nerunāja. Nevajadzēja. Mēs visi redzējām, ka tās divas liekās kustas puselpu lēnāk nekā mēs.',
            'Dace pēc tam vairs negulēja. Viņa teica, ka ēnas pieliecas pie ausīm, kad liesma kļūst vājāka.',
            'No rīta bija seši guļammaisi. Neviens neatcerējās, ka būtu uztaisījis vēl vienu.',
        ],
    },
    {
        'title': 'Piezīme 5: Izsalkums bez mutes',
        'author': 'Brother Arnolds',
        'min_room': 12,
        'text': [
            'Es nācu šurp, lai pierādītu, ka dziļās vietas ir tikai senas pasaules kauju rētas.',
            'Es kļūdījos. Tā nav brūce. Tas ir izsalkums.',
            'Radības nesargā apakšējos kambarus. Tās tos baro.',
            'Katrs līķis, ko atstājām aiz sevis, bija pazudis, kad gājām tam koridoram garām vēlreiz. Ne kaulu. Ne drēbju. Tikai mitrs karstums.',
            'Ja virszeme šīs alas aizzīmogos, tad nevis, lai mūs nelaistu iekšā, bet lai šo izsalkumu nelaistu ārā.',
        ],
    },
    {
        'title': 'Piezīme 6: Mira uzrakstīja manu vārdu',
        'author': 'T. Ozols',
        'min_room': 15,
        'text': [
            'Mira nomira pirms trim kambariem. Es pats viņu apraku zem balta akmens pārkares.',
            'Šonakt atradu rakstītu ziņu uz sienas viņas rokrakstā.',
            'TOM NĀC ZEMĀK. DURVIS IR ATVĒRTAS.',
            'Burti vēl bija mitri. Tie smaržoja pēc dzelzs un veca lietus.',
            'Esmu aptinis rokas ar drānu, jo katru reizi, kad aizmiegu, mostos ar zemi zem nagiem.',
        ],
    },
    {
        'title': 'Piezīme 7: Tie valkā mūs',
        'author': 'nezināms',
        'min_room': 18,
        'text': [
            'Pazudušie nav miruši. Ne gluži.',
            'Es vienu no viņiem ieraudzīju tumsā, kad mana laterna izdzisa. Tam vēl bija Andra seja, bet smaids bija pārāk plats.',
            'Tas atdarināja viņa gaitu, klepu, pat to, kā viņš aiz bailēm pieskārās nazim pie jostas.',
            'Kad pasaucu viņa vārdu, viss pārējais tunelī apklusa, it kā pati ala gaidītu manu atbildi.',
            'Ja šeit lejā satiec kādu pazīstamu, neļauj viņam nostāties tev aiz muguras.',
        ],
    },
    {
        'title': 'Piezīme 8: Pēdējā lapa',
        'author': 'bez paraksta',
        'min_room': 22,
        'text': [
            'Kamēr tu šo lasi, tas jau zina, cik ātri tu elpo.',
            'Tas iemācās katru skrējēju pēc baiļu ritma. Pēc tam izdobt tuneļus šajā formā un gaida.',
            'Iepriekšējās piezīmes tika atstātas tev ar nolūku. Cerība aizceļo dziļāk par kliedzieniem.',
            'Apakšā nekad nav bijis ceļš ārā. Tikai ceļš uz iekšu.',
            'Ja šī lapa ir silta, negriezies apkārt. Tas nozīmē, ka esmu tuvu.',
        ],
    },
]

# Piezīmju izkritīšanas varbūtības
LORE_DROP_BASE_CHANCE = 0.07
LORE_DROP_ROOM_BONUS = 0.003
LORE_DROP_MAX_CHANCE = 0.16

# ============================================================
# Beigu bosa cīņas direktorija un mākslas faili
# ============================================================
FINAL_BOSS_DIR = os.path.join(BASE_DIR, 'final_boss_fight')
FINAL_BOSS_ARTS = {
    1: 'standing_up.txt',
    2: 'armored_enhanced_standing.txt',
    3: 'bloodysmilezoomed.txt',
    4: 'Sitting_interaction.txt',
}

# ============================================================
# Stāsta ievada lapas — katrai lapai ir attēls un teksta rindas
# ============================================================
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

# ============================================================
# Galvenās izvēlnes ASCII māksla
# ============================================================
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
