from backend import logger, app, db
import cache


def clean_description(description):

    clean_description = description.replace(" ", "_").lower()
    return clean_description


def log_event(description, user):
    cache.store(clean_description(description), user.email)
    return


def read_event_log(description):
    return str(cache.retrieve(clean_description(description)))