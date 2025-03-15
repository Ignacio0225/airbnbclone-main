from django.contrib import admin
from .models import Review
# Register your models here.


class WordFilter(admin.SimpleListFilter):

    title = "Filter by words"
    parameter_name = "word"
    def lookups(self,request,model_admin):
        return [
            ("good","Good"),
            ("great","Great"),
            ("awesome","Awesome")
        ]
    def queryset(self,request,reviews):
        word = self.value()
        if word:
            return  reviews.filter(payload__contains=word)
        else:
            reviews

class RatingFilter(admin.SimpleListFilter):
    title = "filter by rating level"
    parameter_name = "rate"

    def lookups(self,request,model_admin):
        return[
            ("under_3","Under the 3"),
            ("over_3","Over the 3"),
        ]

    def queryset(self,request,reviews):
        rate = self.value()
        if rate == "under_3":
            return reviews.filter(rating__lte= 3)
        elif rate == "over_3":
            return reviews.filter(rating__gt = 3)
        else:
            return reviews


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "payload",
    )
    list_filter=(
        WordFilter,
        RatingFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly"
    )