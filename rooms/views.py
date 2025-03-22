#장고 유틸리티로 시간 관련 된것은 이거쓰는게 좋음
from tabnanny import check

from django.utils import timezone
from django.conf import settings
#사용할 수 있는 status code들이 있음
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
#exceptions 는 에러들을 모아둠
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from .models import Amenity, Room
from categories.models import Category
from booking.models import Booking
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from booking.serializers import PublicBookingSerializer,CreateRoomBookingSerializer


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
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)

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
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class Rooms(APIView):

    #GET은 읽기전용으로 인증 없이 확인가능 POST,PUT,DELETE는 인증 해줌(전역변수)
    #permission_classes = [IsAuthenticatedOrReadOnly]

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
                return Response(serializer.errors,HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)


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

    permission_classes = [IsAuthenticatedOrReadOnly]

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

    def post(self,request,pk):
        serializer = ReviewSerializer(data = request.data)
        if serializer.is_valid():
            reviews =serializer.save(
                #유저를 바꿀수 없게 접속된 유저로 설정
                user = request.user,
                #어느 방에 작성할건지를 설정하게 해줌 (보이지는 않지만 db에는 연결돼서 저장됨)
                room = self.get_object(pk)
            )
            serializer = ReviewSerializer(reviews)
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
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)

class RoomBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self,pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self,request,pk):

        # user(요청자)가 존재하지 않는 room에 대한 예약을 요청하면 room이 존재하지 않는다고 안내 할 수 있음 (DoesNotExist)
        room = self.get_object(pk)
        #현재 현지 시간 확인 방법 .date()는 시간을 제외한 날짜만
        now = timezone.localtime(timezone.now()).date()
        booking = Booking.objects.filter(
            room = room,
            kind = Booking.BookingKindChoices.ROOM,
            #check_in 날짜보다 gte(큰) 것만 필터
            check_in__gte=now,
        )
        serializer = PublicBookingSerializer(booking,many=True)
        return Response(serializer.data)

        # ------------------다른방법-----------------
        # 반드시 user(요청자)가 존재 하는 room의 room__pk를 입력 한다고 하면 아래처럼 작성
        # user가 방이 없는 상황이라도 예약이 안됐다고 생각할 수있음
        # ORM 필터 해서 바로 room__pk를 방을 찾을 수 있음
        # booking = Booking.objects.filter(room__pk = pk)

    def post(self,request,pk):
        room = self.get_object(pk)
        serializer = CreateRoomBookingSerializer(data = request.data)
        if serializer.is_valid():
            #현재 날짜 이후로 부킹 할수있게 하는방법 (만약 과거 날짜로 시간을 지정한다면 에러)
            # 방법1 check_in = request.data.get('check_in') # 이후 if-else로 날짜 비교하여 입력 가능
            # 방법2 booking.serializers.py에 is_valid 를 검사 할수 있는 로직을 써서 여기서는 pass로 진행
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM,
            )
            #저장할때는 일반으로 보여주는 시리얼라이져 사용
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)
