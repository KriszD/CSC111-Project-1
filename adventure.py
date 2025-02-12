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
# Some of this code was written with the help of ChatGPT
from __future__ import annotations
import json
import copy
from typing import Optional
from game_entities import Location, Item, Puzzle, Player
from proj1_event_logger import Event, EventList


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - items: a list of Item objects, representing all items in the game.
        - puzzles: a mapping from puzzle id to Puzzle object, representing all puzzles in the game.
        - current_location_id: The id of the current location that the user is at. By default, they start at position 1.
        - ongoing: The status of the condition of the game (whether it is ongoing or not)

    Representation Invariants:
        - 1 <= current_location_id <= 9
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    _locations: dict[int, Location]
    items: list[Item]
    puzzles: dict[int, Puzzle]
    current_location_id: int
    ongoing: bool

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file

        >>> game = AdventureGame('game_data.json', 1)
        >>> game.current_location_id
        1
        >>> game.ongoing
        True
        """

        self._locations, self.items, self.puzzles = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item], dict[int, Puzzle]]:
        """Load locations and items from a JSON file with the given filename and return a tuple consisting of (1) a
        dictionary of locations mapping each game location's ID to a Location object, (2) a list of all Item objects,
        and (3) a dictionary of puzzles mapping each game puzzle's ID to a Puzzle object

        >>> locations, items, puzzles = AdventureGame._load_game_data('game_data.json')
        >>> len(locations)
        9
        >>> len(items)
        5
        >>> len(puzzles)
        4
        """

        with open(filename, 'r', encoding='utf-8') as f:  # Got this encoding thing from ChatGPT, as it fixed our
            # JSON file encoding issue that we could not figure out how to fix ourselves.

            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            information = (loc_data['name'], loc_data['brief_description'], loc_data['long_description'])

            location_obj = Location(loc_data['id'], information, loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:  # Go through each element associated with the 'items' key in the file
            item_obj = Item(item_data['id'], item_data['name'], item_data['description'], item_data['status'])
            items.append(item_obj)

        puzzles = {}
        for puzzle_data in data['puzzles']:  # Go through each element associated with the 'puzzles' key in the file
            information = (puzzle_data['name'], puzzle_data['description'])
            messages = (puzzle_data['win_message'], puzzle_data['lose_message'])

            puzzle_obj = Puzzle(puzzle_data['id'], information, puzzle_data['available_commands'], messages)
            puzzles[puzzle_data['id']] = puzzle_obj

        return locations, items, puzzles

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.

        >>> game = AdventureGame('game_data.json', 1)
        >>> game.get_location(1).information[0]
        'John P. Robarts Research Library, Floor 14'

        >>> game.get_location(2).information[0]
        'St. George Subway Station'
        """

        if loc_id is None:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def combine(self, combine_player: Player) -> None:
        """Combine items if possible, printing a result message.

        >>> combine_player = Player('user')
        >>> game = AdventureGame('game_data.json', 1)
        >>> game.combine(combine_player)
        You don't have anything you can combine at the moment.
        """
        if not (self.items[2].status and self.items[3].status):
            if 3 in combine_player.items and 4 in combine_player.items:
                print("You put your G-Fuel in one hand, and your Lucky Mug in the other, "
                      "and you close your eyes and slam them together. When you open your eyes, "
                      "you have a mug full of G-Fuel!")
                combine_player.items[3].status = True
                combine_player.items[4].status = True
            elif 3 in combine_player.items:
                print("Something to put in your Lucky Mug would be really great right now.")
            elif 4 in combine_player.items:
                print("Something to put this G-Fuel in would be really great right now.")
            else:
                print("You don't have anything you can combine at the moment.")
        else:
            print("You have already combined the Lucky Mug with G-Fuel.")

    def win(self) -> None:
        """Determine if the player has won, prompting them for submission."""
        self.ongoing = False
        print("You have every single item you need. It is 1 minute before the deadline, do you submit "
              "your assignment? (yes, no)")

        win_choice = input("\nEnter action: ").lower().strip()
        while win_choice not in ["yes", "no"]:
            print("That was an invalid option; try again.")
            win_choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", win_choice)

        if win_choice == "yes":
            print("You submit your assignment in time. Congratulations, you won the game with",
                  player.remaining_turns, "turns left!")
        elif win_choice == "no":
            print("You decide not to submit your assignment... you fail it. Congratulations, you lost the game "
                  "with", player.remaining_turns, "turns left! "
                                                  "Your score was: ",
                  sum([item.status for item in self.items if item.status is True]), "out of 5")

    def save_game_state(self, save_player: Player, save_game_log: EventList) -> dict:
        """Return a snapshot (as a dictionary) of all mutable game state.

        >>> save_player = Player('user')
        >>> game = AdventureGame('game_data.json', 1)
        >>> save_game_log = []
        >>> snapshot = game.save_game_state(save_player, save_game_log)
        >>> isinstance(snapshot, dict)
        True
        """
        return {
            'current_location_id': self.current_location_id,
            'ongoing': self.ongoing,
            '_locations': copy.deepcopy(self._locations),
            'items': copy.deepcopy(self.items),
            'puzzles': copy.deepcopy(self.puzzles),
            'player.items': copy.deepcopy(save_player.items),
            'player_remaining_turns': save_player.remaining_turns,
            'game_log': copy.deepcopy(save_game_log)
        }

    def load_game_state(self, snapshot: dict, load_player: Player, load_game_log: EventList) -> None:
        """Restore the game state from the given snapshot dictionary.

        ChatGPT made this doctest.
        >>> game = AdventureGame('game_data.json', 1)
        >>> load_player = Player('user')
        >>> load_game_log = EventList()
        >>> load_player.remaining_turns = 10
        >>> snapshot = game.save_game_state(load_player, load_game_log)
        >>> game.current_location_id = 5
        >>> load_player.remaining_turns = 3
        >>> game.ongoing = False
        >>> game.current_location_id
        5
        >>> load_player.remaining_turns
        3
        >>> game.ongoing
        False
        >>> game.load_game_state(snapshot, load_player, load_game_log)
        >>> game.current_location_id
        1
        >>> load_player.remaining_turns
        10
        >>> game.ongoing
        True
        """
        self.current_location_id = snapshot['current_location_id']
        self.ongoing = snapshot['ongoing']
        self._locations = snapshot['_locations']
        self.items = snapshot['items']
        self.puzzles = snapshot['puzzles']
        load_player.items = snapshot['player.items']
        load_player.remaining_turns = snapshot['player_remaining_turns']
        restored_log = snapshot['game_log']
        load_game_log.first = restored_log.first
        load_game_log.last = restored_log.last


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    game_log = EventList()
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    player = Player('user')  # initializes the default player object

    menu = ["look", "inventory", "combine", "turns", "score", "undo", "log", "quit"]
    other_commands = ['charge laptop', 'take subway', 'return stone', 'pickup usb', 'pickup laptop charger']
    puzzle_commands = ['play ddakji', 'investigate podiums', 'pokemon battle', 'play tenjack']

    choice = None
    event = None

    state_history = [game.save_game_state(player, game_log)]

    last_location_id = game.current_location_id

    while game.ongoing:
        location = game.get_location()
        location.conditions(player, game.puzzles)

        if game.current_location_id != last_location_id:  # Don't repeat description if they didn't move
            print("You are now at:", location.information[0])
            if not location.visited:
                print(location.information[1])  # Brief description on first visit
                location.visited = True
            else:
                print(location.information[2])  # Long description after first visit
            last_location_id = game.current_location_id  # Update the last location
        # Do not print anything if the location has not changed

        print("What to do? Choose from: look, inventory, combine, turns, score, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        new_event = Event(location.id, location.information[2], choice)
        game_log.add_event(new_event)

        if choice in menu:
            if choice == "log":
                game_log.display_events()
            elif choice == 'look':
                print(location.information[2])
            elif choice == 'inventory':
                print([player.items[item].name for item in player.items])
            elif choice == 'combine':
                game.combine(player)
            elif choice == 'turns':
                print(player.remaining_turns)
            elif choice == 'undo':
                if len(state_history) > 1:
                    state_history.pop()  # Remove the snapshot for the current state.
                    game.load_game_state(state_history[-1], player, game_log)
                    print("Undid the last move.")
                    continue
                else:
                    print("No moves to undo.")
                    continue
            elif choice == 'score':
                print("Your score is:", sum([item.status for item in game.items if item.status is True]), "out of 5")
            elif choice == 'quit':
                quit()

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result  # Changes the current location id to the updated one
            player.remaining_turns -= 1

            if choice in other_commands:
                if choice == 'charge laptop':
                    player.items[2].status = True
                elif choice == 'take subway':
                    pass  # The available commands will move them using the TTC
                elif choice == 'return stone':
                    player.items[5].status = True
                    player.items.pop(5)
                elif choice == 'pickup usb':
                    player.items[game.items[0].id] = game.items[0]
                    player.items[1].status = True
                elif choice == 'pickup laptop charger':
                    player.items[game.items[1].id] = game.items[1]

            if choice in puzzle_commands:
                if choice == 'investigate podiums':
                    game.puzzles[1].rom_podiums(game, player)
                elif choice == 'pokemon battle':
                    game.puzzles[2].pokemon_battle(game, player)
                elif choice == 'play tenjack':
                    game.puzzles[3].tenjack(game, player)
                elif choice == 'play ddakji':
                    game.puzzles[4].ddakji(player)

        state_history.append(game.save_game_state(player, game_log))  # Log the game state for undoing purposes

        if player.remaining_turns <= 0:
            print("You ran out of turns. Your score was:",
                  sum([item.status for item in game.items if item.status is True]), "out of 5")
            game.ongoing = False
        if all(item.status is True for item in game.items):  # Check if the user won the game.
            game.win()
