"""
grafika.py — ASCII mākslas renderēšana un HP joslu attēlošana.

Šajā failā ir funkcijas, kas mērogo un centrē ASCII mākslu,
attēlo HP joslas un apvieno vairākus attēlus blakus.
"""

from terminals import (
    get_terminal_width, get_terminal_size, center_ascii,
)


# ============================================================
# ASCII mākslas mērogošana
# ============================================================

def scale_ascii_art(text, max_width=None, max_height=None, allow_expand=False):
    """Mērogo ASCII mākslu, lai tā ietilptu terminālī.
    Ja allow_expand=True un terminālī ir daudz vietas, palielina attēlu."""
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

    # Palielināšana, ja terminālī ir pietiekami daudz vietas
    if allow_expand and max_width > orig_w and max_width >= orig_w * 1.3:
        expand_factor = int(max_width / orig_w)
        expand_factor = max(2, min(expand_factor, 3))
        scaled_lines = []
        for line in lines:
            expanded_line = ''.join(ch * expand_factor for ch in line)
            for _ in range(expand_factor):
                scaled_lines.append(expanded_line)
        return '\n'.join(scaled_lines)

    # Ja attēls jau ietilpst — neko nemaina
    if orig_w <= max_width:
        return '\n'.join(lines)

    # Samazināšana, lai ietilptu terminālī
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
    """Mērogo un centrē ASCII mākslu ekrānā."""
    scaled = scale_ascii_art(text, max_width=max_width, allow_expand=allow_expand)
    return center_ascii(scaled)


# ============================================================
# HP joslas attēlošana
# ============================================================

def display_hp_bar(current, max_hp, label="HP", centered=False):
    """Attēlo krāsainu HP joslu ar procentuālo aizpildījumu."""
    percentage = current / max_hp if max_hp > 0 else 0
    bar_length = 20
    filled = int(percentage * bar_length)
    bar = '█' * filled + '░' * (bar_length - filled)

    # Krāsa atkarībā no HP procentiem
    if percentage > 0.6:
        color = '\033[92m'   # zaļš
    elif percentage > 0.3:
        color = '\033[93m'   # dzeltens
    else:
        color = '\033[91m'   # sarkans

    reset = '\033[0m'
    line = f"{label}: {color}{bar}{reset} {current}/{max_hp}"
    if centered:
        print(line.center(get_terminal_width()))
    else:
        print(line)


# ============================================================
# Vairāku attēlu apvienošana blakus (izvēlnes pogām)
# ============================================================

def render_side_by_side(*arts, spacing=6):
    """Novieto vairākus ASCII attēlus blakus ar norādītu atstarpi."""
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
