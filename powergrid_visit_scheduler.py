#! .venv/Scripts/python.exe

import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

#----------------------
# DEFAULT DATA
#----------------------
# global defaults for incharges and projects including distances.
DEFAULT_INCHARGES = ["I1", "I2", "I3", "I4", "I5"]
DEFAULT_PROJECTS = [
    {
        "name": "Project 1",
        "start": datetime(2026,3,1),
        "end": datetime(2026,5,31),
        "locations": [
            {"name": "A", "distance": 120},
            {"name": "B", "distance": 80},
            {"name": "C", "distance": 60}
        ]
    },
    {
        "name": "Project 2",
        "start": datetime(2026,3,1),
        "end": datetime(2027,2,28),
        "locations": [
            {"name": "D", "distance": 200},
            {"name": "E", "distance": 150}
        ]
    }
]

weeks = ["Week 1", "Week 2"]

#----------------------
# UTILITIES AND CORE LOGIC
#----------------------

def get_locations(date, projects):
    """Return a list of active location dicts with name and distance for the given date."""
    locs = []
    for p in projects:
        if p["start"] <= date <= p["end"]:
            # ensure each location is a dict with name and distance
            for l in p["locations"]:
                if isinstance(l, dict):
                    locs.append(l)
                else:
                    # backward compatibility: assume distance 0
                    locs.append({"name": l, "distance": 0})
    # eliminate duplicates by name
    seen = set()
    unique = []
    for l in locs:
        if l["name"] not in seen:
            seen.add(l["name"])
            unique.append(l)
    return unique


def generate_schedule(incharges, projects, start, end):
    """Creates a monthly schedule between start and end dates.

    The returned schedule is a dict keyed by month string. Each value is a
    list of assignment dicts with keys 'incharge', 'location', 'distance',
    and 'week'. Assignments are distributed such that cumulative travel
    distances remain as balanced as possible across incharges.
    """
    schedule = {}
    cum_distances = {i: 0 for i in incharges}
    current = start
    weeks = ["Week 1", "Week 2"]

    while current <= end:
        month = current.strftime("%B %Y")
        active_locations = get_locations(current, projects)
        assignments = []

        # shuffle to avoid deterministic order
        random.shuffle(active_locations)
        for loc in active_locations:
            # pick incharge with smallest cumulative distance
            incharge = min(cum_distances, key=cum_distances.get)
            assignments.append({
                "incharge": incharge,
                "location": loc["name"],
                "distance": loc.get("distance", 0),
                "week": random.choice(weeks)
            })
            cum_distances[incharge] += loc.get("distance", 0)

        schedule[month] = assignments
        current += relativedelta(months=1)

    return schedule

#----------------------
# EXAMPLE DATA / SCRIPT ENTRY POINT
#----------------------

def main():
    # use global defaults
    incharges = DEFAULT_INCHARGES
    projects = DEFAULT_PROJECTS
    schedule = generate_schedule(incharges, projects,
                                 datetime(2026,3,1), datetime(2027,2,1))
    for month, data in schedule.items():
        print("\n", month)
        print("-------------------------")
        for a in data:
            print(f"{a['incharge']} -> {a['location']} ( {a['week']} , {a['distance']} km)")


if __name__ == "__main__":
    main()

