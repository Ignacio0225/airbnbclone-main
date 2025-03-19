from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rooms.models import Room
from .models import Wishlist
from .serializers import WishlistSerializer
# Create your views here.




class Wishlists(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        all_wishlists = Wishlist.objects.filter(user = request.user)
        serializer = WishlistSerializer(
            all_wishlists,
            many=True,
            context={"request":request},
        )
        return Response(serializer.data)

    def post(self,request):
        serializer = WishlistSerializer(data = request.data)
        if serializer.is_valid():
            wishlist = serializer.save(
                user = request.user,
            )
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class WishlistDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self,pk,user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(wishlist,context={"request":request})
        return Response(serializer.data)

    def delete(self,request,pk):
        wishlist = self.get_object(pk, request.user)
        wishlist.delete()
        return Response(status=HTTP_200_OK)

    def put(self,request,pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(
            wishlist,
            data = request.data,
            partial=True,
        )
        if serializer.is_valid():
            wishlist = serializer.save()
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WishlistToggle(APIView):
    def get_list(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    def get_room(self,pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    #url에 pk와 room_pk 를 받아옴
    def put(self,request,pk,room_pk):
        #pk 와 요청을 보낸 유저 에맞는 정보만 가져옴(두 조건에 모두 충족)
        wishlist = self.get_list(pk,request.user)
        #url로 받아온 room_pk의 정보를 받아옴
        room = self.get_room(room_pk)
        #리스트 형태로 받아오는것을 바라는게 아니라 있는지 없는지만 확인.exists() ,Ture or Flase로 나옴
        if wishlist.rooms.filter(pk=room.pk).exists():
            #가지고 있는 list에서 삭제, delete  와는 다름
            wishlist.rooms.remove(room)
        else:
            wishlist.rooms.add(room)
        return Response(status=HTTP_200_OK)