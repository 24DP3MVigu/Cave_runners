import random

def calculate_damage(attacker_attack, defender_defense):
    """
    Aprēķina damage, ņemot vērā attack un defense.
    Formula:
        damage = attack - (defense / 2)
    Vienmēr vismaz 1 damage.
    """

    damage = attacker_attack - (defender_defense / 2)

    # Minimālais damage
    damage = max(1, int(damage))

    return damage


def calculate_critical(damage, crit_chance=0.15):
    """
    Kritiskais sitiens: 15% iespēja.
    Kritiskais sitiens = damage * 2
    """

    if random.random() < crit_chance:
        return damage * 2, True
    return damage, False


def final_damage(attacker_attack, defender_defense):
    """
    Pilns damage aprēķins:
    1) pamata damage (attack vs defense)
    2) kritiskais sitiens (ja notiek)
    """

    base_damage = calculate_damage(attacker_attack, defender_defense)
    dmg, crit = calculate_critical(base_damage)

    return dmg, crit
