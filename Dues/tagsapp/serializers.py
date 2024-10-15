# serializers.py
from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        # Specify the fields to include in the serializer.
        fields = ['id', 'name', 'description', 'condition', 'color', 'time_added']
        # 'id' is automatically added to represent the primary key
