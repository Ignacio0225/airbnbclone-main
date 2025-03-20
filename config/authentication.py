from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


class TrustMeBroAuthentication(BaseAuthentication):
    def authenticate(self, request):
        #헤더 안에 유저 네임이 있는지 확인
        username = request.headers.get('trust-me')
        #없으면 None 반환
        if not username:
            return None
        #있으면 try로 넘어와서 그 다음 스텝 실행을 위한 try
        try:
            #username이 있는경우 user에 넣어줌 후에 이것은 인증된 request.user가 됨
            user = User.objects.get(username=username)
            #여기서 user가 인증된 request.user라는 거임 이제 이것은 view.py 에서 request.*user*로 쓰임.
            return (user,None)
        #없으면 유저가 없다고 스트링 형태로 반환 해줌
        except User.DoesNotExist:
            raise AuthenticationFailed(f'No user{username}')
