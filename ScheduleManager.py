from Event import Event
from Schedule import Schedule
from datetime import datetime
from datetime import timedelta
import random
import math
import csv
import matplotlib.pyplot as plt


class ScheduleManager:
    def __init__(self, office_rooms_list_input, meeting_rooms_list_input, employees_list_input):
        self.building_schedule = Schedule([])  # List of all events in the building
        self.office_rooms_list = office_rooms_list_input  # List of office_rooms
        self.meeting_rooms_list = meeting_rooms_list_input  # List of meeting rooms
        # self.all_rooms_list = self.office_rooms_list_input + self.meeting_rooms_list_input
        self.employees_list = employees_list_input  # List of employees
        self.number_of_rooms = len(office_rooms_list_input) + len(meeting_rooms_list_input)  # Just a number
        self.number_of_employees = len(employees_list_input)  # Number of employees
        self.total_meetings = 0  # Total meetings
        self.number_of_employees_in_meeting_list = []  # Integer list of the number of people in each meeting
        self.people_in_meetings_list = []  # List of people in meetings
        self.number_of_meetings_in_rooms_list = []  # List of integers with the number of meetings in each room
        self.durations_of_meetings_in_minutes_list = []  # List of integers for the duration of meetings in minutes

    def setup(self, filename_inference, filename_opt):
        # print("\nExperimental class setup:")
        # print("\nNumber of rooms " + str(self.number_of_rooms))
        # print("Number of employees " + str(self.number_of_employees))

        # 1) Determine the number of meetings in each room
        # self.number_of_meetings_in_rooms_list - contains the information
        # 2) Determine the meeting duration for each meeting
        # self.durations_of_meetings_in_minutes_list - contains the information
        self.number_of_meetings_and_durations()

        # print(self.number_of_meetings_in_rooms_list)
        # print(self.durations_of_meetings_in_minutes_list)

        # 3) Determine how many employees should attend each meeting
        # + 4) Randomly select employees to attend each meeting
        # self.number_of_employees_in_meeting_list - Number of employees in meeting
        # self.people_in_meetings_list - The employees in the meeting
        self.employees_in_meeting()

        # print(self.number_of_employees_in_meeting_list)
        # print(len(self.people_in_meetings_list))

        # 5) Randomly set start time for the events and create the events
        # Need to set these by using the room schedule and prevent scheduling meetings outside of that time frame

        # Take from the room uptime schedule
        start_of_day = 5
        work_hours_in_day = 18
        meeting_total_index = 0
        person_in_meeting_index = 0

        # Create draft events with people, note: these events are not assigned to the rooms or office at this point
        for meeting_room_index in range(len(self.meeting_rooms_list)):
            # print("Meeting room index:" + str(meeting_room_index))
            for meeting_index in range(self.number_of_meetings_in_rooms_list[meeting_room_index]):
                # print("Number of meetings in room:" + str())
                self.building_schedule.add_event(self.random_event(
                    self.meeting_rooms_list[meeting_room_index].working_schedule.get_event(0).start_time.hour,
                    work_hours_in_day, self.durations_of_meetings_in_minutes_list[meeting_total_index],
                    self.meeting_rooms_list[meeting_room_index]))
                # Add employees to the event
                for person_index in range(self.number_of_employees_in_meeting_list[meeting_total_index]):
                    # print(len(self.people_in_meetings_list))
                    # print(self.people_in_meetings_list[person_in_meeting_index])
                    # building_schedule[]
                    self.building_schedule.get_event(self.building_schedule.get_number_of_events() - 1).add_employee(
                        self.people_in_meetings_list[person_in_meeting_index])
                    person_in_meeting_index = person_in_meeting_index + 1
                meeting_total_index = meeting_total_index + 1

        max_number_of_attempts = 100
        # Remove duplicate employees
        self.remove_duplicate_employees()

        # Assign the events to the rooms and the employees and check the events don't clash
        for event_index in range(self.building_schedule.get_number_of_events()):
            # print(self.building_schedule.get_number_of_events())
            # print(event_index)
            # print(self.building_schedule.get_event(event_index).room.events_schedule.is_clash(self.building_schedule.get_event(event_index)))
            count = 0
            while self.building_schedule.get_event(event_index).room.events_schedule.is_clash(
                    self.building_schedule.get_event(event_index)) or not self.building_schedule.get_event(
                    event_index).room.working_schedule.is_contained(self.building_schedule.get_event(event_index)):
                # ("Clash:")
                # print(self.building_schedule.get_event(event_index).room.events_schedule.is_clash(self.building_schedule.get_event(event_index)))
                # print("Contained:")
                # print(self.building_schedule.get_event(event_index).room.working_schedule.is_contained(self.building_schedule.get_event(event_index)))
                count = count + 1
                if count > max_number_of_attempts:
                    print("Event can't be scheduled")
                    break   # Why not create a new event?
                # print("Room is unavailable for booking")
                # Try first to change the time of the meeting
                current_event = self.building_schedule.get_event(event_index)
                new_event = self.random_event(start_of_day, work_hours_in_day,
                                              self.durations_of_meetings_in_minutes_list[event_index],
                                              self.building_schedule.get_event(event_index).room)
                # Add the employees to the new_event
                new_event.employees = current_event.employees
                self.building_schedule.replace_event(current_event, new_event)
            # print(self.building_schedule.get_event(event_index).room.events_schedule.is_clash(self.building_schedule.get_event(event_index)))
            # print("Room is available for booking")
            # print("Event_index: " + str(event_index))
            if not count > max_number_of_attempts:
                for employee_index in range(len(self.building_schedule.get_event(event_index).employees)):
                    count = 0
                    while self.building_schedule.get_event(event_index).employees[employee_index].events_schedule.is_clash(self.building_schedule.get_event(event_index)) or not self.building_schedule.get_event(event_index).employees[employee_index].working_schedule.is_contained(self.building_schedule.get_event(event_index)):
                        # print("Employee is unavailable for booking")
                        # Try to assign a new employee also need to check that the employee is only in the list once
                        count = count + 1
                        if count > max_number_of_attempts:
                            # print("Event can't be scheduled")
                            break   # Why not create a new event instead???
                        replacement_employee = self.random_employee_duplicate(
                            self.building_schedule.get_event(event_index).employees[employee_index],
                            self.building_schedule.get_event(
                                event_index).employees)
                        self.building_schedule.get_event(event_index).employees[employee_index] = replacement_employee
                    if count <= max_number_of_attempts:
                        self.building_schedule.get_event(event_index).employees[employee_index].add_event(
                            self.building_schedule.get_event(event_index))
                if count <= max_number_of_attempts:
                    self.building_schedule.get_event(event_index).room.add_event(
                        self.building_schedule.get_event(event_index))

        # Assign employees to office - This should have already been done
        # print("Number of employees: " + str(len(self.employees_list)))
        # print("Number of offices: " + str(len(self.office_rooms_list)))
        k = 0
        for office in self.office_rooms_list:
            for i in range(office.max_office_occupancy):
                if k == self.number_of_employees:
                    break
                self.employees_list[k].assigned_office = office
                k = k + 1

        lunch_events = []
        before_events = []
        after_events = []

        for employee_index in range(len(self.employees_list)):
            # self.employees_list[employee_index].assigned_office = self.office_rooms_list[employee_index]
            start_time = self.employees_list[employee_index].working_schedule.get_event(0).end_time
            end_time = self.employees_list[employee_index].working_schedule.get_event(1).start_time
            lunch_events.append(Event(start_time, end_time, "Lunch", None, [self.employees_list[employee_index]]))
            start_time = self.employees_list[employee_index].working_schedule.get_event(0).start_time - timedelta(seconds=1)
            end_time = self.employees_list[employee_index].working_schedule.get_event(0).start_time
            before_events.append(Event(start_time, end_time, "Arriving", None, [self.employees_list[employee_index]]))
            start_time = self.employees_list[employee_index].working_schedule.get_event(1).end_time
            end_time = start_time + timedelta(seconds=1)
            after_events.append(Event(start_time, end_time, "Arriving", None, [self.employees_list[employee_index]]))
            self.employees_list[employee_index].add_event(lunch_events[len(lunch_events)-1])
            self.employees_list[employee_index].add_event(before_events[len(lunch_events)-1])
            self.employees_list[employee_index].add_event(after_events[len(lunch_events) - 1])

        # Sort all of the meeting room schedules
        for meeting_room in self.meeting_rooms_list:
            meeting_room.events_schedule.sort()

        # Sort all employee's schedules
        for employee in self.employees_list:
            employee.events_schedule.sort()

        # Set up the office schedules based on the events above
        for employee in self.employees_list:
            office = employee.assigned_office
            for event_index in range(1, len(employee.events_schedule.events)):
                start_time = employee.events_schedule.events[event_index-1].end_time
                end_time = employee.events_schedule.events[event_index].start_time
                if not start_time == end_time:
                    new_event = Event(start_time, end_time, "Normal working", office, [employee])
                    office.events_schedule.add_event(new_event)

        # Remove inserted events from employees
        for employee_index in range(len(self.employees_list)):
            self.employees_list[employee_index].remove_event(lunch_events[employee_index])
            self.employees_list[employee_index].remove_event(before_events[employee_index])
            self.employees_list[employee_index].remove_event(after_events[employee_index])

        # Add office events to employee events
        for employee in self.employees_list:
            for event in employee.assigned_office.events_schedule.events:
                in_event = False
                for event_employees in event.employees:
                    if employee == event_employees:
                        in_event = True
                if in_event:
                    employee.add_event(event)

        # Sort all the employee's schedules
        for employee in self.employees_list:
            employee.events_schedule.sort()

        # Sort all the office schedules
        for office in self.office_rooms_list:
            office.events_schedule.sort()

        # Write to csv file - For Lingfeng
        self.inference_output_file(filename_inference, timedelta(minutes=15), datetime(2010, 1, 1, 5, 00, 00))

        # Write to csv file - For Michal - Full occupancy
        self.optimization_output_file(filename_opt, datetime(2010, 1, 1, 5, 00, 00))

        self.print_sorted_all()

        # self.show_gantt()

    def set_number_of_meetings_in_room(self, pmf):
        # self.number_of_meetings_in_rooms_list.extend([self.randint(2, max_meeting_occupancy)])
        prob = random.random()
        cdf = pmf.convert_pmf_values_to_cmf()
        sampled = -1  # -1 should never be returned under normal circumstances
        for index in range(len(cdf) - 1):
            if not (prob < cdf[index]) & (prob < cdf[index + 1]):
                sampled = pmf.get_values(index)
        self.number_of_meetings_in_rooms_list.extend([sampled])
        return sampled

    def set_sample_pmf_values(self, pmf):
        prob = random.random()
        cdf = pmf.convert_pmf_values_to_cmf()
        sampled = -1  # -1 should never be returned under normal circumstances
        for index in range(len(cdf) - 1):
            if not (prob < cdf[index]) & (prob < cdf[index + 1]):
                sampled = pmf.get_values(index)
        return sampled

    def random_event(self, start_of_day, work_hours_in_day, duration_of_meeting, room):
        hour = self.randint(0, work_hours_in_day)
        half_hour = 30 * self.randint(0, 1)
        end_half_hour = math.floor((half_hour + duration_of_meeting) / 60)
        end_mins = half_hour + duration_of_meeting - 60 * end_half_hour

        # print("\nhour " + str(hour))
        # print("half_hour " + str(half_hour))
        # print("duration mins " + str(duration_of_meeting))
        # print("end_half_hour " + str(end_half_hour))
        # print("end_mins " + str(end_mins))
        # print("\nstart hour " + str(hour + start_of_day))
        # print("start half hour " + str(half_hour))
        # print("end hour " + str(hour + end_half_hour + start_of_day))
        # print("end half hour " + str(end_mins))

        # Create datetime objects
        if hour + end_half_hour + start_of_day > 23:
            hour = 22 - hour - end_half_hour
        start_time = datetime(2010, 1, 1, hour + start_of_day, half_hour, 00)
        end_time = datetime(2010, 1, 1, hour + end_half_hour + start_of_day, end_mins, 00)
        return Event(start_time, end_time, "Meeting", room, [])

    def find_duplicates(self, lst):
        duplicates = []
        count = {}
        for item in lst:
            if item in count:
                count[item] += 1
            else:
                count[item] = 1
        for item, freq in count.items():
            if freq > 1:
                duplicates.append(item)
        return duplicates

    def random_employee_duplicate(self, employee, employee_list):
        replacement_employee = None
        no_repeates = True
        while no_repeates:
            no_repeates = False
            replacement_employee = self.employees_list[self.randint(0, self.number_of_employees - 1)]
            if replacement_employee is employee:
                no_repeates = True
            else:
                for employees in employee_list:
                    if replacement_employee is employees:
                        no_repeates = True
        return replacement_employee

    def schedule_as_dictionary_format(self, schedule):
        tasks = []
        for event_index in range(schedule.get_number_of_events()):
            tasks.append((schedule.get_event(event_index).start_time.strftime("%H:%M"), schedule.get_event(event_index).end_time.strftime("%H:%M")))
        return tasks

    def gantt(self, tasks):
    # Create a figure and axis
        fig, ax = plt.subplots()

    # Set the y-axis limits and tick labels
        ax.set_ylim(0.5, len(tasks) + 0.5)
        ax.set_yticks(list(range(1, len(tasks) + 1)))
        ax.set_yticklabels(list(tasks.keys()))

    # Plot each task as a series of horizontal bars, shifted down by half their height
        for i, (task, segments) in enumerate(tasks.items()):
            for start, end in segments:
                height = 0.4
                ax.broken_barh([(self.to_minutes(start), self.to_minutes(end) - self.to_minutes(start))], (i + 1 - height / 2, height),
                               facecolors='blue')

    # Set the x-axis limits and tick labels
        ax.set_xlim(300, 1380)
        ax.set_xticks(range(300, 1380, 60))
        ax.set_xticklabels([self.to_time(minutes) for minutes in range(300, 1380, 60)])

    #    # Set the axis labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel('Employee')
        ax.set_title('Daily Schedule')
    #
    #    # Show the chart
        plt.show()

    def to_minutes(self, time_str):
        """Convert a time string in the format 'HH:MM' to minutes"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def to_time(self, minutes):
        """Convert minutes to a time string in the format 'HH:MM'"""
        hours, minutes = divmod(minutes, 60)
        return f'{hours:02d}:{minutes:02d}'

    def number_of_meetings_and_durations(self):
        for meeting_room in range(len(self.meeting_rooms_list)):
            self.set_number_of_meetings_in_room(self.meeting_rooms_list[meeting_room].number_of_meetings_in_room_pmf)
            print()
            for i in range(self.number_of_meetings_in_rooms_list[meeting_room]):
                self.durations_of_meetings_in_minutes_list.append(
                    self.set_sample_pmf_values(self.meeting_rooms_list[meeting_room].meeting_durations_in_minutes))

    def employees_in_meeting(self):
        for meeting_room in range(len(self.meeting_rooms_list)):
            for meeting_index in range(self.number_of_meetings_in_rooms_list[meeting_room]):
                number_of_people = self.set_sample_pmf_values(
                    self.meeting_rooms_list[meeting_room].number_of_employees_in_event)
                self.number_of_employees_in_meeting_list.extend([number_of_people])
                for people in range(number_of_people):
                    self.people_in_meetings_list.append(
                        self.employees_list[self.randint(0, self.number_of_employees - 1)])

    def remove_duplicate_employees(self):
        for event_index in range(self.building_schedule.get_number_of_events()):
            duplicate_employees = self.find_duplicates(self.building_schedule.get_event(event_index).employees)
            if not (len(duplicate_employees) == 0):
                # print("Duplicates employees exist")
                # print(duplicate_employees)
                for employee in duplicate_employees:
                    replacement_employee = self.random_employee_duplicate(employee, self.building_schedule.get_event(
                        event_index).employees)
                    self.building_schedule.get_event(event_index).employees[
                        self.building_schedule.get_event(event_index).employees.index(employee)] = replacement_employee

    def show_gantt(self):
        meeting_room_tasks = {}
        for meeting_room in self.meeting_rooms_list:
            tasks = self.schedule_as_dictionary_format(meeting_room.events_schedule)
            meeting_room_tasks[f"MR {meeting_room.room_name}"] = tasks

        office_room_tasks = {}
        for office_room in self.office_rooms_list:
            tasks = self.schedule_as_dictionary_format(office_room.events_schedule)
            office_room_tasks[f"O {office_room.room_name}"] = tasks

        # Would be good to colour code
        employee_tasks = {}
        for employee in self.employees_list:
            tasks = self.schedule_as_dictionary_format(employee.events_schedule)
            employee_tasks[f"Emp {employee.employee_id}"] = tasks

        self.gantt(meeting_room_tasks)
        self.gantt(office_room_tasks)
        self.gantt(employee_tasks)

    def print_sorted_all(self):
        for meeting_room in self.meeting_rooms_list:
            print("Meeting room: " + meeting_room.room_name)
            meeting_room.events_schedule.sort()
            meeting_room.events_schedule.print()

        for office_room in self.office_rooms_list:
            print("Office: " + office_room.room_name)
            office_room.events_schedule.sort()
            office_room.events_schedule.print()

        for employee in self.employees_list:
            print("Employee: " + str(employee.employee_id))
            employee.events_schedule.sort()
            employee.events_schedule.print()

    def optimization_output_file(self, filename, time_now_start):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow(["Room", "Time", "Occupied", "Occupancy", "Max_occupancy"])
            header = ['Time']
            for room in self.office_rooms_list:
                header.append('Office')
            for room in self.meeting_rooms_list:
                header.append('Meeting room')
            writer.writerow(header)
            for i in range(0, 73):
                occupancy_list = [time_now_start.strftime("%H:%M")]
                time_now_end = time_now_start + timedelta(minutes=1)
                test_event = Event(time_now_start, time_now_end, None, None, None)
                # for event in office.events_schedule.
                for office in self.office_rooms_list:
                    in_room = False
                    person_count = 0
                    for event in office.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            if event.employees is None:
                                in_room = False
                            else:
                                person_count = person_count + 1
                    if in_room:
                        occupancy_list.append(person_count)
                    else:
                        occupancy_list.append(0)
                for meeting_room in self.meeting_rooms_list:
                    in_room = False
                    for event in meeting_room.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            occupancy_list.append(len(event.employees))
                    if not in_room:
                        occupancy_list.append(0)
                writer.writerow(occupancy_list)
                time_now_start = time_now_start + timedelta(minutes=15)
            max_occupancy_list = ['Maximum occupancy']
            for room in self.office_rooms_list:
                max_occupancy_list.append(room.max_office_occupancy)
            for room in self.meeting_rooms_list:
                max_occupancy_list.append(room.max_meeting_occupancy)
            writer.writerow(max_occupancy_list)
            room_cost_list = ['Room cost']
            for room in self.office_rooms_list:
                room_cost_list.append(95.39 * room.area)
            for room in self.meeting_rooms_list:
                room_cost_list.append(95.39 * room.area)
            writer.writerow(room_cost_list)

    def inference_output_file(self, filename, timestep, time_now_start):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Room", "Time", "Occupied", "Occupancy", "Max_occupancy"])
            #
            # Now go through all available times
            #
            for i in range(0, 73):
                time_now_end = time_now_start + timedelta(seconds=1)
                test_event = Event(time_now_start, time_now_end, None, None, None)
                # for event in office.events_schedule.
                for office in self.office_rooms_list:
                    in_room = False
                    person_count = 0
                    for event in office.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            person_count = person_count + 1
                    if in_room:
                        writer.writerow(["Office " + str(office.room_name), time_now_start.strftime("%H:%M"), 1, person_count,
                                         office.max_office_occupancy])
                    else:
                        writer.writerow(
                            ["Office " + str(office.room_name), time_now_start.strftime("%H:%M"), 0, 0,
                             office.max_office_occupancy])

                for meeting_room in self.meeting_rooms_list:
                    in_room = False
                    for event in meeting_room.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            writer.writerow(
                                ["Meeting room " + str(meeting_room.room_name), time_now_start.strftime("%H:%M"), 1,
                                 len(event.employees), meeting_room.max_meeting_occupancy])
                    if not in_room:
                        writer.writerow(
                            ["Meeting room " + str(meeting_room.room_name), time_now_start.strftime("%H:%M"), 0, 0,
                             meeting_room.max_meeting_occupancy])
                time_now_start = time_now_start + timestep

    def randint(self, a, b):
        # Define the range of possible values
        # a Lower bound (inclusive)
        # b Upper bound (inclusive)

        # Sample a value from the distribution
        U = random.random()
        X = a + math.floor((b - a + 1) * U)
        return X
