from models import TimeSlot
from constraints import DAYS

# Create the time slots that we will add our events too
def create_time_slots():
    slots = []

    # Go from 8:00 am to 12:00 am
    start_hour = 8
    end_hour = 24

    for day in DAYS:
        current = start_hour * 60 # convert to minutes

        while current < end_hour * 60:
            slots.append(
                TimeSlot(
                    day=day,
                    start=current,
                    end=current + 10
                )
            )

            # Chose time slot size of 10 minutes because of polytime
            current += 10

    return slots