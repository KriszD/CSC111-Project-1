"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
# Some of this code was written with the help of ChatGPT

from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id: The id of the location.
        - information: A tuple consisting of three things: the name of the location, the brief description
          of the Location, played after the first or when the player 'looks',
          and the long description of the Location, played on a player's first visit.
        - available_commands: The commands available to perform at this specific location.
        - items: The items found at this location.
        - visited: The status of whether the player has already visited this location or not.

    Representation Invariants:
        - all([len(info) > 0 for info in information])
        - len(available_commands) > 0
    """

    id: int
    information: tuple[str, str, str]  # name, brief description, long description
    available_commands: dict[str, int]
    items: list[Item]
    visited: bool

    def __init__(self, location_id: int, information: tuple[str, str, str],
                 available_commands: dict[str, int], items: list[Item]) -> None:
        """Initialize a new location.

        >>> location = Location(1, ('Forest', 'A dark forest', \
        'A thick and misty forest with tall trees.'), {'look': 1}, [])
        >>> location.information[0]
        'Forest'
        >>> location.visited
        False
        """
        self.id = location_id
        self.information = information
        self.available_commands = available_commands
        self.items = items
        self.visited = False

    def conditions(self, player: Player, puzzles: dict[int, Puzzle]) -> None:
        """Update available commands of each location based on necessary game conditions.

        >>> player = Player("Bob")
        >>> item = Item(1, "Laptop", "A shiny laptop", False)
        >>> puzzle = Puzzle(1, ("Puzzle", "Solve riddle"), {"look": "It's a riddle!"}, ("You solved it!", "Try again!"))
        >>> location = Location(1, ("Forest", "A dark forest", "A thick and misty forest."), {"look": 1}, [item])
        >>> location.conditions(player, {1: puzzle})
        >>> "charge laptop" in location.available_commands
        False
        """
        def has_item(item_id: int) -> bool:
            """Check if player has a specific item by its ID."""
            return item_id in player.items  # Check if the item_id exists as a key in the dictionary

        def add_command(command: str, value: int) -> None:
            """Add a command if not already present."""
            if command not in self.available_commands:
                self.available_commands[command] = value

        def remove_command(command: str) -> None:
            """Remove a command if present."""
            self.available_commands.pop(command, None)

        # Dictionary mapping location IDs to conditions that dynamically add/remove available commands
        # based on player statuses (items, puzzles, etc.).
        location_conditions = {
            1: lambda: add_command("charge laptop", 1) if has_item(2) and not player.items[2].status
            else remove_command("charge laptop"),
            2: lambda: (
                add_command("take subway", 9) if puzzles[4].won else remove_command("take subway"),
                remove_command("play ddakji") if puzzles[4].won else None),
            3: lambda: remove_command("investigate podiums") if puzzles[1].won else None,
            4: lambda: (
                add_command("return stone", 4) if has_item(5) else remove_command("return stone"),
                remove_command("pokemon battle") if puzzles[2].won else None),
            5: lambda: remove_command("play tenjack") if puzzles[3].won else None,
            7: lambda: remove_command("pickup usb") if has_item(1) else add_command("pickup usb", 7),
            8: lambda: remove_command("pickup laptop charger") if has_item(2) else add_command("pickup laptop charger",
                                                                                               8),
            9: lambda: (
                add_command("take subway", 2) if puzzles[4].won else remove_command("take subway"),
                remove_command("play ddakji") if puzzles[4].won else None),
        }

        # Execute the corresponding condition for the current location
        if self.id in location_conditions:
            location_conditions[self.id]()


@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - id: The id of the item.
        - name: The name of the item.
        - description: The description of the item.
        - status: The status of whether the item's condition to win has been met or not.
        - start_position: The starting position of the item on the grid.

    Representation Invariants:
        - len(name) > 0
        - len(description) > 0
        - 1 <= start_position <= 9
    """

    id: int
    name: str
    description: str
    status: bool

    def __init__(self, item_id: int, name: str, description: str, status: bool) -> None:
        """Initialize a new Item.

        >>> item = Item(1, "Laptop", "A shiny laptop", False)
        >>> item.name
        'Laptop'
        >>> item.status
        False
        """
        self.id = item_id
        self.name = name
        self.description = description
        self.status = status


@dataclass
class Player:
    """A Player in our text adventure game world.

    Instance Attributes:
        - name: The name of the user playing the game.
        - items: A dictionary mapping item object ids to items that the user has obtained throughout their playthrough.
        - remaining_turns: The amount of remaining turns the player has in their playthrough.

    Representation Invariants:
        - len(name) > 0
        - remaining_turns > 0
    """

    name: str
    items: dict[int: Item]
    remaining_turns: int

    def __init__(self, name: str) -> None:
        """Initialize a new player.

        >>> player = Player("Bob")
        >>> player.name
        'Bob'
        >>> player.remaining_turns
        50
        """
        self.name = name  # Never became used, was kept in case further modifications were made for
        # leaderboards, save files, etc.
        self.items = {}
        self.remaining_turns = 40  # Default turn max, shortest path to win takes 25 turns. Most players who tested
        # the game took around 30+, so 40 was fitting.


@dataclass
class Puzzle:
    """A Puzzle in our text adventure game world.

    Instance Attributes:
        - id: The id of the puzzle.
        - information: A tuple consisting of two things: the string name of the puzzle, and the instructions
          for the completion of the puzzle provided to the user.
        - available_commands: The commands available during the puzzle and their respective messages.
        - messages: A tuple consisting of two things: the message provided when the player completes the puzzle
          successfully, and the message provided when the player completes the puzzle unsuccessfully.
        - won: The status of whether the player has already completed this puzzle successfully or not.

    Representation Invariants:
        - 1 <= id <= 4
        - all([len(info) > 0 for info in information])
        - all([len(message) > 0 for message in messages])
    """

    id: int
    information: tuple[str, str]
    available_commands: dict[str, str]
    messages: tuple[str, str]
    won: bool

    def __init__(self, puzzle_id: int, information: tuple[str, str], available_commands: dict[str, str],
                 messages: tuple[str, str]) -> None:
        """Initialize a new Puzzle.

        >>> puzzle = Puzzle(1, ("Puzzle", "Solve riddle"), {"look": "It's a riddle!"}, ("You solved it!", "Try again!"))
        >>> puzzle.information[0]
        'Puzzle'
        >>> puzzle.won
        False
        """

        self.id = puzzle_id
        self.information = information
        self.available_commands = available_commands
        self.messages = messages
        self.won = False

    def rom_podiums(self, player: Player) -> None:
        """Initializes and plays through the Rom Podiums Puzzle, a complex puzzle about CS riddles."""

        main_artifact_commands = {
            "inspect main artifact": "I am a quite complex password. Guess me? You cannot."
                                     " 4 ordered numbers, I definitely am not.",
            "solve main artifact riddle": "1234"
        }

        # Remove main artifact commands initially
        self.available_commands.pop("inspect main artifact", None)
        self.available_commands.pop("solve main artifact riddle", None)

        print(self.information[1])
        win_count = 0  # Track the number of solved riddles

        while not self.won:
            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()

            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            if choice == 'exit puzzle':
                return

            if choice == "cheatcode":  # Since this game has randomness, add a cheatcode, so it can be won with 1 go
                player.remaining_turns -= 2  # Subtract 2 turns since you cheated :(
                print("Hello TA. You have used the cheatcode to bypass the Tenjack Puzzle. Congrats!")
                print(self.messages[0])
                self.won = True
                return

            # Delegate command handling
            if choice.startswith("inspect artifact") or choice.startswith("solve artifact"):
                win_count = self.handle_artifact(choice, player, win_count, main_artifact_commands)
            elif choice.startswith("inspect main artifact") or choice.startswith("solve main artifact"):
                self.handle_main_artifact(choice)

    def handle_artifact(self, choice: str, player: Player, win_count: int, main_artifact_commands: dict) -> int:
        """Handles artifact interactions, including inspecting and solving."""

        if choice.startswith("inspect artifact"):
            print(f"Inspecting Artifact: {self.available_commands[choice]}")

        elif choice.startswith("solve artifact"):
            artifact_number = choice.split()[2]
            answer = input(f"Enter answer for {choice}: ").lower().strip()
            correct_answer = self.available_commands.get(f"solve artifact {artifact_number} riddle")

            if answer == correct_answer:
                player.remaining_turns -= 1
                print(self.messages[0])
                win_count += 1

                # Remove the solved artifact commands
                self.available_commands.pop(choice, None)
                self.available_commands.pop(f"inspect artifact {artifact_number}", None)

                # Unlock main artifact commands when all riddles are solved
                if win_count == 6:
                    self.available_commands.update(main_artifact_commands)
            else:
                player.remaining_turns -= 1
                print(self.messages[1])

        return win_count

    def handle_main_artifact(self, choice: str) -> None:
        """Handles interactions with the main artifact."""

        if choice == "inspect main artifact":
            print(self.available_commands["inspect main artifact"])

        elif choice == "solve main artifact riddle":
            answer = input("Enter answer for the main artifact riddle: ").lower().strip()
            if answer == self.available_commands["solve main artifact riddle"]:
                print("'That is... correct! You may now have the Ancient Computer Scientist Stone.'")
                self.won = True
                self.available_commands.pop("solve main artifact riddle", None)
            else:
                print(self.messages[1])

    def pokemon_battle(self, player: Player) -> None:
        """Initializes and plays through the Pokémon Battle Puzzle, a simple puzzle."""
        print(self.information[1])
        while not self.won:
            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()
            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            if choice == 'exit puzzle':
                return

            if choice == "flamethrower":
                player.remaining_turns -= 1
                print(self.available_commands["flamethrower"])
                return
            elif choice == "close combat":
                player.remaining_turns -= 1
                print(self.available_commands["close combat"])
                return
            elif choice == "thunder punch":
                player.remaining_turns -= 1
                print(self.available_commands["thunder punch"])
                self.won = True
            elif choice == "earthquake":
                player.remaining_turns -= 1
                print(self.available_commands["earthquake"])
                return
            elif choice == "bag":
                print(self.available_commands["bag"])
                continue
            elif choice == "run":
                print(self.available_commands["run"])
                continue

            if not self.won:
                print(self.messages[1])

        print(self.messages[0])

    def tenjack(self, player: Player) -> None:
        """Initializes and plays through the Tenjack Puzzle."""
        cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        player_hand = []
        stand = False

        def hit(cards: list[int], hand: list[int]) -> None:
            """Gives the player an additional card."""
            card = random.choice(cards)
            hand.append(card)
            cards.remove(card)
            print(self.available_commands['hit'], hand[-1])
            print('You have:', sum(hand))

        print(self.information[1])
        hit(cards, player_hand)  # For the initial card given
        while not stand:
            if sum(player_hand) > 21:
                print('Your hand is over 21, therefore, you bust.')
                print(self.messages[1])
                return

            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()

            if choice == "cheatcode":  # Since this game has randomness, add a cheatcode, so it can be won with 1 go
                player.remaining_turns -= 2  # Subtract 2 turns since you cheated :(
                print("Hello TA. You have used the cheatcode to bypass the Tenjack Puzzle. Congrats!")
                print(self.messages[0])
                self.won = True
                return

            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            if choice == 'exit puzzle':
                return

            if choice == 'hit':
                hit(cards, player_hand)

            elif choice == 'stand':
                print(self.available_commands['stand'], sum(player_hand))
                stand = True

        dealer_hand = random.randint(15, 21)
        print('The dealer has a', dealer_hand)
        player.remaining_turns -= 1  # Subtract 1 turn no matter what the outcome
        if sum(player_hand) > dealer_hand:
            print(self.messages[0])
            self.won = True
        elif sum(player_hand) < dealer_hand:
            print(self.messages[1])
        else:
            print("'Tie, you have to play me again.'")

    def ddakji(self, player: Player) -> None:
        """Initializes and plays through the Ddakji Puzzle."""

        state = {
            'power': 'low',
            'hand': 'right',
            'side': 'up'
        }

        print(self.information[1])

        while not self.won:
            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()
            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            if choice == 'exit puzzle':
                return

            # Handle choice
            self.handle_ddakji_choice(choice, player, state)

    def handle_ddakji_choice(self, choice: str, player: Player, state: dict) -> None:
        """Handles the player's choice in the Ddakji puzzle."""

        if choice == 'current form':
            print(self.available_commands[choice], [state['power'], state['hand'], state['side']])

        elif choice.startswith("set "):
            self.update_ddakji_state(choice, state)

        elif choice == "throw":
            self.evaluate_throw(player, state)

    def update_ddakji_state(self, choice: str, state: dict) -> None:
        """Updates the Ddakji game state based on user input."""

        if "power" in choice:
            state['power'] = 'high' if "high" in choice else 'low'
        elif "hand" in choice:
            state['hand'] = 'left' if "left" in choice else 'right'
        elif "side" in choice:
            state['side'] = 'down' if "down" in choice else 'up'

    def evaluate_throw(self, player: Player, state: dict) -> None:
        """Evaluates the outcome of the throw."""

        if state['power'] == 'high' and state['hand'] == "right" and state['side'] == "down":
            player.remaining_turns -= 1
            self.won = True
            print(self.available_commands["throw"], self.messages[0])
        else:
            player.remaining_turns -= 1
            print(self.available_commands["throw"], self.messages[1])


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
