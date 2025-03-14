from rest_framework.serializers import ModelSerializer
from .models import Amenity, Room
from users.serializer import TinyUserSerializer
from categories.serializers import CategorySerializer


class AmenitySerializer(ModelSerializer):

    class Meta:
        model = Amenity
        fields = (
            "name",
            "description",
        )

class RoomDetailSerializer(ModelSerializer):
    owner = TinyUserSerializer(read_only= True) #user 정보를 직접 입력 할수없게 읽기전용으로 변경
    amenities = AmenitySerializer(many=True)
    categories = CategorySerializer()

    class Meta:
        model = Room
        fields = "__all__"
        # depth = 1  # 모든 정보를 다 보여줌

class RoomListSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price"
        )
