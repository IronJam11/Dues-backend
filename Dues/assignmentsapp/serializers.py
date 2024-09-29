from rest_framework import serializers
from .models import Subtask

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'description', 'attachment', 'attachment_name']
    
    def get_attachment_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.attachment.url)
