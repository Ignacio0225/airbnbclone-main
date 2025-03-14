from django.shortcuts import render
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Amenity, Room
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer

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
        serializer = RoomListSerializer(all_room, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = RoomDetailSerializer(data = request.data) # 모든 정보를 가져오게 위해 많은 정보를 갖고있는 클래스로 사용
        if serializer.is_valid():
            room = serializer.save()
            serializer = room.data
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class RoomDetail(APIView):

    def get_object(self,pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound


    def get(self,request,pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data)
