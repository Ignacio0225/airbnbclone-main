from django.urls import path
from .views import Me, Users,PublicUser,ChangePassword,LogIn,LogOut


urlpatterns = [
    path("",Users.as_view()),
    path("me",Me.as_view()),
    path("change-password",ChangePassword.as_view()),
    path("log-in",LogIn.as_view()),
    path("log-out",LogOut.as_view()),
    #str을 받기때문에 다른 url을 받아도 username 으로 인식하기때문에 맨 밑으로 내려야함 (장고는 순서대로 처리함)
    #또는 @같은것을 추가해서 겹치지 않게 함.
    path("@<str:username>", PublicUser.as_view()),
]