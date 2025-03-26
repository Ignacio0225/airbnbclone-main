from django.urls import path
from .views import Perks, PerkDetail, Experiences, ExperienceDetail,ExperienceBooking,PerksInExperience,ExperienceBookingPersonal



urlpatterns = [
    path("",Experiences.as_view()),
    path("<int:pk>",ExperienceDetail.as_view()),
    path("<int:pk>/perks",PerksInExperience.as_view()),
    path("<int:pk>/booking",ExperienceBooking.as_view()),
    path("<int:pk>/booking/<int:booking_pk>",ExperienceBookingPersonal.as_view()),
    path("perks/",Perks.as_view()),
    path("perks/<int:pk>",PerkDetail.as_view())
]