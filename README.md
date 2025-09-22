# Occupancy Monte Carlo

This repository contains the reproducible code and workflow for paper **MERCURY**:  
Monte Carlo simulation of **office and meeting room usage** in buildings, including optional **cancellation logic** and **probability mass functions (PMFs)** for meeting statistics.

---

##  Features

- Generate synthetic daily schedules for **offices** and **meeting rooms**
- Handle conflicts with optional **cancellation model**
- Export room usage data in two formats:
  - **Inference CSV**: room-level occupancy flags
  - **Optimisation CSV**: full occupancy table with maximum capacity and room cost
- Compute **PMFs**:
  - **Type III (Occupancy Data)**: includes headcounts
  - **Type IV (Occupied-only Data)**: ignores headcounts
- Visualise results with **Gantt charts**

---

##  Repository structure

```
.
├── ScheduleManager.py              # Base scheduler
├── ScheduleManager_cancel.py       # Scheduler with cancellations
├── Room.py                         # Room object definition
├── Employee.py                     # Employee object definition
├── Event.py                         # Event object definition
├── Schedule.py                      # Schedule object definition
├── Occupancy_Generator.ipynb       # Notebook to run simulations
├── Data/                           # Input/output data
│   ├── office_Num1.csv …           # Daily inference datasets
│   ├── office_Num1_Opt.csv …       # Daily optimisation datasets
│   ├── num_of_meetings.json        # Saved statistics
│   ├── num_of_people.json
│   └── duration_of_meetings_min.json
└── README.md                       # Project description (this file)
```

---

##  Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/andrewsjw0568/Occupancy_Monte_Carlo.git
cd Occupancy_Monte_Carlo
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies (minimum):

```
numpy
pandas
matplotlib
```

---

##  Quick start

### Generate a synthetic schedule

```python
from ScheduleManager import ScheduleManager
from PMF import PMF
from Event import Event
from Room import Room

# Define PMFs
meeting_durations_PMF   = PMF([30,60,90,120], [0.2,0.6,0.1,0.1])
number_of_employees_PMF = PMF([2,3,4,5],      [0.5,0.15,0.05,0.3])
number_of_meetings_PMF  = PMF([2,3,4,5],      [0.25,0.25,0.25,0.25])

# Initialise schedule manager
sm = ScheduleManager(office_rooms_list, meeting_rooms_list, employees_list)
sm.setup(
    filename_inference="Data/office_Num1.csv",
    filename_opt="Data/office_Num1_Opt.csv"
)
```

### Run with cancellation model

```python
from ScheduleManager_cancel import ScheduleManager as CancelSM
sm = CancelSM(office_rooms_list, meeting_rooms_list, employees_list)
cancelled = sm.setup("Data/office_Num1.csv", "Data/office_Num1_Opt.csv", simulation_day_index=1)
print(sm.cancel_rate_summary)  # Cancellation rates
```

---

##  Data exports

### Inference CSV
Columns:
- `Room` (Office XXX / Meeting room XXX)  
- `Time` (HH:MM)  
- `Occupied` (0/1 flag)  
- `Occupancy` (number of people)  
- `Max_occupancy` (capacity)


---

##  PMF utilities

### Type III (Occupancy Data)

```python
pmf_df = pmf(Schedule_df,
             Meeting_Room="Meeting room 100",
             method="Number_of_Meetings",
             Days=30)
```

- `Number_of_Meetings`: PMF of daily meeting counts (0..9 by default)
- `Number_of_People`: PMF of attendees per meeting (0..9 by default)
- `Duration`: PMF of meeting lengths in minutes (30..300, step 30)

### Type IV (Occupied Data)

```python
pmf4_df = pmf_4(Schedule4_df,
                Meeting_Room="Meeting room 101",
                method="Duration",
                Days=30)
```

- `Number_of_Meetings`: PMF of daily meeting counts
- `Duration`: PMF of meeting lengths in minutes

---

##  Room object parameters

When creating a room:

```python
Room(
  room_type_string, room_name_string,
  area_float, room_height_float, room_cost_per_area,
  max_meeting_occupancy_integer, max_office_occupancy_integer,
  meeting_durations_in_minutes_pmf,
  number_of_employees_in_event_pmf,
  number_of_meetings_in_room_pmf
)
```

Examples:

- **Office**:  
  `Room("Office", "00X", 2.3452, 2, 0.1, 0, 1, PMFs...)`  
- **Meeting room**:  
  `Room("Meeting room", "10X", 2.3452*5, 2, 0.1, 5, 0, PMFs...)`

---

##  Employee object parameters

The `Employee` class stores the employee’s personal details, assigned office, and associated schedules.

```python
Employee(
  employee_id_string,      # unique identifier for the employee
  role_string,             # role of the employee
  assigned_office_room     # reference to the assigned Office Room
)
```

Attributes:
- `events_schedule` → the employee’s meeting schedule
- `working_schedule` → planned working hours
- `actual_working` → realised working schedule (including absences)

Main methods:
- `add_event(new_event)` / `remove_event(event)` → modify meeting schedule
- `add_work_event(new_event)` / `remove_work_event(event)` → modify work schedule


---

##  Event object parameters

The `Event` class defines meetings or work activities, storing time, type, location, and participants.

```python
Event(
  start_time_datetime,   # start time
  end_time_datetime,     # end time
  event_type_string,     # type of event
  event_room,            # Room where the event takes place
  event_employees        # list of Employee objects
)
```

Main methods:
- `duration()` → compute duration of the event
- `is_overlap(event)` → check for overlap with another event
- `is_contained(event)` → check if fully contained in another event
- `is_before(event)` / `is_after(event)` → chronological ordering
- `add_employee(employee)` / `remove_employee(employee)` → update participants
- `print()` → display start and end time


---

##  Schedule object parameters

The `Schedule` class is a collection of `Event` objects with clash detection and basic operations.

```python
Schedule(
  events_list    # list of Event objects
)
```

Main methods:
- `get_number_of_events()` → return number of events
- `get_event(i)` → retrieve the i-th event
- `add_event(event)` / `remove_event(event)` → modify schedule
- `replace_event(current_event, new_event)` → update an event
- `is_clash(event)` → check if a new event overlaps with existing ones
- `is_contained(event)` → check containment
- `sort()` → order events chronologically
- `print()` → print all events in schedule


---

##  Reproducibility

- Fix random seeds for repeatable runs.
- Record PMF parameters used.
- Store raw CSVs in `Data/` for audit trail.
- Notebook `Occupancy_Generator.ipynb` contains worked examples.

---

##  Maintainers

- Dr James Andrews (@andrewsjw0568)  
- Lingfeng Wang (@Lingfeng-Wang)  
