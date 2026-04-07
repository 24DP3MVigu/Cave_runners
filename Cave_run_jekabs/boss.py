import random


def is_boss_room(room_number: int) -> bool:
    """Return True if the given room number is a boss room (every 10th room)."""
    return room_number > 0 and room_number % 10 == 0


def _base_stats_for_boss_index(index: int) -> dict:
    """Base stats that grow modestly with the boss index (1 for 10, 2 for 20, ...)."""
    # Keep bases conservative so scaling later can tune difficulty
    return {
        'hp': 80 + (index - 1) * 40,
        'attack': 12 + (index - 1) * 5,
        'defense': 6 + (index - 1) * 3,
        'xp_reward': 40 + (index - 1) * 20,
    }


 


def generate_boss(player: dict, room_number: int) -> dict:
    """Generate a boss dict scaled to the provided `player` and `room_number`.

    Returned dict matches the shape expected by the game's combat system:
    { 'name','hp','attack','defense','xp_reward', 'art'(optional) }
    """
    if not is_boss_room(room_number):
        raise ValueError('Room is not a boss room')

    boss_index = max(1, room_number // 10)
    bases = _base_stats_for_boss_index(boss_index)

    # Use base stats only (no player/XP multipliers). Add only light random variance.
    variance = random.uniform(0.96, 1.04)

    hp = max(10, int(bases['hp'] * variance))
    attack = max(1, int(bases['attack'] * (0.95 + random.random() * 0.1)))
    defense = max(0, int(bases['defense'] * (0.95 + random.random() * 0.1)))
    xp_reward = max(5, int(bases['xp_reward']))

    name = f"Boss_{boss_index}"

    return {
        'name': name,
        'hp': hp,
        'attack': attack,
        'defense': defense,
        'xp_reward': xp_reward,
    }


def boss_special_action(boss: dict, player: dict) -> dict:
    """Decide a boss special action for a single turn.

    Returns a dict with keys:
    - 'type': 'attack'|'special'|'defend'
    - 'value': numeric effect (damage or defense boost)
    - 'text': short description
    """
    boss_power = (boss.get('attack', 10) + boss.get('hp', 50) / 20)
    p_level = max(1, player.get('level', 1))
    boss_index = 1
    try:
        boss_index = int(boss.get('name', '').split('_')[-1])
    except Exception:
        boss_index = 1

    # Probability of special increases slightly with boss index and player level
    special_chance = min(0.35, 0.08 * boss_index + 0.01 * p_level)

    if random.random() < special_chance:
        # Choose from charge (high damage) or fortify (boost defense this turn)
        if random.random() < 0.6:
            damage = max(1, int(boss_power * random.uniform(1.1, 1.8)))
            return {
                'type': 'special',
                'value': damage,
                'text': f"{boss['name']} izmanto Īpašo Uzbrukumu un nodara {damage} damage!"
            }
        else:
            buff = max(1, int(boss.get('defense', 0) * random.uniform(0.8, 1.6)))
            return {
                'type': 'defend',
                'value': buff,
                'text': f"{boss['name']} pastiprina aizsardzību par {buff}!"
            }

    # Normal attack
    damage = max(1, int(boss.get('attack', 10) * random.uniform(0.8, 1.25)))
    return {
        'type': 'attack',
        'value': damage,
        'text': f"{boss['name']} uzbrūk un nodara {damage} damage."
    }


def boss_intro_text(boss: dict) -> str:
    """Return a short intro string for the boss room."""
    return f"Tu nonāci boss telpā — {boss.get('name')} parādās!"


__all__ = [
    'is_boss_room',
    'generate_boss',
    'boss_special_action',
    'boss_intro_text',
]
