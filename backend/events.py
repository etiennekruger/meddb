from backend import app, db, logger
import models


def clean_description(description):

    return description.lower().replace(" ", "_")


def log_event(user, description):
    event_obj = models.Event()
    event_type_obj = models.EventType.query.filter(models.EventType.description==clean_description(description)).first()
    if event_type_obj is None:
        event_type_obj = models.EventType()
        event_type_obj.description = clean_description(description)
    event_obj.event_type = event_type_obj
    event_obj.user = user
    db.session.add(event_obj)
    db.session.commit()
    return