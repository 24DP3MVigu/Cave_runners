def level_up(player):
    print("\n*** LEVEL UP! ***")
    player["level"] += 1
    points = 3

    print(f"Tu sasniedzi {player['level']} līmeni!")
    print(f"Tev ir {points} atribūtu punkti ko sadalīt.")

    while points > 0:
        print("\nIzvēlies, kur ieguldīt punktu:")
        print("1 - HP (+5 max_hp un +5 hp)")
        print("2 - Strength (+1)")
        print("3 - Defense (+1)")
        print(f"Atlikušie punkti: {points}")

        choice = input("Tava izvēle: ")

        if choice == "1":
            player["max_hp"] += 5
            player["hp"] = player["max_hp"]
            points -= 1
            print("HP palielināts!")
        elif choice == "2":
            player["strength"] += 1
            points -= 1
            print("Strength palielināts!")
        elif choice == "3":
            player["defense"] += 1
            points -= 1
            print("Defense palielināts!")
        else:
            print("Nederīga izvēle.")

    print("\nTavi jaunie stati:")
    print(player)
    return player
