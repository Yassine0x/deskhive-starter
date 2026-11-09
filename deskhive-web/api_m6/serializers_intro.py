"""M6 Lab 1 — complete this plain DRF Serializer (no database writing).

Use the existing Space fields and the M6-EXERCISES.md instructions.
Keep it a regular serializers.Serializer, not ModelSerializer.
"""
from rest_framework import serializers


class SpaceSnapshotSerializer(serializers.Serializer):
    # TODO M6 Lab 1: declare the explicit serializer fields:
    # code (SlugField), name (CharField), kind (ChoiceField),
    # capacity (IntegerField min 1), hourly_rate (DecimalField positive).
    # Refer to the actual Space model and tests for the expected constraints.
    pass
