from rest_framework.serializers import ModelSerializer
#위에랑 중복 될 수 있음
from rest_framework import serializers
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
    owner = TinyUserSerializer(
        read_only= True,
    ) #user 정보를 직접 입력 할수없게 읽기전용으로 변경
    amenities = AmenitySerializer(
        read_only=True,
        many=True,
    )
    category = CategorySerializer(
        read_only=True,
    )
    review_rating = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = "__all__"
        # depth = 1  # 모든 정보를 다 보여줌
    # def create(self, validated_data):
    #     return


    #메서드 이름은 반드시 속성 이름 앞에 get_을 붙여줘야함, 두번째 인자는 현재 선택돼있는 방을 의미함
    def get_review_rating(self,room):
        #Room.models 에서 rating  함수를 가져와서 room.에 넣어줌 (두번째인자안에)
        return room.rating()



    # #.save(owner=request.user)를 통해  requset 에서 user 데이터를 받아와서  validated_data 에 저장해줌
    # def create(self, validated_data):
    #     return Room.objects.create(**validated_data)


class RoomListSerializer(ModelSerializer):
    review_rating = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "review_rating",
        )

    def get_review_rating(self,room):
        return room.rating()