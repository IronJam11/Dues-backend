# chatsapp/serializers.py
from rest_framework import serializers
from .models import Room
from userapp.models import User

class RoomSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    admins = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    late_joiners = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    
    class Meta:
        model = Room
        fields = ['id', 'room_name', 'participants', 'admins', 'late_joiners', 'time_created', 'slug', 'type']
        read_only_fields = ['slug', 'time_created']

    def create(self, validated_data):
        # Create a Room instance and save it
        participants = validated_data.pop('participants')
        admins = validated_data.pop('admins')
        late_joiners = validated_data.pop('late_joiners')
        
        room = Room.objects.create(**validated_data)
        
        # Add participants, admins, and late joiners
        room.participants.set(participants)
        room.admins.set(admins)
        room.late_joiners.set(late_joiners)
        
        return room

    def update(self, instance, validated_data):
        # Update fields in the Room instance
        participants = validated_data.pop('participants', None)
        admins = validated_data.pop('admins', None)
        late_joiners = validated_data.pop('late_joiners', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if participants is not None:
            instance.participants.set(participants)
        if admins is not None:
            instance.admins.set(admins)
        if late_joiners is not None:
            instance.late_joiners.set(late_joiners)

        instance.save()
        return instance
