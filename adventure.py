"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
import json
from typing import Optional
from game_entities import Location, Item, Puzzle, Player
from proj1_event_logger import Event, EventList


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The id of the current location that the user is at. By default, they start at position 1.
        - ongoing: The status of the condition of the game (whether it is ongoing or not)
        - submitted: Whether the user has submitted their assignment or not (one of the win conditions)

    Representation Invariants:
        - 1 <= current_location_id <= 9
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.
    #   - _puzzles: a mapping from puzzle id to Puzzle object.
    #                       This represents all the puzzles in the game.
    _locations: dict[int, Location]
    _items: list[Item]
    _puzzles: dict[int, Puzzle]
    current_location_id: int
    ongoing: bool
    submitted: bool

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        self._locations, self._items, self._puzzles = self._load_game_data(game_data_file)

        self.current_location_id = initial_location_id
        self.ongoing = True
        self.submitted = False

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item], dict[int, Puzzle]]:
        """Load locations and items from a JSON file with the given filename and return a tuple consisting of (1) a
        dictionary of locations mapping each game location's ID to a Location object, (2) a list of all Item objects,
        and (3) a dictionary of puzzles mapping each game puzzle's ID to a Puzzle object"""

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:  # Go through each element associated with the 'items' key in the file
            item_obj = Item(item_data['id'], item_data['name'], item_data['description'], item_data['status'],
                            item_data['start_position'], item_data['combination'])
            items.append(item_obj)

        puzzles = {}
        for puzzle_data in data['puzzles']:  # Go through each element associated with the 'puzzles' key in the file
            puzzle_obj = Puzzle(puzzle_data['id'], puzzle_data['name'], puzzle_data['description'],
                                puzzle_data['available_commands'], puzzle_data['win_message'],
                                puzzle_data['lose_message'])
            puzzles[puzzle_data['id']] = puzzle_obj

        return locations, items, puzzles

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        if loc_id is None:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def win_condition(self) -> None:
        """Returns whether the user has achieved all the objectives needed to win the game.
        """
        if all(item.status for item in game._items) and self.submitted:
            print('Congratulations! You won the game with', player.remaining_turns, 'turns remaining!')
            game.ongoing = False


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    player = Player('user')  # initializes the default player object

    menu = ["look", "inventory", "turns", "undo", "log", "quit"]
    other_commands = ['charge laptop', 'take subway', 'return stone', 'pickup usb', 'pickup laptop charger']
    puzzle_commands = ['play ddakji', 'investigate podiums', 'pokemon battle', 'play tenjack']
    choice = None
    event = None

    while game.ongoing:
        game.win_condition()
        location = game.get_location()
        location.conditions(player, game._puzzles)

        game_log.add_event(event, choice)

        if not location.visited:
            print(location.long_description)
            location.visited = True
        else:
            print(location.brief_description)

        print("What to do? Choose from: look, inventory, turns, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice in menu:
            if choice == "log":
                game_log.display_events()
            elif choice == 'look':
                print(location.long_description)
            elif choice == 'inventory':
                print([player.items[item].name for item in player.items])
            elif choice == 'turns':
                print(player.remaining_turns)
            elif choice == 'undo':
                game_log.remove_last_event()
                # TODO: undo should not log None, and maybe even not undo
            elif choice == 'quit':
                quit()

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result  # Changes the current location id to the updated one
            player.remaining_turns -= 1  # Decreases remaining turns

            if choice in other_commands:
                if choice == 'charge laptop':
                    player.items[2].won = True
                elif choice == 'take subway':
                    pass
                elif choice == 'return stone':
                    player.items.pop(5)
                    player.items[5].won = True
                elif choice == 'pickup usb':
                    player.items[game._items[0].id] = game._items[0]
                    player.items[1].won = True
                elif choice == 'pickup laptop charger':
                    player.items[game._items[1].id] = game._items[1]

            if choice in puzzle_commands:
                if choice == 'investigate podiums':
                    game._puzzles[1].rom_podiums(game, player)
                elif choice == 'pokemon battle':
                    game._puzzles[2].pokemon_battle(game, player)
                elif choice == 'play tenjack':
                    game._puzzles[3].tenjack(game, player)
                elif choice == 'play ddakji':
                    game._puzzles[4].ddakji()
        event = Event(location.id, location.long_description, None, None, game_log.last)
