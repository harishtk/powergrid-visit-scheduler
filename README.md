# PowerGrid Visit Scheduler

## Overview
We have successfully implemented the Scheduler Application with a Tkinter Graphical User Interface (GUI), matching your requirements. We preserved your core logic from `scheduler_demo.py` while creating a cohesive, dynamic UI wrapper in `gui_app.py`.

### Features
- **Dynamic Supervisors**: The UI allows defining any number of supervisors.
- **Dynamic Projects & Locations**: Full CRUD (Create/Read/Update/Delete) functionality for projects. Each project can have dynamic locations alongside their travel distances.
- **Fair Allocation Generation**: The core scheduling script logic is integrated directly. It takes the UI inputs and dynamically allocates locations to the supervisors such that their total accumulated distances are kept fair and balanced over the given months.

## Setup
A Python Virtual Environment (`.venv`) is recommended.

### Windows
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

3. Install requirements (requires `python-dateutil`):
   ```bash
   pip install python-dateutil
   ```

### Linux
We have provided an automated script for Ubuntu/Debian users.

1. Make the script executable:
   ```bash
   chmod +x run_linux.sh
   ```
2. Run the script:
   ```bash
   ./run_linux.sh
   ```
   *(This script will automatically create the virtual environment, install dependencies, and run the gui app.)*

## Running the Application (Windows)
You can execute the desktop app by running the main graphic script using the Python executable.

If using the virtual environment, simply run:
```bash
.venv\Scripts\python.exe gui_app.py
```

## Usage
1. Launch the app `gui_app.py`.
2. Inspect the **Supervisors** tab to see the pre-populated list and try adding/removing someone.
3. Switch to the **Projects** tab. Select the existing projects, examine their dates and locations. Try adding a new location.
4. Go to the **Generate Schedule** tab. The Date parameters are now auto-calculated based on your loaded projects. Click **Generate Schedule**.
5. Observe the tabular Treeview output which clearly lists the assignments per month and provides a neat **Cumulative Travel Distances Summary** table at the bottom, verifying that the assignments were balanced equitably.

## Developer Documentation: Scheduling Algorithm

The application uses a **Greedy Load Balancing Algorithm** combined with randomization to assign project locations to supervisors fairly.

### How it Works
1. **Time Iteration**: The scheduler iterates month-by-month from the start date to the end date.
2. **Active Locations Filter**: For each month, it filters all projects that are currently active (i.e., the current month falls between the project's start and end dates) and gathers their associated locations.
3. **Randomization**: The list of active locations for the month is shuffled randomly. This prevents deterministic assignment patterns (e.g., the same person always getting the first location in the list) and adds natural variation to the schedule.
4. **Greedy Assignment**: For each active location, the algorithm identifies the supervisor who currently has the **minimum cumulative travel distance**. It assigns the location to that supervisor.
5. **Accumulation**: The distance of the newly assigned location is added to the chosen supervisor's running total, and the process repeats for the next location.

This approach ensures that over the course of the schedule, travel burdens are continually balanced and distributed as equitably as possible among all available supervisors.

## Credits
Initiated & Ideated By: Navin S
Prompt By: Hariskumar K
AI Assistant: Antigravity (Google)
