from rest_framework import serializers
from .models import Idea

class IdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = '__all__'  # You can specify fields like ['id', 'title', 'description', ...] as needed
