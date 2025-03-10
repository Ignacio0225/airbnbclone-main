from random import choices
from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "kind",
            "created_at"
        )

        # exclude = (
        #     "created_at",
        # )


        # fields,exclude 둘중 하나만 사용가능
        # 전체를 선택하는 방법 -> "__all__"

