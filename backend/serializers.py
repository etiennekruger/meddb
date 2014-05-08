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


def model_to_dict(obj, include_related=False, parent_class=None):
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
                if not type(child_or_list) == parent_class:
                    tmp_dict[key] = child_or_list.to_dict(include_related, parent_class=type(obj))
            else:
                # this is a list of children
                tmp = []
                if child_or_list:
                    for child in child_or_list:
                        if not type(child) == parent_class:
                            tmp.append(child.to_dict(include_related, parent_class=type(obj)))
                tmp_dict[key] = tmp
    return tmp_dict


def medicine_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj, include_related)
    tmp_dict['name'] = obj.name
    tmp_dict['average_price'] = float('%.3g' % tmp_dict['average_price'])
    return tmp_dict


def queryset_to_json(obj_or_list, include_related=False):
    """
    Convert a single model object, or a list of model objects to dicts, before
    serializing the results as a json string.
    """

    if isinstance(obj_or_list, db.Model):
        # this a single object
        out = obj_or_list.to_dict(include_related=True)
    else:
        # this is a list of objects
        out = []
        for obj in obj_or_list:
            out.append(obj.to_dict(include_related=False))
    return json.dumps(out, cls=CustomEncoder, indent=4)