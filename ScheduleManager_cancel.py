from Event import Event
from Schedule import Schedule
from datetime import datetime
from datetime import timedelta
import random
import math
import csv
import matplotlib.pyplot as plt
import json


class ScheduleManager:
    def __init__(self, office_rooms_list_input, meeting_rooms_list_input, employees_list_input):
        self.building_schedule = Schedule([])
        self.office_rooms_list = office_rooms_list_input
        self.meeting_rooms_list = meeting_rooms_list_input
        self.employees_list = employees_list_input

        self.number_of_rooms = len(office_rooms_list_input) + len(meeting_rooms_list_input)
        self.number_of_employees = len(employees_list_input)

        self.total_meetings = 0
        self.number_of_employees_in_meeting_list = []
        self.people_in_meetings_list = []
        self.number_of_meetings_in_rooms_list = []
        self.durations_of_meetings_in_minutes_list = []

        self.cancelled_events_list = []
        self.cancelled_count_per_room = {}
        self.cancelled_meetings = {}
        self.cancel_rate_summary = {}

    def setup(self, filename_inference, filename_opt, simulation_day_index=0):
        self.cancelled_events_list = []
        self.cancelled_count_per_room = {}
        self.cancelled_events_count = 0
        self.cancelled_meetings = {}
        max_number_of_attempts = 100

        self.number_of_meetings_and_durations()
        self.employees_in_meeting()

        start_of_day = 5
        work_hours_in_day = 18
        meeting_total_index = 0
        person_in_meeting_index = 0

        for meeting_room_index in range(len(self.meeting_rooms_list)):
            for meeting_index in range(self.number_of_meetings_in_rooms_list[meeting_room_index]):
                self.building_schedule.add_event(self.random_event(
                    self.meeting_rooms_list[meeting_room_index].working_schedule.get_event(0).start_time.hour,
                    work_hours_in_day,
                    self.durations_of_meetings_in_minutes_list[meeting_total_index],
                    self.meeting_rooms_list[meeting_room_index]
                ))
                for _ in range(self.number_of_employees_in_meeting_list[meeting_total_index]):
                    self.building_schedule.get_event(
                        self.building_schedule.get_number_of_events() - 1
                    ).add_employee(self.people_in_meetings_list[person_in_meeting_index])
                    person_in_meeting_index += 1
                meeting_total_index += 1

        self.remove_duplicate_employees()

        for event_index in reversed(range(self.building_schedule.get_number_of_events())):
            count = 0
            while (
                self.building_schedule.get_event(event_index).room.events_schedule.is_clash(self.building_schedule.get_event(event_index))
                or not self.building_schedule.get_event(event_index).room.working_schedule.is_contained(self.building_schedule.get_event(event_index))
            ):
                count += 1
                if count > max_number_of_attempts:
                    cancelled_event = self.building_schedule.get_event(event_index)
                    room = cancelled_event.room
                    room_name = room.room_name

                    self.cancelled_count_per_room[room_name] = self.cancelled_count_per_room.get(room_name, 0) + 1

                    cancelled_info = {
            'room_name': room_name,
            'start': cancelled_event.start_time.strftime("%Y-%m-%d %H:%M"),
            'end': cancelled_event.end_time.strftime("%Y-%m-%d %H:%M"),
            'duration_minutes': int((cancelled_event.end_time - cancelled_event.start_time).total_seconds() / 60),
            'employees': [e.employee_id for e in cancelled_event.employees],
            'reason': 'Time conflict',
            'day': simulation_day_index
        }
                    self.cancelled_meetings.setdefault("cancelled", []).append(cancelled_info)

                    self.building_schedule.remove_event(cancelled_event)
                    break

                current_event = self.building_schedule.get_event(event_index)
                new_event = self.random_event(
                    start_of_day,
                    work_hours_in_day,
                    self.durations_of_meetings_in_minutes_list[event_index],
                    current_event.room
                )
                new_event.employees = current_event.employees
                self.building_schedule.replace_event(current_event, new_event)

            if count > max_number_of_attempts:
                continue

            for employee_index in range(len(self.building_schedule.get_event(event_index).employees)):
                count = 0
                while (
                    self.building_schedule.get_event(event_index).employees[employee_index].events_schedule.is_clash(self.building_schedule.get_event(event_index))
                    or not self.building_schedule.get_event(event_index).employees[employee_index].working_schedule.is_contained(self.building_schedule.get_event(event_index))
                ):
                    count += 1
                    if count > max_number_of_attempts:
                        cancelled_event = self.building_schedule.get_event(event_index)
                        room = cancelled_event.room
                        room_name = room.room_name

                        self.cancelled_count_per_room[room_name] = self.cancelled_count_per_room.get(room_name, 0) + 1

                        cancelled_info = {
                            'room_name': room_name,
                            'start': cancelled_event.start_time.strftime("%Y-%m-%d %H:%M"),
                            'end': cancelled_event.end_time.strftime("%Y-%m-%d %H:%M"),
                            'duration_minutes': int((cancelled_event.end_time - cancelled_event.start_time).total_seconds() / 60),
                            'employees': [e.employee_id for e in cancelled_event.employees],
                            'reason': 'Employees conflict',
                            'day': simulation_day_index
                        }
                        self.cancelled_meetings.setdefault("cancelled", []).append(cancelled_info)

                        self.building_schedule.remove_event(cancelled_event)
                        break

                    replacement_employee = self.random_employee_duplicate(
                        self.building_schedule.get_event(event_index).employees[employee_index],
                        self.building_schedule.get_event(event_index).employees
                    )
                    self.building_schedule.get_event(event_index).employees[employee_index] = replacement_employee

                if count > max_number_of_attempts:
                    break

                self.building_schedule.get_event(event_index).employees[employee_index].add_event(
                    self.building_schedule.get_event(event_index)
                )

            if count <= max_number_of_attempts:
                self.building_schedule.get_event(event_index).room.add_event(
                    self.building_schedule.get_event(event_index)
                )




        # Assign employees to offices
        k = 0
        for office in self.office_rooms_list:
            for _ in range(office.max_office_occupancy):
                if k == self.number_of_employees:
                    break
                self.employees_list[k].assigned_office = office
                k += 1

        # Add placeholder lunch, arrival, departure events
        lunch_events, before_events, after_events = [], [], []
        for employee in self.employees_list:
            start_time = employee.working_schedule.get_event(0).end_time
            end_time = employee.working_schedule.get_event(1).start_time
            lunch_events.append(Event(start_time, end_time, "Lunch", None, [employee]))

            start_time = employee.working_schedule.get_event(0).start_time - timedelta(seconds=1)
            end_time = employee.working_schedule.get_event(0).start_time
            before_events.append(Event(start_time, end_time, "Arriving", None, [employee]))

            start_time = employee.working_schedule.get_event(1).end_time
            end_time = start_time + timedelta(seconds=1)
            after_events.append(Event(start_time, end_time, "Leaving", None, [employee]))

            employee.add_event(lunch_events[-1])
            employee.add_event(before_events[-1])
            employee.add_event(after_events[-1])

        # Sort meeting room and employee schedules
        for meeting_room in self.meeting_rooms_list:
            meeting_room.events_schedule.sort()

        for employee in self.employees_list:
            employee.events_schedule.sort()

        # Fill in office schedules with normal working periods
        for employee in self.employees_list:
            office = employee.assigned_office
            for event_index in range(1, len(employee.events_schedule.events)):
                start_time = employee.events_schedule.events[event_index - 1].end_time
                end_time = employee.events_schedule.events[event_index].start_time
                if start_time != end_time:
                    new_event = Event(start_time, end_time, "Normal working", office, [employee])
                    office.events_schedule.add_event(new_event)

        # Remove placeholder events from employee schedules
        for idx, employee in enumerate(self.employees_list):
            employee.remove_event(lunch_events[idx])
            employee.remove_event(before_events[idx])
            employee.remove_event(after_events[idx])

        # Add office events back to employee schedules
        for employee in self.employees_list:
            for event in employee.assigned_office.events_schedule.events:
                if employee in event.employees:
                    employee.add_event(event)

        # Final sorting of all schedules
        for employee in self.employees_list:
            employee.events_schedule.sort()

        for office in self.office_rooms_list:
            office.events_schedule.sort()

        # Write simulation output files
        self.inference_output_file(filename_inference, timedelta(minutes=15), datetime(2010, 1, 1, 5, 0, 0))
        self.optimization_output_file(filename_opt, datetime(2010, 1, 1, 5, 0, 0))

        # Save true meeting statistics
        self.true_number_of_meetings()
        self.true_number_of_people_in_meetings()
        self.true_duration_of_meetings()

        # Compute cancellation rates
        self.cancel_rate_summary = {}
        self.cancel_rate_summary["rates_per_room"], self.cancel_rate_summary["overall_rate"] = self.compute_cancellation_rates()

        # Save cancelled meeting statistics
        #with open('Data/cancelled_meetings.json', 'a') as file:
            #json.dump(self.cancelled_meetings, file, indent=2)
            #file.write('\n')

        #with open('Data/cancel_rate_summary.json', 'a') as file:
            #json.dump(self.cancel_rate_summary, file, indent=2)
            #file.write('\n')

        print("[DEBUG] Writing to JSON files...")
        print("Cancelled meeting count:", len(self.cancelled_meetings.get("cancelled", [])))
        print("Cancel rate:", self.cancel_rate_summary)

        #try:
            #with open('Data/cancelled_meetings.json', 'a') as file:
                #json.dump(self.cancelled_meetings, file, indent=2)
                #file.write('\n')
            #print("Cancelled meetings written successfully.")
        #except Exception as e:
            #print("Error writing cancelled_meetings.json:", e)

        try:
            with open('Data/cancel_rate_summary.json', 'a') as file:
                json.dump(self.cancel_rate_summary, file, indent=2)
                file.write('\n')
            print("Cancel rate summary written successfully.")
        except Exception as e:
            print("Error writing cancel_rate_summary.json:", e)
    
        return self.cancelled_meetings


    # --- NEW methods to get cancellation info and rates ---

    def get_cancelled_events(self):
        """
        Return the list of cancelled events with full details.
        """
        return self.cancelled_events_list

    def get_cancelled_count_per_room(self):
        """
        Return dictionary mapping room names to number of cancellations.
        """
        return self.cancelled_count_per_room

    def compute_cancellation_rates(self):
        """
        Compute per-room cancellation rates and overall cancellation rate.
        """
        rates_per_room = {}
        total_attempted = sum(self.number_of_meetings_in_rooms_list)
        total_cancelled = sum(self.cancelled_count_per_room.values())
        overall_rate = total_cancelled / total_attempted if total_attempted > 0 else 0

        for room in self.meeting_rooms_list:
            room_name = room.room_name
            attempted_in_room = self.number_of_meetings_in_rooms_list[self.meeting_rooms_list.index(room)]
            cancelled_in_room = self.cancelled_count_per_room.get(room_name, 0)
            rate = cancelled_in_room / attempted_in_room if attempted_in_room > 0 else 0
            rates_per_room[room_name] = rate

        return rates_per_room, overall_rate
    def set_number_of_meetings_in_room(self, pmf):
        """
        Sample the number of meetings for a room from its PMF.
        """
        prob = random.random()
        cdf = pmf.convert_pmf_values_to_cmf()
        sampled = -1
        for index in range(len(cdf) - 1):
            if not (prob < cdf[index]) & (prob < cdf[index + 1]):
                sampled = pmf.get_values(index)
        self.number_of_meetings_in_rooms_list.extend([sampled])
        return sampled

    def set_sample_pmf_values(self, pmf):
        """
        Sample a single value from a PMF.
        """
        prob = random.random()
        cdf = pmf.convert_pmf_values_to_cmf()
        sampled = -1
        for index in range(len(cdf) - 1):
            if not (prob < cdf[index]) & (prob < cdf[index + 1]):
                sampled = pmf.get_values(index)
        return sampled

    def random_event(self, start_of_day, work_hours_in_day, duration_of_meeting, room):
        """
        Generate a random meeting event with start and end times within working hours.
        """
        hour = self.randint(0, work_hours_in_day)
        half_hour = 30 * self.randint(0, 1)
        end_half_hour = math.floor((half_hour + duration_of_meeting) / 60)
        end_mins = half_hour + duration_of_meeting - 60 * end_half_hour

        if hour + end_half_hour + start_of_day > 23:
            hour = 22 - hour - end_half_hour

        start_time = datetime(2010, 1, 1, hour + start_of_day, half_hour, 0)
        end_time = datetime(2010, 1, 1, hour + end_half_hour + start_of_day, end_mins, 0)

        return Event(start_time, end_time, "Meeting", room, [])

    def find_duplicates(self, lst):
        """
        Find duplicate items in a list.
        """
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
        """
        Replace a duplicate employee with a random available employee not in the list.
        """
        replacement_employee = None
        no_repeats = True
        while no_repeats:
            no_repeats = False
            replacement_employee = self.employees_list[self.randint(0, self.number_of_employees - 1)]
            if replacement_employee is employee:
                no_repeats = True
            else:
                for employees in employee_list:
                    if replacement_employee is employees:
                        no_repeats = True
        return replacement_employee

    def remove_duplicate_employees(self):
        """
        Remove duplicate employees from each event's participant list.
        """
        for event_index in range(self.building_schedule.get_number_of_events()):
            duplicate_employees = self.find_duplicates(self.building_schedule.get_event(event_index).employees)
            if duplicate_employees:
                for employee in duplicate_employees:
                    replacement_employee = self.random_employee_duplicate(
                        employee,
                        self.building_schedule.get_event(event_index).employees
                    )
                    idx = self.building_schedule.get_event(event_index).employees.index(employee)
                    self.building_schedule.get_event(event_index).employees[idx] = replacement_employee

    def number_of_meetings_and_durations(self):
        """
        Sample number of meetings and their durations for each meeting room.
        """
        for meeting_room in range(len(self.meeting_rooms_list)):
            self.set_number_of_meetings_in_room(self.meeting_rooms_list[meeting_room].number_of_meetings_in_room_pmf)
            for _ in range(self.number_of_meetings_in_rooms_list[meeting_room]):
                self.durations_of_meetings_in_minutes_list.append(
                    self.set_sample_pmf_values(self.meeting_rooms_list[meeting_room].meeting_durations_in_minutes)
                )

    def employees_in_meeting(self):
        """
        Assign employees to meetings based on sampled number of attendees.
        """
        for meeting_room in range(len(self.meeting_rooms_list)):
            for _ in range(self.number_of_meetings_in_rooms_list[meeting_room]):
                number_of_people = self.set_sample_pmf_values(
                    self.meeting_rooms_list[meeting_room].number_of_employees_in_event
                )
                self.number_of_employees_in_meeting_list.append(number_of_people)
                for _ in range(number_of_people):
                    self.people_in_meetings_list.append(
                        self.employees_list[self.randint(0, self.number_of_employees - 1)]
                    )

    def inference_output_file(self, filename, timestep, time_now_start):
        """
        Write inference occupancy data to CSV for analysis.
        """
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Room", "Time", "Occupied", "Occupancy", "Max_occupancy"])
            for _ in range(73):
                time_now_end = time_now_start + timedelta(seconds=1)
                test_event = Event(time_now_start, time_now_end, None, None, None)
                for office in self.office_rooms_list:
                    in_room = False
                    person_count = 0
                    for event in office.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            person_count += 1
                    if in_room:
                        writer.writerow([
                            "Office " + str(office.room_name),
                            time_now_start.strftime("%H:%M"),
                            1, person_count,
                            office.max_office_occupancy
                        ])
                    else:
                        writer.writerow([
                            "Office " + str(office.room_name),
                            time_now_start.strftime("%H:%M"),
                            0, 0,
                            office.max_office_occupancy
                        ])
                for meeting_room in self.meeting_rooms_list:
                    in_room = False
                    for event in meeting_room.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            writer.writerow([
                                "Meeting room " + str(meeting_room.room_name),
                                time_now_start.strftime("%H:%M"),
                                1, len(event.employees),
                                meeting_room.max_meeting_occupancy
                            ])
                    if not in_room:
                        writer.writerow([
                            "Meeting room " + str(meeting_room.room_name),
                            time_now_start.strftime("%H:%M"),
                            0, 0,
                            meeting_room.max_meeting_occupancy
                        ])
                time_now_start += timestep

    def optimization_output_file(self, filename, time_now_start):
        """
        Write full occupancy data for optimization to CSV.
        """
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            header = ['Time']
            for room in self.office_rooms_list:
                header.append('Office')
            for room in self.meeting_rooms_list:
                header.append('Meeting room')
            writer.writerow(header)
            for _ in range(73):
                occupancy_list = [time_now_start.strftime("%H:%M")]
                time_now_end = time_now_start + timedelta(minutes=1)
                test_event = Event(time_now_start, time_now_end, None, None, None)
                for office in self.office_rooms_list:
                    in_room = False
                    person_count = 0
                    for event in office.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            if event.employees is not None:
                                person_count += 1
                    occupancy_list.append(person_count if in_room else 0)
                for meeting_room in self.meeting_rooms_list:
                    in_room = False
                    for event in meeting_room.events_schedule.events:
                        if event.is_contained(test_event):
                            in_room = True
                            occupancy_list.append(len(event.employees))
                    if not in_room:
                        occupancy_list.append(0)
                writer.writerow(occupancy_list)
                time_now_start += timedelta(minutes=15)
            max_occupancy_list = ['Maximum occupancy']
            for room in self.office_rooms_list:
                max_occupancy_list.append(room.max_office_occupancy)
            for room in self.meeting_rooms_list:
                max_occupancy_list.append(room.max_meeting_occupancy)
            writer.writerow(max_occupancy_list)
            room_cost_list = ['Room cost']
            for room in self.office_rooms_list + self.meeting_rooms_list:
                room_cost_list.append(95.39 * room.area)
            writer.writerow(room_cost_list)

    def randint(self, a, b):
        """
        Generate random integer in [a, b] inclusive.
        """
        U = random.random()
        X = a + math.floor((b - a + 1) * U)
        return X

    def true_number_of_people_in_meetings(self):
        """
        Save true number of people per meeting in JSON.
        """
        True_number_of_people = []
        for meeting_room in self.meeting_rooms_list:
            meeting_room.events_schedule.sort()
            True_number_of_people.append(meeting_room.events_schedule.number_of_people_in_meetings())
        with open('Data/num_of_people.json', 'a') as file:
            json.dump(True_number_of_people, file)
            file.write('\n')

    def true_duration_of_meetings(self):
        """
        Save true durations of meetings in JSON.
        """
        True_duration_of_meetings = []
        for meeting_room in self.meeting_rooms_list:
            meeting_room.events_schedule.sort()
            True_duration_of_meetings.append(meeting_room.events_schedule.duration_of_meetings())
        True_duration_of_meetings_min = [[td.total_seconds() / 60 for td in inner] for inner in True_duration_of_meetings]
        with open('Data/duration_of_meetings_min.json', 'a') as file:
            json.dump(True_duration_of_meetings_min, file)
            file.write('\n')

    def true_number_of_meetings(self):
        """
        Save true number of meetings per room in JSON.
        """
        True_number_of_meetings = []
        for meeting_room in self.meeting_rooms_list:
            meeting_room.events_schedule.sort()
            True_number_of_meetings.append(meeting_room.events_schedule.number_of_meetings())
        with open('Data/num_of_meetings.json', 'a') as file:
            json.dump(True_number_of_meetings, file)
            file.write('\n')

   
