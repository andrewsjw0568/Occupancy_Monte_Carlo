class Schedule:
    """
    * Schedule stores the events and perform checks on event clashes
    * and if one event is entirely contained within another event
    *
    * @author Dr. James Andrews
    * @version 0.1.0
    * @date 20/01/2023
    """

    def __init__(self, events_list):
        """
        * Constructor for objects of class Schedule
        *
        @param  events_list  a list of all events in the schedule
        """
        self.events = events_list

    def get_number_of_events(self):
        """
        * Gets the number of events in the schedule
        *
        * @return    the number of events in the schedule
        """
        return len(self.events)

    def get_event(self, i):
        """
        * Gets the event in the schedule at index i
        *
        * @param  i  the index of the event in the schedule
        * @return    the i-th event in the schedule
        """
        return self.events[i]

    def get_event_index(self, event):
        """
        * Gets the index of the event
        * @param  event  the event object
        * @return  the index of the event
        """
        return self.events.index(event)

    def add_event(self, new_event):
        """
        * Adds an event to the schedule
        *
        * @param  new_event  adds the new event to the schedule
        """
        self.events.extend([new_event])

    def remove_event(self, event):
        """
        * Removes an event from the schedule
        *
        * @param  event  removes the event from the schedule
        """
        self.events.remove(event)

    def replace_event(self, current_event, new_event):
        """
        * Replaces the current_event with the new_event, the current_event will be lost
        @param current_event:
        @param new_event:
        """
        self.events[self.get_event_index(current_event)] = new_event

    def is_clash(self, other_event):
        """
        * Checks if an event exists in the schedule that occurs at the same time (or partially) as the new event
        *
        * @param  other_event  checks if an event has a clash with existing events in the schedule
        * @return    true if there is an event clash and false if there is no event clash
        """
        for event in self.events:
            if event.is_overlap(other_event):
                return True
        return False

    def is_contained(self, other_event):
        """
        * Checks if an event is entirely contained within a schedule event
        *
        * @param  newEvent  checks if an event occurs entirely within events of an existing schedule event
        * @return    true if the event is entirely contained within existing events in the schedule
        *                  and false otherwise
        """
        for event in self.events:
            if event.is_contained(other_event):
                return True
        return False

    def print(self):
        """
        *  Prints the details of the schedule
        *
        """
        for event in self.events:
            if event is not None:
                event.print()

    def sort(self):
        """
        *  Sort the schedule with the earliest event first
        """
        sorted_events_list = []
        number_of_events = self.get_number_of_events()
        for i in range(number_of_events):
            for j in range(self.get_number_of_events()):
                if j == 0:
                    earliest_event = self.events[j]
                elif earliest_event.is_after(self.events[j]):
                    earliest_event = self.events[j]
            sorted_events_list.append(earliest_event)
            self.events.remove(earliest_event)
        self.events = sorted_events_list
