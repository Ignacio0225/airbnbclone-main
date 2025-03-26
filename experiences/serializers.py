from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rooms.serializers import TinyUserSerializer, CategorySerializer
from .models import Perk
from .models import Experience

class PerkSerializer(ModelSerializer):

    class Meta:
        model = Perk
        fields = "__all__"


class ExperiencesSerializer(ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class ExperienceDetailSerializer(ModelSerializer):
    host = TinyUserSerializer(
        read_only=True,
    )
    perks = PerkSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer(
        read_only=True,
    )
    class Meta:
        model=Experience
        fields = (
            'start',
            'end',
            'country',
            'city',
            'name',
            'price',
            'perks',
            'category',
            'host',
        )
