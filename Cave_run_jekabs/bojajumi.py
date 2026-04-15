"""
bojajumi.py — Bojājumu aprēķināšanas sistēma.

Šajā failā ir funkcijas, kas aprēķina uzbrukuma bojājumus,
kritiskos sitienus un gala bojājumu vērtību.
"""

import random


# ============================================================
# Bojājumu aprēķini
# ============================================================

def calculate_damage(attacker_attack, defender_defense):
    """Aprēķina pamata bojājumu: uzbrukums mīnus puse aizsardzības.
    Minimālais bojājums vienmēr ir 1."""
    damage = attacker_attack - (defender_defense / 2)
    damage = max(1, int(damage))
    return damage


def calculate_critical(damage, crit_chance=0.15):
    """Pārbauda, vai notiek kritiskais sitiens (15% iespēja pēc noklusējuma).
    Ja notiek — dubulto bojājumu."""
    if random.random() < crit_chance:
        return damage * 2, True
    return damage, False


def final_damage(attacker_attack, defender_defense):
    """Aprēķina gala bojājumu — kombinē pamata aprēķinu ar kritiskā sitiena pārbaudi.
    Atgriež (bojājums, vai_bija_kritiskais)."""
    base_damage = calculate_damage(attacker_attack, defender_defense)
    dmg, crit = calculate_critical(base_damage)
    return dmg, crit
