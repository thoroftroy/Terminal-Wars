# Imports
import random
import time
from colorama import Fore, Style
import os
import sys
import platform
import json
from datetime import datetime
import threading
import shutil
from packaging.version import Version

# Dictionaries
monster = { # This is a dictionary of all the monsters which will be used to create their stats
    "names": [],
    "base_health": 10,
    "base_damage": 1,
    "base_defense": 1,
    "base_accuracy": 50,
    "base_speed": 1,
}

monster_data = { # This is the dictionary that defines the current monster being fought
    "name": "placeholder_name",
    "max_health": 0,
    "health": 0,
    "damage": 0,
    "defense": 0,
    "accuracy": 0,
    "speed": 0,
    "id":0,
}

player_data = {
    "name": "placeholder_name",
    "max_health": 25,
    "health": 25,
    "damage": 5,
    "defense": 1,
    "accuracy": 50,
    "speed": 1,

    "coins": 0,
    "xp": 0,

    "inventory": [],
    "relics": [],
    "wishes": [],
    "pets": [],

    "difficulty": "normal",
    "reborn_used": 0,

    "is_dead": False,

    "berserker_level": 0
}

persistentStats = {
    # Location
    "floor": 0,
    "room": 0,
    "dungeon": 0,
    "biome": 0,
    # Monster info
    "monsters_killed": 0,
    "boss_fight_ready": False,
    # Other
    "current_version": "Unknown",
}

shop_data = { # Shop prices and other stats
    "health_cost": 2,
    "damage_cost": 5,
    "defense_cost": 4,
    "accuracy_cost": 2,
    "speed_cost": 1,

    "health_boost_factor": 7, # How much of each stat you get per purchase
    "damage_boost_factor": 5,
    "defense_boost_factor": 3,
    "accuracy_boost_factor": 2.5,
    "speed_boost_factor": 0.5,

    "cost_factor": 1.2, # Multiplied with price to increase shop cost

    "berserker_cost": 500, # Berserker level and cost, each level grants a x2 damage multiplier
    "berserker_kills": 250,
    "berserker_cost_factor": 5, # Multiplied with both kills and cost
    # Single use upgrades
    "eye_cost": 500, # Lets you see more monster stats
    "dice_cost": 1000, # Tips all RNG slightly in the player's favor
    "reaper_cost": 1500, # Heals the player more from kills
    "greed_cost": 2000, # Adds a chance to earn coins from killing anything
    "disruptor_cost": 5000, # Lets you peirce 70% of enemy shield
    "attractor_cost": 2500, # Makes portals much more common
}

# Drop table - the drops are procedurally generated
drop_table = {
    "names": [],
    "desc": [],
    "health_boost": [10,1000000],
    "damage_boost": [10,100000],
    "defense_boost": [10,10000],
    "accuracy_boost": [1,100],
    "speed_boost": [1,100],
}
# Wishes - the wishes are procedurally generated
wish_table = {
    "names": [],
    "desc": [],
    "health_boost": [1000,100000000],
    "damage_boost": [1000,10000000],
    "defense_boost": [1000,1000000],
}
# Relics - also procedurally generated, the multipliers are added then multiplied with the player stats
relic_table = {
    "names": [],
    "desc": [],
    "health_boost": [0.1,4],
    "damage_boost": [0.1,4],
    "defense_boost": [0.1,4],
}
pet_table = { # Only one pet can be equipped at a time, they are randomly generated
    "names": [],
    "desc": [],
    "health_boost": [10, 1000000],
    "damage_boost": [10, 100000],
    "defense_boost": [10, 10000],
    "accuracy_boost": [1, 100],
    "speed_boost": [1, 100],
}

# Global Variables
current_version = 0.1

# Idle management
last_user_action = time.time()
idle_lock = threading.Lock()

# Startup
startup_grace_period = True

# Save and load variables
current_save_name = ''
saved_games = []
global_save_path = ''
save_directory = "terminalwars/saves"
os.makedirs(save_directory, exist_ok=True)

# Helper Functions
def function_start():
    save_to_file()
    clear_screen()
    update_last_action()

def update_last_action(): # Updates the idle lockout timer
    with idle_lock:
        global last_user_action
        last_user_action = time.time()

def idle_checker_thread(): # The idle checker
    global last_user_action
    idle_timeout = 120  # The number of seconds before a timeout
    while True:
        time.sleep(1)
        with idle_lock:
            if time.time() - last_user_action >= idle_timeout:
                save_to_file()
                print(Fore.BLACK + "|")
                print(Fore.RED + "\nYou have been idle for too long!")
                print(Fore.GREEN + "Saving game...\n" + Fore.RED + "Exiting...")
                time.sleep(0.1)
                print(Style.RESET_ALL)
                os._exit(0)  # Should exit the entire program

def grace_period_timer():
    global startup_grace_period # Grace period timer: During the start of the program don't allow the tamagotchi or the gacha to do anything
    time.sleep(30)
    startup_grace_period = False

def rainbow_text(text): # sets a segment of text to be rainbow
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    return "".join(colors[i % len(colors)] + c for i, c in enumerate(text))

def clear_screen(): # Define the current os and clear screen properly
    print(Style.RESET_ALL)
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.system('clear')
    elif platform.system() == 'Windows':
        os.system('cls')

# Print/Stat Functions
def show_stats_screen(): # Prints all of the players recorded stats
    pass

def print_combat_stats(): # Prints the main stats screen during combat
    pass

def print_inventory(): # shows the players inventory screen
    pass

def print_relics(): # shows the players relics
    pass

def print_wishes(): # shows the players wishes
    pass

def print_shop(): # prints the main shop screen
    pass

def print_pet(): # shows the players pet management window
    pass

# Other Functions
def list_saved_files():  # lists saved files
    global global_save_path, player_data, current_save_name, current_version, save_directory
    files = os.listdir(save_directory)
    json_files = [f for f in files if f.endswith('.json')]
    active = []
    dead = []

    for file in json_files:
        try:
            with open(os.path.join(save_directory, file), 'r') as f:
                data = json.load(f)
                if data.get("persistentStats", {}).get("is_dead", False):
                    dead.append(file)
                else:
                    active.append(file)
        except Exception: # I know this is kind a broad exeption but like, it works
            continue

    print(Fore.CYAN + "Active Save Files:")
    for f in active:
        print("  " + f)
    print(Fore.RED + "\nDead Save Files:")
    for f in dead:
        print("  " + f)
    print(Style.RESET_ALL)

def save_to_file():  # Saves the file
    global global_save_path, player_data, current_save_name, current_version, save_directory, persistentStats
    player_data["name"] = os.path.splitext(current_save_name)[0]

    persistentStats["current_version"] = f"{current_version}"

    data = {
        "player_data": player_data,
        "persistentStats": persistentStats,
    }

    try:
        with open(global_save_path, "w") as f:
            json.dump(data, f, indent=4)
    except PermissionError as e:
        print(f"[SAVE ERROR] Permission denied: {global_save_path}")
        print("Try closing other programs, check OneDrive sync, or move the file out of protected folders.")
        input("Press Enter to exit.")
        sys.exit(1)


def load_from_file(filename):  # Load data from files
    global global_save_path, player_data, current_save_name, current_version, save_directory, persistentStats

    path = os.path.join(save_directory, filename)
    global_save_path = path

    try:
        with open(path, "r") as f:
            data = json.load(f)

        player_data.update(data.get("player", {}))
        persistentStats.update(data.get("persistentStats", {}))

        # Starts the idle checker
        idle_thread = threading.Thread(target=idle_checker_thread, daemon=True)
        idle_thread.start()

        # Grace period
        threading.Thread(target=grace_period_timer, daemon=True).start()

        print(Fore.GREEN + f"Loaded from {filename}")

        # Version check
        if "current_version" not in persistentStats:
            print(Fore.RED + "WARNING")
            print(Fore.RED + "This save file does not have a version number.")
            print(Fore.RED + "It may be from an old version of the game and may not load correctly.")
            print(Fore.RED + "Expect to have MAJOR compatability issues")
            print(Fore.RED + "These issues can be totally GAMEBREAKING")
            input(Fore.BLUE + "Press ENTER to continue...")
        elif persistentStats["current_version"] != f"{current_version}":
            print(Fore.RED + "WARNING")
            print(Fore.RED + "This save file is not from the current version of the game")
            print(Fore.RED + "This save is from " + Fore.MAGENTA + persistentStats["current_version"])
            print(Fore.RED + "Expect to have some minor compatability issues")

        return True

    except Exception as e:
        print(Fore.RED + f"\nError loading save '{filename}': {e}")
        print(Fore.RED + "Your save may be corrupted.")
        print(Fore.YELLOW + "If a backup exists, you can try restoring it by renaming:")
        print(Fore.CYAN + f"  {filename}.bak  →  {filename}")
        print(Fore.YELLOW + "Then restart the game.")
        print(Style.RESET_ALL)
        sys.exit(1)

def inventory(): # Inventory management
    pass

def relics(): # relic management
    pass

def pets(): # pet management
    pass

def reset_monster():
    pass

def monster_death_check(): # Manages what happens after the monster dies
    pass

def monster_attack(): # the mosnter's attack during combat
    pass

def player_death_check(): # Manages the player's death
    pass

def player_attack(): # the players attack during combat
    pass

# Main Functions
def combat(): # The main combat management
    while True: # Ensures the game is always in combat when it should be
        function_start() # Saves the game, clears the screen, prevents idle lockout
        print_combat_stats()

def shop(): # Manages the level ups/shop
    pass

def explore(): # Manages the exploration of biomes and such
    pass

def startup(): # the start up function
    global current_version, current_save_name, save_directory, global_save_path, saved_games, player_data
    clear_screen()
    print(Fore.YELLOW + f"Terminal Wars v{current_version} loaded!")
    print(Fore.BLUE + "What is your name? [Type existing name to load or new name to create a save]")
    list_saved_files()

    name_input = input(Fore.GREEN + "\n> ").strip().lower()
    if not name_input.endswith(".json"):
        name_input += ".json"

    current_save_name = name_input
    global_save_path = os.path.join(save_directory, current_save_name)

    saved_games = [f for f in os.listdir(save_directory) if f.endswith(".json")]

    if current_save_name in saved_games:
        success = load_from_file(current_save_name)
        if not success:
            print(Fore.RED + "Failed to load save.")
            print(Fore.BLUE + "Press ENTER to exit.") # TURN THIS INTO A HELPER FUNCTION
            input(Fore.GREEN + "> ")
            print(Style.RESET_ALL)
            sys.exit()
        if persistentStats.get("is_dead", False):
            show_stats_screen()
            print(Fore.RED + "\nThis character is dead. You must create a new one.\n")
            print(Fore.BLUE + "Press ENTER to exit")
            input(Fore.GREEN + "> ")
            print(Style.RESET_ALL)
            sys.exit()
    else:
        print(Fore.YELLOW + f"Creating new save file: {current_save_name}")

    if current_save_name not in saved_games:
        print(Fore.YELLOW + "Choose difficulty: Easy / Normal / Hard / Impossible")
        print(Fore.CYAN + "(Difficulty effects monster damage and starting xp)")
        choice = input(Fore.GREEN + "> ").strip().lower()

        if choice in ["easy", "eas"]:
            player_data["difficulty"] = "easy"
        elif choice in ["normal", "norm"]:
            player_data["difficulty"] = "normal"
        elif choice in ["hard", "drd"]:
            player_data["difficulty"] = "hard"
        elif choice in ["impossible", "imp"]:
            player_data["difficulty"] = "impossible"
        else:
            print(Fore.RED + f"No acceptable input selected, defaulting to {Fore.CYAN}normal")
            player_data["difficulty"] = "normal"  # Default to normal
        update_last_action()
        print(Fore.BLUE + f"Player has chosen {Fore.CYAN}{player_data['difficulty']}{Fore.BLUE} difficulty!")
        time.sleep(0.8)
    combat()


# Starts the program
if __name__ == "__main__":
    startup()


# Color Code
# ------------------------
# RED = Error, issue, damage, monster
# GREEN = Player things or inputs
# YELLOW = Information
# MAGENTA = Descriptions
# CYAN = Emphasis
# BLUE = Other ui
# RAINBOW = Special
