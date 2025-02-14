"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate an entire
playthrough of the game. Please consult the project handout for instructions and details.

You can copy/paste your code from the ex1_simulation file into this one, and modify it as needed
to work with your game.

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
from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["go east", "go south"])
        >>> len(sim._events) > 0
        True
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        locations, items, puzzles = self._game._load_game_data(game_data_file)

        # this is only to prevent PythonTA from complaining
        if items:
            pass
        if puzzles:
            pass

        # Access the correct Location object from the locations dictionary using the location ID
        location = locations[initial_location_id]

        # Add the first event with the initial location's long description
        new_event = Event(initial_location_id, location.information[2])
        self._events.add_event(new_event)

        # Generate subsequent events based on the commands
        self.generate_events(commands, self._game.get_location(initial_location_id))

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """Generate all events in this simulation.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["go east", "go south"])
        >>> len(sim._events) > 1
        True
        """

        curr_loc = current_location
        for command in commands:
            if command in curr_loc.available_commands:
                next_id = curr_loc.available_commands[command]
                curr_loc = self._game.get_location(next_id)
                self._events.add_event(Event(curr_loc.id, curr_loc.information[1], command, None, None))
            else:
                # Command is not a location command (likely a puzzle command); skip it.
                continue

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["go east"])
        >>> sim.get_id_log()
        [1, 2]

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["go south", "go south", "pickup usb"])
        >>> sim.get_id_log()
        [1, 4, 7, 7]
        """

        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and log location descriptions."""

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


def test_win_walkthrough() -> None:
    """Test a walkthrough of the adventure game where the actions are created so that the player wins"""
    win_walkthrough = ["go south", "pokemon battle", "thunder punch", "go south", "pickup usb", "go east",
                       "pickup laptop charger", "go north", "play tenjack", "cheatcode", "go north", "go east",
                       "investigate podiums", "solve artifact 1 riddle", "loop", "solve artifact 2 riddle", "list",
                       "solve artifact 3 riddle", "function", "solve artifact 4 riddle", "python",
                       "solve artifact 5 riddle", "recursion", "solve artifact 6 riddle", "tree",
                       "solve main artifact riddle", "1234", "go west", "go west", "charge laptop", "go south",
                       "return stone", "inventory", "combine", "yes"]
    expected_log = [1, 4, 4, 7, 7, 8, 8, 5, 5, 2, 3, 3, 2, 1, 1, 4, 4]
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log == sim.get_id_log()


def test_lose_demo() -> None:
    """Test a walkthrough of the adventure game where the actions are created so that the player loses"""
    lose_demo = [
        "go east", "go west", "go south", "pokemon battle", "flamethrower", "pokemon battle", "close combat",
        "pokemon battle", "thunder punch", "go east", "go east", "go north", "go west", "go west", "go south",
        "go south", "go north", "go south", "pickup usb", "go east", "go west", "go east", "go north",
        "go south", "pickup laptop charger", "go east", "go north", "go north", "go west", "go west",
        "go south", "go north", "charge laptop", "go south", "go south", "go east", "go north",
        "go north", "go west", "go east", "go south", "go east", "go north", "go south", "go west",
        "go north", "go west", "go south", "go east", "go east"
    ]
    expected_log = [1, 2, 1, 4, 4, 4, 4, 5, 6, 3, 2, 1, 4, 7, 4, 7, 7, 8, 7, 8, 5, 8, 8, 9,
                    6, 3, 2, 1, 4, 1, 1, 4, 7, 8, 5, 2, 1, 2, 5, 6, 3, 6, 5, 2, 1, 4, 5, 6]
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()


def test_inventory_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how the inventory system works"""
    inventory_demo = [
        "go south", "pokemon battle", "thunder punch", "go south", "pickup usb", "go east",
        "pickup laptop charger", "inventory"
    ]
    expected_log = [1, 4, 4, 7, 7, 8, 8]
    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()


def test_scores_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how the score system works"""
    scores_demo = [
        "go south", "go south", "pickup usb", "go east",
        "pickup laptop charger", "go north", "go north", "go west", "charge laptop", "score"
    ]
    expected_log = [1, 4, 7, 7, 8, 8, 5, 2, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()


def test_enhancement1_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how this enhancement works"""
    enhancement1_demo = [
        "go east", "go east", "investigate podiums", "inspect artifact 1", "solve artifact 1 riddle",
        "loop", "inspect artifact 2", "solve artifact 2 riddle", "list",
        "inspect artifact 3", "solve artifact 3 riddle", "function", "inspect artifact 4",
        "solve artifact 4 riddle", "python",
        "inspect artifact 5", "solve artifact 5 riddle", "recursion", "inspect artifact 6",
        "solve artifact 6 riddle", "tree",
        "inspect main artifact", "solve main artifact riddle", "1234", "inventory"
    ]
    expected_log = [1, 2, 3, 3]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement1_demo)
    assert expected_log == sim.get_id_log()


def test_enhancement2_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how this enhancement works"""
    enhancement2_demo = [
        "go south", "pokemon battle", "bag", "run", "close combat", "pokemon battle", "thunder punch",
        "inventory"
    ]
    expected_log = [1, 4, 4, 4]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement2_demo)
    assert expected_log == sim.get_id_log()


def test_enhancement3_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how this enhancement works"""
    enhancement3_demo = [
        "go south", "go east", "play tenjack", "cheatcode", "inventory"
    ]
    expected_log = [1, 4, 5, 5]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement3_demo)
    assert expected_log == sim.get_id_log()


def test_enhancement4_demo() -> None:
    """Demo a walkthrough of the adventure game where the actions display how this enhancement works"""
    enhancement4_demo = [
        "go east", "play ddakji", "observe tv", "read poster", "observe athlete", "eavesdrop",
        "observe book", "current form", "set high power", "set side down", "throw"
    ]
    expected_log = [1, 2, 2]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement4_demo)
    assert expected_log == sim.get_id_log()


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
