from django.conf import settings
#사용할 수 있는 status code들이 있음
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.response import Response
#exceptions 는 에러들을 모아둠
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from .models import Amenity, Room
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer

# Create your views here.

class Amenities(APIView):
    def get(self,request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = AmenitySerializer(data = request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data,)
        else:
            return Response(serializer.errors)

class AmenityDetail(APIView):
    #get_objects -> 유효한 pk를 받아오지 못한다면 404 에러를표시해줌
    def get_object(self,pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound
    #urls 에서 pk 를 가져와서 get_object 에서 그 pk가 유효한지 확인후 data를 가져옴
    def get(self,request,pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self,request,pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_serializer = serializer.save()
            return Response(AmenitySerializer(updated_serializer).data,)
        else:
            return Response(serializer.errors)

    def delete(self,request,pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class Rooms(APIView):

    def get(self,request):
        all_room = Room.objects.all()
        serializer = RoomListSerializer(
            all_room,
            many=True,
            context={'request':request},
        )
        return Response(serializer.data)

    def post(self,request):
        # request를 보낸 유저가 로그인중인지 확인 로그인 하지 않았다면 오류 메세지를 전달함 (장고는 request에서 자동으로 유저 정보를 가져와줌)
        if request.user.is_authenticated:
            # 모든 정보를 가져오기 위해 많은 정보를 갖고있는 클래스로 사용
            serializer = RoomDetailSerializer(data = request.data)
            if serializer.is_valid():
                #post 요청한 requst에서 categroy를 가져오기 위해 설정 category는 사용자가 숫자로 post 하기 때문에 결국 숫자를 가져온다는말
                category_pk = request.data.get("category")
                # category: 를 안썼다면 Parserror를 보여줌.
                if not category_pk:
                    raise ParseError("Category is required")
                # Category가 갖고있지 않는 pk를 준다면 에러를 보여줌
                try:
                    category = Category.objects.get(pk=category_pk)
                    # pk 로 가져온 category 에서 kind 가 EXPERIENCES면 에러를 보여줌
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The category kind should be 'ROOMS' ")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
                #with 를 쓰더라도 오류 메세지는 줘야하기때문에 작성
                try:
                    # with transaction.atomic():을 추가 해주면 바로db에 저장 하는게 아니라 모든게 문제 없을때 저장이 되고 실패가 하나라도 있을시
                    # 저장되지않고 실패하기전 원래 상태로 되돌림
                    # try , except가 있다면 transaction 이 에러를 파악하지 못하기 때문에 내부에는 사용하지 않음
                    with transaction.atomic():
                        # 실행 되면 안보이지만 serializer 의 create(self,validated_data)에 자동으로 추가됨
                        room = serializer.save(
                            owner=request.user,
                            category=category
                        )
                        amenities = request.data.get("amenities")
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            #.add를 하므로써 자동으로 저장됨 .save가 필요 없음
                            room.amenities.add(amenity)
                        serializer = RoomDetailSerializer(room,context={'request':request})
                        return Response(serializer.data)

                except Exception:
                    raise ParseError("Amenity not found")
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated


class RoomDetail(APIView):

    def get_object(self,pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound


    def get(self,request,pk):
        room = self.get_object(pk)
        # context 를 추가 할 수 있음 serializer에도 get_으로 추가
        # 로그인 한사람이 이 방의 주인인지 아닌지 확인 유저 인증과 같은 개념, owner가 True 일경우 edit 버튼을 추가 할 수 있음
        serializer = RoomDetailSerializer(
            room,
            context={"request":request})
        return Response(serializer.data)

    def put(self,request,pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated

        if room.owner != request.user:
            raise PermissionDenied

        serializer = RoomDetailSerializer(
            room,
            data = request.data,
            partial=True,
        )

        if serializer.is_valid():
            category_pk = request.data.get("category")

            if not category_pk:
                raise ParseError("Category is required")

            try:
                category = Category.objects.get(pk = category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The Category kind should be 'ROOMS'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            try:
                with transaction.atomic():
                    room = serializer.save(
                        category = category
                    )
                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk = amenity_pk)
                        room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(room)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")

        else:
            return Response(serializer.errors)


    def delete(self,request,pk):
        room = self.get_object(pk)
        #request를 보낸 유저가 로그인중인지 확인 로그인 하지 않았다면 오류 메세지를 전달함 (장고는 request에서 자동으로 유저 정보를 가져와줌)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        #이미 존재하는 room.owner의 정보와 요청을 보낸 user의 정보가 일치 하지 않을경우 오류메세지 전송 (owner는 user 데이터를 갖고있음)
        if room.owner != request.user:
            raise PermissionDenied

        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class RoomReviews(APIView):

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        #page를 정수가 아닌것으로 입력 했을 경우 page 1로 보내주는 try를 만듦
        try:
            page = request.query_params.get('page', 1)
            #page 번호를 문자열로 받아오기때문에 수동으로 정수형으로 바꿔줌
            page = int(page)
        except ValueError:
            page = 1
        page_size = 3
        start = (page -1) * page_size
        end = start + page_size
        #page를 찾지 못하면 자동으로 기본으로 page 1 로 이동
        room =self.get_object(pk)
        #보여줄 serializer (ReviewSerializer)로 가져옴
        serializer = ReviewSerializer(
            #0부터 3전까지만 로딩 하게 해줌
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

class RoomAmenities(APIView):

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        try:
            page = request.query_params.get('page',1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = AmenitySerializer(
            room.amenities.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

class RoomPhotos(APIView):
    def get_object(self,pk):
        try:
            return Room.objects.get(pk = pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self,request,pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(
                room=room
            )
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)