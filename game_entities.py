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
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from typing import TYPE_CHECKING  # TODO: explain what this does
if TYPE_CHECKING:
    from assignments.project1.adventure import AdventureGame


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - id: The id of the location.
        - name: The name of the location.
        - brief_description: The brief description of the Location, played after the first or when the player 'looks'.
        - long_description: The long description of the Location, played on a player's first visit.
        - available_commands: The commands available to perform at this specific location.
        - items: The items found at this location.
        - visited: The status of whether the player has already visited this location or not.

    Representation Invariants:
        - len(name) > 0
        - len(brief_description) > 0
        - len(long_description) > 0
    """

    id: int
    name: str
    brief_description: str
    long_description: str
    available_commands: dict[str, int]
    items: list[Item]
    visited: bool

    def __init__(self, location_id: int, brief_description: str, long_description: str,
                 available_commands: dict[str, int], items: list[Item]) -> None:
        """Initialize a new location."""

        self.id = location_id
        self.brief_description = brief_description
        self.long_description = long_description
        self.available_commands = available_commands
        self.items = items
        self.visited = False

    def conditions(self, player: Player, puzzles: dict[int, Puzzle]) -> None:
        """Update available commands of each location based on necessary game conditions."""

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

        location_conditions = {
            1: lambda: add_command("charge laptop", 1) if has_item(2) else remove_command("charge laptop"),
            2: lambda: (
                add_command("take subway", 9) if puzzles[4].won else remove_command("take subway"),
                remove_command("play ddakji") if puzzles[4].won else None),
            3: lambda: remove_command("investigate podiums") if puzzles[1].won else None,
            4: lambda: (
                add_command("return stone", 4) if has_item(5) else remove_command("return stone"),
                remove_command("pokemon battle") if puzzles[2].won else None),
            5: lambda: remove_command("play blackjack") if puzzles[3].won else None,
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
        - combination: The id of the item that this item can be combined with, or None.

    Representation Invariants:
        - len(name) > 0
        - len(description) > 0
        - 1 <= start_position <= 9
    """

    id: int
    name: str
    description: str
    status: bool
    start_position: int
    combination: Optional[int] = None

    def __init__(self, item_id: int, name: str, description: str, status: bool,
                 start_position: int, combination: Optional[int] = None) -> None:
        """Initialize a new Item."""

        self.id = item_id
        self.name = name
        self.description = description
        self.status = status
        self.start_position = start_position
        self.combination = combination


@dataclass
class Puzzle:
    """A Puzzle in our text adventure game world.

    Instance Attributes:
        - id: The id of the puzzle.
        - name: The string name of the puzzle.
        - description: The instructions for the completion of the puzzle provided to the user.
        - available_commands: The commands available during the puzzle and their respective messages.
        - win_message: The message provided when the player completes the puzzle successfully.
        - lose_message: The message provided when the player completes the puzzle unsuccessfully.
        - won: The status of whether the player has already completed this puzzle successfully or not.

    Representation Invariants:
        - 1 <= id <= 4
        - len(name) > 0
        - len(description) > 0
        - len(win_message) > 0
        - len(lose_message) > 0
    """

    id: int
    name: str
    description: str
    available_commands: dict[str, str]
    win_message: str
    lose_message: str
    won: bool

    def __init__(self, puzzle_id: int, name: str, description: str, available_commands: dict[str, str],
                 win_message: str, lose_message: str) -> None:
        """Initialize a new Puzzle."""

        self.id = puzzle_id
        self.name = name
        self.description = description
        self.available_commands = available_commands
        self.win_message = win_message
        self.lose_message = lose_message
        self.won = False

    def rom_podiums(self, game: AdventureGame, player: Player) -> None:
        """Initializes and plays through the Rom Podiums Puzzle, a complex puzzle about CS riddles."""
        print(self.description)
        win_count = 0  # Track the number of solved riddles

        while not self.won:
            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()

            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            # Handle the actions based on available commands
            for command, riddle in list(self.available_commands.items()):
                if "inspect artifact" in command and choice == command:
                    print(f"Inspecting Artifact: {riddle}")

                elif "solve artifact" in command and choice == command:
                    answer = input(f"Enter answer for {command}: ").lower().strip()

                    # Check if the answer is correct
                    artifact_number = command.split()[2]  # Extract the artifact number (1, 2, 3, etc.)
                    correct_answer = self.available_commands[f"solve artifact {artifact_number} riddle"]
                    if answer == correct_answer:
                        print(self.win_message)
                        win_count += 1
                        self.available_commands.pop(command, None)  # Remove the command after solving
                    else:
                        print(self.lose_message)

            # Check win condition (all riddles solved)
            if win_count == 6:  # Completing all 6 necessary riddles
                print(self.available_commands["inspect main artifact"])
                answer = input("Enter answer for the main artifact riddle: ").lower().strip()
                if answer == self.available_commands["solve main artifact riddle"]:
                    print("'That is... correct! You may now have the Ancient Computer Scientist Stone.'")
                    player.items[game._items[4].id] = game._items[4]  # Give the user the Stone
                    self.won = True
                else:
                    print(self.lose_message)

    def pokemon_battle(self, game: AdventureGame, player: Player) -> None:
        """Initializes and plays through the Pokemon Battle Puzzle, a simple puzzle."""
        print(self.description)
        while not self.won:
            print("Your options are:")
            for action in self.available_commands:
                print("-", action)

            choice = input("\nEnter action: ").lower().strip()
            while choice not in self.available_commands:
                print("That was an invalid option; try again.")
                choice = input("\nEnter action: ").lower().strip()

            print("========")
            print("You decided to:", choice)

            if choice == "flamethrower":
                print(self.available_commands["flamethrower"])
            elif choice == "close combat":
                print(self.available_commands["close combat"])
            elif choice == "thunder punch":
                print(self.available_commands["thunder punch"])
                self.won = True
            elif choice == "earthquake":
                print(self.available_commands["earthquake"])
            elif choice == "bag":
                print(self.available_commands["bag"])
            elif choice == "run":
                print(self.available_commands["run"])

            if not self.won:
                print(self.lose_message)

        print(self.win_message)
        player.items[game._items[3].id] = game._items[3]  # Give the user the G-Fuel

    def blackjack(self, game: AdventureGame, player: Player) -> None:
        """Initializes and plays through the Blackjack Puzzle.
        Note, this Puzzle is hardcoded, and does not represent an actual game of Blackjack.
        """

    def ddakji(self) -> None:
        """Initializes and plays through the Ddakji Puzzle.
        Note, this Puzzle is relatively hardcoded.
        """


@dataclass
class Player:
    """A Player in our text adventure game world.

    Instance Attributes:
        - name: The name of the user playing the game.
        - items: A dictionary mapping item object ids to items that the user has obtained throughout their playthrough.
        - remaining_turns: The amount of remianing turns the player has in their playthrough.

    Representation Invariants:
        - len(name) > 0
        - remaining_turns > 0
    """

    name: str
    items: dict[int: Item]
    remaining_turns: int

    def __init__(self, name: str) -> None:
        """Initialize a new player."""

        self.name = name
        self.items = {}
        self.remaining_turns = 50


if __name__ == "__main__":
    pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })
