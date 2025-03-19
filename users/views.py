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