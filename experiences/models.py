from django.db import models
from common.models import CommonModel


# Create your models here.
class Experience(CommonModel):
    """Experience Model Definition"""
    country = models.CharField(
        max_length=50,
        default="한국",
    )

    city = models.CharField(
        max_length=80,
        default="서울",
    )

    name = models.CharField(
        max_length=250,
    )
    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    price = models.PositiveIntegerField()
    address = models.CharField(
        max_length=250,
    )
    start = models.TimeField()
    end = models.TimeField()
    description = models.TextField()
    perks = models.ManyToManyField(
        "experiences.Perk",
        related_name="experiences",
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank="",
        on_delete=models.SET_NULL,
        related_name="experiences",
    )

    def __str__(self):
        return self.name


class Perk(CommonModel):
    """What is included on an Experience"""
    name = models.CharField(
        max_length=100,
    )
    detail = models.CharField(
        max_length=250,
        blank=True,
        default="",
        # null=True, #default="" 랑 같음 근데 default는 빈칸을 저장 해주는거고 null 은 null을 저장해줌
    )
    explanation = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name
