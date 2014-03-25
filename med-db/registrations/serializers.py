import json
from datetime import datetime, date
from django.db import models
from django.core import serializers


class CustomEncoder(json.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_obj = obj.strftime("%B %d, %Y, %H:%M")
        elif isinstance(obj, date):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, models.Model):
            try:
                encoded_obj = json.dumps(obj.to_dict(), cls=CustomEncoder, indent=4)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = json.JSONEncoder.default(self, obj)
        return encoded_obj


class BaseSerializer():
    """
    Convert Django models to Python dicts, before encoding them in JSON format.
    """

    def __init__(self):
        return

    def to_dict(self, obj, include_related=False):
        tmp_dict = {
            field_name: getattr(obj, obj._meta.get_field(field_name)) for field_name in obj._meta.get_all_field_names()
        }
        return tmp_dict

    def serialize(self, obj_or_list, include_related=False):
        if isinstance(obj_or_list, models.Model):
            out = self.to_dict(obj_or_list, include_related)
        else:
            out = []
            for obj in obj_or_list:
                out.append(self.to_dict(obj, include_related))
        return json.dumps(out, cls=CustomEncoder, indent=4)


class MedicineSerializer(BaseSerializer):

    def serialize(self, obj, include_related=False):
        out = BaseSerializer.to_dict(self, obj, include_related=include_related)

        return json.dumps(out, cls=CustomEncoder, indent=4)