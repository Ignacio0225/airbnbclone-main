import jwt
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from .serializer import PrivateUserSerializer
from .models import User
# Create your views here.


class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        serializer = PrivateUserSerializer(user)
        return Response(serializer.data)

    def put(self,request):
        user = request.user
        serializer = PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class Users(APIView):

    def post(self,request):
        password = request.data.get('password')
        if not password:
            raise ParseError
        serializer = PrivateUserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            #raw password 저장을 방지하기 위해 hash화 하는것 (user.password = password) 이렇게 하면 절대 안됨
            user.set_password(password)
            user.save()
            serializer=PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class PublicUser(APIView):

    def get(self,request,username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound

        #PublicUserSerializer를 만들어서 쓰는것을 추천 Private은 너무 많은 정보가 들어있음
        serializer = PrivateUserSerializer(user)
        return Response(serializer.data)

class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            raise ParseError
        #만약 예전 비밀번호가 맞다면
        if user.check_password(old_password):
            #새로운 비밀번호로 세팅해라
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class LogIn(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request,user)
            return Response({"ok":"Welcome!"})
        else:
            return Response({"error":"wrong password"})

class LogOut(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        logout(request)
        return Response({"ok":"bye!"})

class JWTLogIn(APIView):
    def post(self, request):
        #username과  password를 잘 썼는지 확인 (없으면 에러)
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            raise ParseError
        #authenticate 함수는 request와 함께 username과 password를 인증 하는 과정
        #authenticate()는 로그인한 사용자 정보를 찾아서 반환합니다.
        # 이 객체는 user 객체이며, 이후 user.pk 값을 토큰 페이로드로 사용할 수 있습니다.
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        #user가 있으면 전달할 token에 갖고있는 pk를 암호화 해서 넘겨줌.
        if user:
            #수정할 수는 없지만 유저 정보를 넘겨주기 때문에 민감한 정보를 줄 수 없음
            token = jwt.encode({"pk":user.pk},settings.SECRET_KEY,algorithm='HS256')
            return Response({"token":token})
        else:
            return Response({"error": "wrong password"})
