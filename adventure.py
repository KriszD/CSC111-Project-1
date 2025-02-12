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
import copy  #NEW
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

        self._locations, self._items, self._puzzles = self._load_game_data(game_data_file)

        self.current_location_id = initial_location_id
        self.ongoing = True
        self.submitted = False

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
            location_obj = Location(loc_data['id'], loc_data['name'], loc_data['brief_description'],
                                    loc_data['long_description'], loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:  # Go through each element associated with the 'items' key in the file
            item_obj = Item(item_data['id'], item_data['name'], item_data['description'], item_data['status'],
                            item_data['combination'])
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

        >>> game = AdventureGame('game_data.json', 1)
        >>> game.get_location()
        Location(id=1, name='John P. Robarts Research Library, Floor 14', brief_description='After a long elevator ride, you arrive on the 14th floor of Robarts. The floor is filled with students cramming for their midterms, and there is not even one single seat available.', long_description='After a long journey, you finally reach the 14th floor. When you open the door, the overwhelming sound of silence hits you. It is perfectly silent, not even one person talking. Every seat is taken, and everyone is working on their tablets and laptops, clearly studying for their midterms. You gaze outside and you see the whole of the UofT campus, you know all your items are out there, ready for you to find. You walk around on your tiptoes, so as to not make even a single sound. As you walk around, you see many outlets both on the tables, as well as on the walls, where many students are charging their devices to keep their grind going.', available_commands={'go south': 4, 'go east': 2, 'charge laptop': 1}, items=[''], visited=False)

        >>> game.get_location(2)
        Location(id=2, name='St. George Subway Station', brief_description='You enter St. George Subway Subway Station, and arrive on the Line 1 platform. The northbound subway car just left, but you see the southbound subway car arriving now, with its doors opening. You could get on, should you have access to it.', long_description="You arrive at the St. George Subway Station. You enter from the St. George Street entrance and arrive on the Line 1 platform. You see lots of people getting off the subway car, some heading up the stairs, some heading down the stairs onto the Line 2 platform. The floors are surprisingly clean, and you smell a strong scent of lavender. 'How delicious', you think to yourself. You see the Southbound subway car arrive on the platform, and its doors are open. You could get on, should you have access to use it.", available_commands={'go south': 5, 'go west': 1, 'go east': 3, 'take subway': 9, 'play ddakji': 2}, items=[''], visited=False)
        """

        if loc_id is None:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def combine(self, player: Player) -> None:
        """Combine items if possible, printing a result message.

        >>> player = Player('user')
        >>> game = AdventureGame('game_data.json', 1)
        >>> game.combine(player)
        You don't have anything you can combine at the moment.
        """
        if not (self._items[2].status and self._items[3].status):
            if 3 in player.items and 4 in player.items:
                print("You put your G-Fuel in one hand, and your Lucky Mug in the other, "
                      "and you close your eyes and slam them together. When you open your eyes, "
                      "you have a mug full of G-Fuel!")
                player.items[3].status = True
                player.items[4].status = True
            elif 3 in player.items:
                print("Something to put in your Lucky Mug would be really great right now.")
            elif 4 in player.items:
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

        choice = input("\nEnter action: ").lower().strip()
        while choice not in ["yes", "no"]:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice == "yes":
            print("You submit your assignment in time. Congratulations, you won the game with",
                  player.remaining_turns, "turns left!")
        elif choice == "no":
            print("You decide not to submit your assignment... you fail it. Congratulations, you lost the game "
                  "with", player.remaining_turns, "turns left! "
                                                  "Your score was: ",
                  sum([item.status for item in self._items if item.status is True]), "out of 5")

    def save_game_state(self, player: Player, game_log: EventList) -> dict:
        """Return a snapshot (as a dictionary) of all mutable game state.

         >>> player = Player('user')
        >>> game = AdventureGame('game_data.json', 1)
        >>> game_log = []
        >>> snapshot = game.save_game_state(player, game_log)
        >>> isinstance(snapshot, dict)  # Check if the result is a dictionary
        True
        """
        return {
            'current_location_id': self.current_location_id,
            'ongoing': self.ongoing,
            'submitted': self.submitted,
            '_locations': copy.deepcopy(self._locations),
            '_items': copy.deepcopy(self._items),
            '_puzzles': copy.deepcopy(self._puzzles),
            'player_items': copy.deepcopy(player.items),
            'player_remaining_turns': player.remaining_turns,
            'game_log': copy.deepcopy(game_log)
        }

    def load_game_state(self, snapshot: dict, player: Player, game_log: EventList) -> None:
        """Restore the game state from the given snapshot dictionary.

        ChatGPT made this doctest.
        >>> # Create a game with initial location 1.
        >>> game = AdventureGame('game_data.json', 1)
        >>> player = Player('user')
        >>> game_log = EventList()
        >>> # Set player's remaining turns to a known value for testing.
        >>> player.remaining_turns = 10
        >>> # Save the current state.
        >>> snapshot = game.save_game_state(player, game_log)
        >>> # Change some of the game state.
        >>> game.current_location_id = 5
        >>> player.remaining_turns = 3
        >>> game.ongoing = False
        >>> # Check that the state has changed.
        >>> game.current_location_id
        5
        >>> player.remaining_turns
        3
        >>> game.ongoing
        False
        >>> # Now restore the state from the snapshot.
        >>> game.load_game_state(snapshot, player, game_log)
        >>> game.current_location_id
        1
        >>> player.remaining_turns
        10
        >>> game.ongoing
        True
        """
        self.current_location_id = snapshot['current_location_id']
        self.ongoing = snapshot['ongoing']
        self.submitted = snapshot['submitted']
        self._locations = snapshot['_locations']
        self._items = snapshot['_items']
        self._puzzles = snapshot['_puzzles']
        player.items = snapshot['player_items']
        player.remaining_turns = snapshot['player_remaining_turns']
        restored_log = snapshot['game_log']
        game_log.first = restored_log.first
        game_log.last = restored_log.last


if __name__ == "__main__":
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    player = Player('user')  # initializes the default player object

    menu = ["look", "inventory", "combine", "turns", "score", "undo", "log", "quit"]
    other_commands = ['charge laptop', 'take subway', 'return stone', 'pickup usb', 'pickup laptop charger']
    puzzle_commands = ['play ddakji', 'investigate podiums', 'pokemon battle', 'play tenjack']

    choice = None
    event = None

    ## NEW
    state_history = [game.save_game_state(player, game_log)]

    while game.ongoing:
        location = game.get_location()
        location.conditions(player, game._puzzles)

        #game_log.add_event(event, choice)

        print("You are now at:", location.name)
        if not location.visited:
            print(location.long_description)
            location.visited = True
        else:
            print(location.brief_description)

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

        # --- NEW EVENT LOGGING ---
        # Create an event that permanently records the command issued from the current location.
        new_event = Event(location.id, location.long_description, choice)
        game_log.add_event(new_event)
        # ---------------------------

        ## NEW
        # If the user wants to undo, revert immediately.
        if choice == 'undo':
            if len(state_history) > 1:
                state_history.pop()  # Remove the snapshot for the current state.
                game.load_game_state(state_history[-1], player, game_log)
                print("Undid the last move.")
                continue
            else:
                print("No moves to undo.")
                continue



        if choice in menu:
            if choice == "log":
                game_log.display_events()
            elif choice == 'look':
                print(location.long_description)
                player.remaining_turns -= 1
            elif choice == 'inventory':
                print([player.items[item].name for item in player.items])
                player.remaining_turns -= 1
            elif choice == 'combine':
                game.combine(player)
                player.remaining_turns -= 1
            elif choice == 'turns':
                print(player.remaining_turns)
            elif choice == 'score':
                print("Your score is:", sum([item.status for item in game._items if item.status is True]), "out of 5")
            # elif choice == 'undo':
            #     if len(state_history) > 1:
            #         # Remove the current state snapshot and load the one from before the last move.
            #         state_history.pop()  # remove snapshot for the current turn (not yet processed)
            #         load_game_state(state_history[-1], game, player, game_log)
            #         print("Undid the last move.")
            #         continue  # Skip further processing this turn.
            #     else:
            #         print("No moves to undo.")
            #         continue

            #game_log.remove_last_event()
            # TODO: undo should not log None, and maybe even not undo
            elif choice == 'quit':
                quit()

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result  # Changes the current location id to the updated one

            if choice in other_commands:
                if choice == 'charge laptop':
                    player.items[2].status = True
                elif choice == 'take subway':
                    pass
                elif choice == 'return stone':
                    player.items[5].status = True
                    player.items.pop(5)
                elif choice == 'pickup usb':
                    player.items[game._items[0].id] = game._items[0]
                    player.items[1].status = True
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
                    game._puzzles[4].ddakji(player)

        ## NEW
        state_history.append(game.save_game_state(player, game_log))

        #event = Event(location.id, location.long_description, None, None, game_log.last)

        if player.remaining_turns <= 0:
            print("You ran out of turns. Your score was:",
                  sum([item.status for item in game._items if item.status is True]), "out of 5")
            game.ongoing = False
        if all(item.status is True for item in game._items):  # Check if the user won the game.
            game.win()
