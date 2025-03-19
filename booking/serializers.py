from tabnanny import check

from django.core.validators import validate_comma_separated_integer_list
from django.utils import timezone
from rest_framework.serializers import ModelSerializer, DateField, ValidationError
from .models import Booking

class CreateRoomBookingSerializer(ModelSerializer):

    # Models.py에서 null=True , blank = True로 돼있기 때문에 여기서 다시 설정해줌
    check_in = DateField()
    check_out = DateField()

    class Meta:
        model = Booking
        fields = (
            'check_in',
            'check_out',
            'guests',
        )

    #value 는 값을 가져옴 (예) check_in 으로 설정한 날짜를 가져옴)
    def validate_check_in(self,value):
        now = timezone.localtime(timezone.now()).date()
        if now > value: # 과거를 선택했다면 True가 됨
            raise ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise ValidationError("Can't book in the past!")
        return value

    #data 전체를 확인
    def validate(self, data):
        # data에서 체크아웃이 체크인보다 빠를경우 에러메세지 전달
        if data["check_out"] <= data["check_in"]:
            raise ValidationError("Check in should be smaller than check out.")

        # db에 있는 데이터와 겹칠지 않을경우를 찾아내는 filter
        # db(check_in) 2025-03-10 lte(<=) = (check_out) 2025-03-16 True, (check_out) 2025-03-30 True, (check_out) 2025-03-05 False
        # db(check_out) 2025-03-20 gte(>=) = (check_in) 2025-03-11 True, (check_in) 2025-03-21 False, (check_in) 2025-03-01 True
        if Booking.objects.filter(
            check_in__lte = data['check_out'],
            check_out__gte = data['check_in']
        ).exists():
            raise ValidationError("Those (or some) of those dates are already taken")
        return data

class PublicBookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = (
            'pk',
            'check_in',
            'check_out',
            'guests'

        )