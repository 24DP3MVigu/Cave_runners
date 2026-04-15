"""
monstri.py — Monstru ielādes un ģenerēšanas sistēma.

Šajā failā tiek ielādēti monstri no CSV faila,
ielādēta to ASCII māksla un ģenerēti monstri cīņai.
"""

import os
import csv
import random
import sys

from iestatijumi import BASE_DIR


# ============================================================
# Monstru saraksta ielāde no CSV faila
# ============================================================

MONSTERS = []
_monsters_csv = os.path.join(BASE_DIR, 'monsters.csv')

try:
    with open(_monsters_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                MONSTERS.append({
                    'name': row['name'],
                    'hp': int(row['hp']),
                    'attack': int(row['attack']),
                    'defense': int(row['defense']),
                    'xp_reward': int(row['xp_reward']),
                })
            except Exception:
                # Izlaist bojātas rindas
                continue
except FileNotFoundError:
    print(f"Kļūda: monsters.csv nav atrasts — {_monsters_csv}")
    sys.exit(1)
except Exception as e:
    print(f"Kļūda, ielādējot monsters.csv: {e}")
    sys.exit(1)


# ============================================================
# Monstru ģenerēšana (ar ASCII mākslu un mērogošanu)
# ============================================================

def load_monster(player, boss: bool = False):
    """Atgriež monstru vārdnīcu ar statistiku un ASCII mākslu.

    - Ja boss=True, izvēlas tikai monstrus, kuru vārds ir LIELIEM BURTIEM.
    - Ja boss=False, izvēlas tikai parastos monstrus.
    Ja neviena kandidāta nav, izmanto visu sarakstu.
    """
    if boss:
        candidates = [m for m in MONSTERS if m.get('name', '').isupper()]
    else:
        candidates = [m for m in MONSTERS if not m.get('name', '').isupper()]

    if not candidates:
        candidates = MONSTERS

    monster = random.choice(candidates).copy()  # Kopēt, lai nemainītu oriģinālu

    # Sākotnējie precizitātes un flinch parametri
    monster['accuracy'] = 1.0
    monster['accuracy_duration'] = 0
    monster['flinch'] = 0

    # Mērogot statistiku atkarībā no uzvarēto bosu skaita (tikai parastajiem)
    if not boss and player.get('boss_wins', 0) > 0:
        scale_factor = 1 + 0.9 * player['boss_wins']
        monster['hp'] = int(monster['hp'] * scale_factor)
        monster['attack'] = int(monster['attack'] * scale_factor)
        monster['defense'] = int(monster['defense'] * scale_factor)

    # Ielādēt ASCII mākslu no Monstri mapes
    monstri_dir = os.path.join(BASE_DIR, 'Monstri')
    art_candidates = [
        os.path.join(monstri_dir, monster['name']),
        os.path.join(monstri_dir, f"{monster['name']}.txt"),
    ]
    # Mēģināt arī reģistrjutīgu meklēšanu (piem., fat_bat → Fat_bat.txt)
    try:
        dir_entries = os.listdir(monstri_dir)
        lower_map = {e.lower(): e for e in dir_entries}
        ci_match = lower_map.get(f"{monster['name'].lower()}.txt")
        if ci_match:
            art_candidates.append(os.path.join(monstri_dir, ci_match))
    except OSError:
        pass

    monster['art'] = None
    for art_path in art_candidates:
        try:
            with open(art_path, 'r', encoding='utf-8') as f:
                monster['art'] = f.read()
                break
        except FileNotFoundError:
            continue

    if monster['art'] is None:
        monster['art'] = f'Nav ASCII mākslas priekš {monster["name"]}'

    # Nodrošināt max_hp lauku HP joslas attēlošanai
    monster['max_hp'] = monster.get('hp', 0)
    return monster
