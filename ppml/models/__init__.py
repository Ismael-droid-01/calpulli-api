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

class Algorithm(Model):
    algorithm_id    = fields.IntField(primary_key=True)
    name            = fields.CharField(max_length=255, unique=True)
    type            = fields.CharField(max_length=255)
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "algorithms"

class NumericParameter(Model):
    parameter_id    = fields.IntField(primary_key=True)
    algorithm    = fields.ForeignKeyField(
        "models.Algorithm", 
        related_name    =   "numeric_parameters",
        to_field        =   "algorithm_id",
        on_delete       =   fields.CASCADE
    )
    type            = fields.CharField(max_length=255)
    default_value   = fields.FloatField()
    max_value       = fields.FloatField()
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "numeric_parameters"

class StringParameter(Model):
    parameter_id    = fields.IntField(primary_key=True)
    algorithm    = fields.ForeignKeyField(
        "models.Algorithm", 
        related_name    =   "string_parameters",
        to_field        =   "algorithm_id",
        on_delete       =   fields.CASCADE
    )
    default_value   = fields.CharField(max_length=255)
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "string_parameters"