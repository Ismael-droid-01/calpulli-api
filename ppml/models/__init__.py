from tortoise.models import Model
from tortoise import fields

class UserProfile(Model): 
    id         = fields.IntField(primary_key=True)
    user_id    = fields.CharField(max_length=255, unique=True)
    username   = fields.CharField(max_length=255, unique=True)
    email      = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=255)
    last_name  = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_profiles"
