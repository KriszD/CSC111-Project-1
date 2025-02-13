"""CSC111 Project 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of this event's location
    - description: Long description of this event's location
    - next_command: String command which leads this event to the next event, None if this is the last game event
    - next: Event object representing the next event in the game, or None if this is the last game event
    - prev: Event object representing the previous event in the game, None if this is the first game event

    >>> event1 = Event(1, 'The first location', 'go north')
    >>> event2 = Event(2, 'The second location', 'go south')
    >>> event1.next = event2
    >>> event2.prev = event1
    >>> event1.id_num
    1
    >>> event1.description
    'The first location'
    >>> event1.next_command
    'go north'
    >>> event2.id_num
    2
    >>> event2.prev.id_num
    1
    >>> event2.next_command
    'go south'
    """

    id_num: int
    description: str
    next_command: Optional[str] = None
    next: Optional[Event] = None
    prev: Optional[Event] = None


class EventList:
    """
    A linked list of game events.

    Instance Attributes:
        - first: the first Game Event added to the EventList
        - last: the last Game Event added to the EventList

    Representation Invariants:
        - self.first is None == self.last is None

    >>> event_list = EventList()
    >>> event1 = Event(1, 'The first location', 'go north')
    >>> event_list.add_event(event1)
    >>> event_list.first.id_num
    1
    >>> event_list.add_event(Event(2, 'The second location', 'go south'))
    >>> event_list.last.id_num
    2
    >>> event_list.get_id_log()
    [1, 2]
    >>> event_list.remove_last_event()
    >>> event_list.get_id_log()
    [1]
    >>> event_list.remove_last_event()
    >>> event_list.is_empty()
    True
    """
    first: Optional[Event]
    last: Optional[Event]

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def __len__(self) -> int:
        """Return the number of events in the EventList."""
        count = 0
        current = self.first
        while current is not None:
            count += 1
            current = current.next  # Assuming Event has a 'next' attribute
        return count

    def display_events(self) -> None:
        """Display all events in chronological order.

        >>> event_list = EventList()
        >>> event1 = Event(1, 'The first location', 'go north')
        >>> event2 = Event(2, 'The second location', 'go south')
        >>> event_list.add_event(event1)
        >>> event_list.add_event(event2)
        >>> event_list.display_events()
        Location: 1, Command: go north
        Location: 2, Command: go south
        """
        print("---------------------------------")
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}")
            curr = curr.next
        print("---------------------------------")

    def is_empty(self) -> bool:
        """Return whether this event list is empty.

        >>> event_list = EventList()
        >>> event_list.is_empty()
        True
        >>> event1 = Event(1, 'The first location', 'go north')
        >>> event_list.add_event(event1)
        >>> event_list.is_empty()
        False
        """

        return self.first is None

    def add_event(self, event: Event) -> None:
        """Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.

        >>> event_list = EventList()
        >>> event1 = Event(1, 'The first location', 'go north')
        >>> event_list.add_event(event1)
        >>> event_list.first.id_num
        1
        >>> event_list.add_event(Event(2, 'The second location', 'go south'))
        >>> event_list.last.id_num
        2
        """
        if event is None:
            return
        elif self.is_empty():
            self.first = event
            self.last = event
        else:
            event.prev = self.last
            self.last.next = event
            self.last = event

    def remove_last_event(self) -> None:
        """Remove the last event from this event list.
        If the list is empty, do nothing.

        >>> event_list = EventList()
        >>> event1 = Event(1, 'The first location', 'go north')
        >>> event_list.add_event(event1)
        >>> event_list.remove_last_event()
        >>> event_list.is_empty()
        True
        >>> event_list.remove_last_event()
        >>> event_list.is_empty()
        True
        """

        if self.is_empty():
            return
        elif self.last.prev is None:
            self.first = None
            self.last = None
        else:
            self.last = self.last.prev
            self.last.next = None

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence.

        >>> event_list = EventList()
        >>> event1 = Event(1, 'The first location', 'go north')
        >>> event_list.add_event(event1)
        >>> event2 = Event(2, 'The second location', 'go south')
        >>> event_list.add_event(event2)
        >>> event_list.get_id_log()
        [1, 2]
        """

        ids = []
        curr = self.first

        while curr is not None:
            ids.append(curr.id_num)
            curr = curr.next
        return ids


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
