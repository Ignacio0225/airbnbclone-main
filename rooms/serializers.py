from django.template.context_processors import request
from rest_framework.serializers import ModelSerializer
#위에랑 중복 될 수 있음
from rest_framework import serializers
from .models import Amenity, Room
from users.serializer import TinyUserSerializer
from reviews.serializers import ReviewSerializer
from categories.serializers import CategorySerializer
from medias.serializers import PhotoSerializer
from wishlists.models import Wishlist


class AmenitySerializer(ModelSerializer):

    class Meta:
        model = Amenity
        fields = (
            "pk",
            "name",
            "description",
        )

class RoomDetailSerializer(ModelSerializer):

    #user = ReadOnlyField(users.User) 이런식으로 사용하면 pk가 아니라 실제 이름을 가져올 수 있음

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
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True,read_only=True)

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
    # 클래스 안에 is_owner 속성을 만든후 True,False 확인 (views.py RoomDetail 클래스
    # get 메서드에 context={"request":request} 추가)
    # 유저 인증과 같은 개념, owner == user 가 True 일경우 edit 버튼을 추가 할 수 있음
    def get_is_owner(self,room):
        request = self.context['request']
        return room.owner == request.user

    #현재 클래스의 serializer가 사용되는 views.py에서 연결된 object를 room(2번째인자에 넣어줌)
    def get_is_liked(self,room):
        request = self.context['request']
        return Wishlist.objects.filter(user = request.user, rooms__pk=room.pk).exists()


    # #.save(owner=request.user)를 통해  requset 에서 user 데이터를 받아와서  validated_data 에 저장해줌
    # def create(self, validated_data):
    #     return Room.objects.create(**validated_data)


class RoomListSerializer(ModelSerializer):
    review_rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True,read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "review_rating",
            'is_owner',
            'photos',
        )

    def get_review_rating(self,room):
        return room.rating()

    def get_is_owner(self,room):
        request = self.context['request']
        return room.owner == request.user