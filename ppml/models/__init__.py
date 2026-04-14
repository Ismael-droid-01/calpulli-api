from enum import Enum

from tortoise.models import Model
from tortoise import fields

class UserProfile(Model): 
    id         = fields.IntField(primary_key=True)
    user_id    = fields.CharField(max_length=255, unique=True)
    username   = fields.CharField(max_length=255, unique=True)
    email      = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=255)
    last_name  = fields.CharField(max_length=255)
    is_disabled = fields.BooleanField(default=False)
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

class NumericParameterType(str, Enum):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN" 

class NumericParameter(Model):
    parameter_id    = fields.IntField(primary_key=True)
    algorithm    = fields.ForeignKeyField(
        "models.Algorithm", 
        related_name    =   "numeric_parameters",
        to_field        =   "algorithm_id",
        on_delete       =   fields.CASCADE
    )
    name            = fields.CharField(max_length=255)
    type            = fields.CharEnumField(NumericParameterType, max_length=50)
    default_value   = fields.FloatField()
    max_value       = fields.FloatField()
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "numeric_parameters"

    async def save(self, *args, **kwargs):
        self._validate_by_type()
        await super().save(*args, **kwargs)
    
    def _validate_by_type(self):
        if self.type == NumericParameterType.INTEGER:
            if not self.default_value.is_integer():
                raise ValueError("Default value must be an integer for INTEGER type.")
            if not self.max_value.is_integer():
                raise ValueError("Max value must be an integer for INTEGER type.")
        elif self.type == NumericParameterType.BOOLEAN:
            if self.default_value not in (0.0, 1.0):
                raise ValueError("Default value must be 0.0 or 1.0 for BOOLEAN type.")
            if self.max_value not in (0.0, 1.0):
                raise ValueError("Max value must be 0.0 or 1.0 for BOOLEAN type.")


class StringParameter(Model):
    parameter_id    = fields.IntField(primary_key=True)
    algorithm    = fields.ForeignKeyField(
        "models.Algorithm", 
        related_name    =   "string_parameters",
        to_field        =   "algorithm_id",
        on_delete       =   fields.CASCADE
    )
    name            = fields.CharField(max_length=255)
    default_value   = fields.CharField(max_length=255)
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "string_parameters"

class Task(Model):
    task_id         = fields.IntField(primary_key=True)
    algorithm       = fields.ForeignKeyField(
        "models.Algorithm", 
        related_name    =   "tasks",
        to_field        =   "algorithm_id",
        on_delete       =   fields.RESTRICT
    )
    user            = fields.ForeignKeyField(
        "models.UserProfile", 
        related_name    =   "tasks",
        to_field        =   "user_id",
        on_delete       =   fields.RESTRICT
    )
    response_time    = fields.FloatField() 
    created_at      = fields.DatetimeField(auto_now_add=True)
    updated_at      = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"

class Result(Model):
    result_id   = fields.IntField(primary_key=True)
    task        = fields.ForeignKeyField(
        "models.Task",
        related_name    = "results",
        to_field        = "task_id",
        on_delete       = fields.CASCADE 
    )
    format      = fields.CharField(max_length=100)
    url         = fields.CharField(max_length=500)
    created_at  = fields.DatetimeField(auto_now_add=True)
    updated_at  = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "results"