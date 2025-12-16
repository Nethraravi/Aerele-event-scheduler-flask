from flask import render_template, request, redirect, url_for
from .models import Resource
from . import db

def register_routes(app):

    @app.route("/resources", methods=["GET", "POST"])
    def resources():
        if request.method == "POST":
            name = request.form["name"]
            type_ = request.form["type"]

            resource = Resource(name=name, type=type_)
            db.session.add(resource)
            db.session.commit()

            return redirect(url_for("resources"))

        all_resources = Resource.query.all()
        return render_template("resources.html", resources=all_resources)
    
    @app.route("/resources/edit/<int:resource_id>", methods=["GET", "POST"])
    def edit_resource(resource_id):
        resource = Resource.query.get_or_404(resource_id)

        if request.method == "POST":
            resource.name = request.form["name"]
            resource.type = request.form["type"]

            db.session.commit()
            return redirect(url_for("resources"))

        return render_template("edit_resource.html", resource=resource)

    
    from datetime import datetime
    from .models import Event

    @app.route("/events", methods=["GET", "POST"])
    def events():
        if request.method == "POST":
            title = request.form["title"]
            start_time = datetime.fromisoformat(request.form["start_time"])
            end_time = datetime.fromisoformat(request.form["end_time"])
            description = request.form["description"]

            if start_time >= end_time:
                return "Error: Start time must be before end time"

            event = Event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description
            )
            db.session.add(event)
            db.session.commit()

            return redirect(url_for("events"))

        all_events = Event.query.order_by(Event.start_time).all()
        return render_template("events.html", events=all_events)
    
    @app.route("/events/edit/<int:event_id>", methods=["GET", "POST"])
    def edit_event(event_id):
        event = Event.query.get_or_404(event_id)

        if request.method == "POST":
            event.title = request.form["title"]
            event.description = request.form["description"]
            event.start_time = datetime.fromisoformat(request.form["start_time"])
            event.end_time = datetime.fromisoformat(request.form["end_time"])

            if event.start_time >= event.end_time:
                return "Error: Start time must be before end time"

            db.session.commit()
            return redirect(url_for("events"))

        return render_template("edit_event.html", event=event)

    
    from .models import Event, Resource, EventResourceAllocation

    @app.route("/allocate", methods=["GET", "POST"])
    def allocate():
        events = Event.query.all()
        resources = Resource.query.all()

        from .utils import has_conflict

        if request.method == "POST":
            event_id = int(request.form["event_id"])
            resource_ids = request.form.getlist("resource_ids")

            event = Event.query.get(event_id)

            for r_id in resource_ids:
                conflict, other_event = has_conflict(event, int(r_id))
                if conflict:
                    return render_template(
                        "conflict.html",
                        resource=Resource.query.get(r_id),
                        event=event,
                        other_event=other_event
                    )

            for r_id in resource_ids:
                allocation = EventResourceAllocation(
                    event_id=event_id,
                    resource_id=int(r_id)
                )
                db.session.add(allocation)

            db.session.commit()
            return redirect(url_for("allocate"))


        allocations = db.session.query(
            Event.title,
            Resource.name
        ).join(EventResourceAllocation, Event.id == EventResourceAllocation.event_id)\
         .join(Resource, Resource.id == EventResourceAllocation.resource_id)\
         .all()

        return render_template(
            "allocate.html",
            events=events,
            resources=resources,
            allocations=allocations
        )
    
    from datetime import datetime

    @app.route("/report", methods=["GET", "POST"])
    def report():
        resources = Resource.query.all()
        report_data = []

        start_date = end_date = None

        if request.method == "POST":
            start_date = datetime.fromisoformat(request.form["start_date"])
            end_date = datetime.fromisoformat(request.form["end_date"])

            for resource in resources:
                allocations = EventResourceAllocation.query.filter_by(
                    resource_id=resource.id
                ).all()

                total_hours = 0
                upcoming = []

                for alloc in allocations:
                    event = Event.query.get(alloc.event_id)

                    # Calculate overlap
                    overlap_start = max(event.start_time, start_date)
                    overlap_end = min(event.end_time, end_date)

                    if overlap_start < overlap_end:
                        duration = (overlap_end - overlap_start).total_seconds() / 3600
                        total_hours += duration

                    if event.start_time > datetime.now():
                        upcoming.append(event)

                report_data.append({
                    "resource": resource,
                    "hours": round(total_hours, 2),
                    "upcoming": upcoming
                })

        return render_template(
            "report.html",
            report_data=report_data,
            start_date=start_date,
            end_date=end_date
        )



