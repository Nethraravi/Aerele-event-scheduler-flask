from .models import Event, EventResourceAllocation

def has_conflict(event, resource_id):
    allocations = EventResourceAllocation.query.filter_by(
        resource_id=resource_id
    ).all()

    for alloc in allocations:
        other_event = Event.query.get(alloc.event_id)

        if (
            event.start_time < other_event.end_time
            and other_event.start_time < event.end_time
        ):
            return True, other_event

    return False, None
