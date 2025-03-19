from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import NotFound,PermissionDenied
from rest_framework.response import Response
from .models import Photo
# Create your views here.


class PhotoDetail(APIView):

    #유저 인증 (접속되어있는지 확인, GET,POST,PUT,DELETE 전부)
    permission_classes = [IsAuthenticated]

    def get_object(self,pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise NotFound
    def delete(self,request,pk):
        photo = self.get_object(pk)
        # #사진이 있는 방과 접속자가 동일한지 확인하는 작업
        # if photo.room:
        #     #사진과 연결된 방의 주인 != 접속한 유저
        #     if photo.room.owner != request.user:
        #         raise PermissionDenied
        # elif photo.experience:
        #     if photo.experience.host != request.user:
        #         raise PermissionDenied
            #
        if (photo.room and photo.room.owner != request.user) or (
                photo.experience and photo.experience.host != request.user):
            raise PermissionDenied
        photo.delete()
        return Response(status = HTTP_200_OK)