from Schedule import Schedule


class Room:
    """
    * Room class - Keeps track of the room data
    *
    * @author Dr. James Andrews
    * @version 0.1.0
    * @date 20/01/2023
    """

    def __init__(self, room_type_string, room_name_string, area_float, room_height_float, room_cost,
                 max_meeting_occupancy_integer, max_office_occupancy_integer, meeting_durations_in_minutes_pmf,
                 number_of_employees_in_event_pmf, number_of_meetings_in_room_pmf):
        self.room_type = room_type_string  # Name of the room type
        self.room_name = room_name_string  # Name of the room
        self.area = area_float  # Area of the room
        self.room_height = room_height_float  # Height of the room
        self.room_cost_per_area = room_cost  # Room cost per unit area
        self.max_meeting_occupancy = max_meeting_occupancy_integer  # Max people for meeting occupancy
        self.max_office_occupancy = max_office_occupancy_integer  # Max people for office occupancy
        self.meeting_durations_in_minutes = meeting_durations_in_minutes_pmf  # Meeting durations in minutes PMF
        self.number_of_employees_in_event = number_of_employees_in_event_pmf  # Number of people in meetings PMF
        self.number_of_meetings_in_room_pmf = number_of_meetings_in_room_pmf  # Number of meetings in the room PMF
        self.events_schedule = Schedule([])  # Schedule of events
        self.working_schedule = Schedule([])  # Schedule of operating hours

    def add_event(self, new_event):
        """
        * Adds an event from the room's schedule
        *
        * @param  event  adds the event from the room's schedule
        """
        self.events_schedule.add_event(new_event)

    def remove_event(self, event):
        """
        * Removes an event from the room's schedule
        *
        * @param  event  removes the event from the room's schedule
        """
        self.events_schedule.remove_event(event)

    def add_event_working(self, new_event):
        """
        * Adds an event from the room's available uptime
        *
        * @param  event  adds the event from the room's schedule
        """
        self.working_schedule.add_event(new_event)

    def remove_event_working(self, event):
        """
        * Removes an event from the room's available uptime
        *
        * @param  event  removes the event from the room's schedule
        """
        self.working_schedule.remove_event(event)
