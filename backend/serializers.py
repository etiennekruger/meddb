import json
from datetime import datetime, date
from backend import db, logger


class CustomEncoder(json.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_obj = obj.strftime("%B %d, %Y, %H:%M")
        elif isinstance(obj, date):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = json.dumps(obj.to_dict(), cls=CustomEncoder, indent=4)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = json.JSONEncoder.default(self, obj)
        return encoded_obj


class BaseSerializer():
    """
    Convert SQLAlchemy models to Python dicts, before encoding them in JSON format.
    """

    def __init__(self):
        return

    def to_dict(self, obj, include_related=False):
        """
        Convert a single model object, or a list of model objects to dicts.
        Handle nested resources recursively.
        """

        # attributes from columns
        columns = obj.__mapper__.column_attrs.keys()
        tmp_dict = {
            key: getattr(obj, key) for key in columns
        }
        # attributes from relationships
        if include_related:
            relationships = obj.__mapper__.relationships.keys()
            for key in relationships:
                child_or_list = getattr(obj, key)
                if isinstance(child_or_list, db.Model):
                    # this is an only child
                    tmp_dict[key] = self.to_dict(child_or_list)
                else:
                    # this is a list of children
                    tmp = []
                    if child_or_list:
                        for child in child_or_list:
                            tmp.append(self.to_dict(child))
                    tmp_dict[key] = tmp
        return tmp_dict

    def to_json(self, obj_or_list, include_related=False):
        """
        Convert a single model object, or a list of model objects to dicts, before
        serializing the results as a json string.
        """

        logger.debug(type(obj_or_list))
        if isinstance(obj_or_list, db.Model):
            # this a single object
            out = self.to_dict(obj_or_list, include_related)
        else:
            # this is a list of objects
            out = []
            for obj in obj_or_list:
                out.append(self.to_dict(obj, include_related))
        return json.dumps(out, cls=CustomEncoder, indent=4)