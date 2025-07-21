class Event:
    """
    * Event class stores the start time, end time and the meeting type
    *
    * @author Dr. James Andrews
    * @version 0.1.0
    * @date 20/01/2023
    """
    def __init__(self, start_time_datetime, end_time_datetime, event_type_string, event_room, event_employees):
        self.start_time = start_time_datetime   # Start date and time of the event
        self.end_time = end_time_datetime       # End date and time of the event
        self.event_type = event_type_string     # Event type
        self.room = event_room                  # Event room
        self.employees = event_employees        # Employees in the event

    def duration(self):
        """
        * Determines the duration of the event
        *
        * @return    duration of the event
        """
        return self.end_time - self.start_time

    def is_overlap(self, event):
        """
        * Checks if there is an overlap of this event with another event
        *
        * @param  event  the event
        * @return    true if the event e overlaps with this event and false otherwise
        """
        return (self.start_time < event.end_time) & (event.start_time < self.end_time)

    def is_contained(self, event):
        """
        * Determines if the event is entirely contained within another event
        *
        * @param  event  the event
        * @return    true if the event is entirely contained within this event and false otherwise
        """
        return not(self.start_time > event.start_time) and not(self.end_time < event.end_time)

    def is_before(self, event):
        """
        * Determines if the event is before this event
        * @param event:
        * @return:    true if the event is before this event and false otherwise
        """
        return self.start_time < event.start_time

    def is_after(self, event):
        """
        * Determines if the event starts after this event
        *
        * @param event:
        * @return:      true if the event starts after this event and false otherwise
        """
        return self.start_time > event.start_time

    def print(self):
        """
        * Print the event start time and end time in yyyy-MM-dd HH:mm:ss format
        *
        """
        print(self.start_time, " - ", self.end_time)

    def add_employee(self, employee):
        """
        * Add employee to the event
        @param employee:  add the employee to the event
        """
        self.employees.append(employee)

    def remove_employee(self, employee):
        """
        * Remove the employee from the event
        * @param employee:  remove the employee from the event
        """
        self.employees.remove(employee)
