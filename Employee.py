from Schedule import Schedule


class Employee:
    """
    * Employee class - Stores the employee personal details, their working schedule and their events schedule
    *
    * @author Dr. James Andrews
    * @version 0.1.0
    * @date 20/01/2023
    """
    def __init__(self, employee_id_string, role_string, assigned_office_room):
        """
        * @param  employee_id_string  the employee's employee identification
        * @param  role_string  the employee's role
        * @param  assigned_office_room  the office the employee is assigned to (if assigned offices)
        * @param  events_schedule  the employee's events
        * @param  working_schedule  the employee's working schedule (plan)
        * @param  actual_working_schedule  the employee's actual working schedule including non-attendance
        """
        self.employee_id = employee_id_string
        self.role = role_string
        self.assigned_office = assigned_office_room
        self.events_schedule = Schedule([])
        self.working_schedule = Schedule([])
        self.actual_working = Schedule([])

    def add_event(self, new_event):
        """
        * Adds an event to the employee's schedule
        *
        * @param  new_event  adds the event to the employee's schedule
        """
        self.events_schedule.add_event(new_event)

    def remove_event(self, event):
        """
        * Removes an event from the employee's schedule
        *
        * @param  event  removes the event from the employee's schedule
        """
        self.events_schedule.remove_event(event)

    def add_work_event(self, new_event):
        """
        * Adds an event to the employee's schedule
        *
        * @param  new_event  adds the event to the employee's schedule
        """
        self.working_schedule.add_event(new_event)

    def remove_work_event(self, event):
        """
        * Removes an event from the employee's schedule
        *
        * @param  event  removes the event from the employee's schedule
        """
        self.working_schedule.remove_event(event)
