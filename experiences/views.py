from django.conf import settings
from django.core.serializers import serialize
from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from django.template.context_processors import request
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ParseError, NotAuthenticated
from rest_framework.response import Response
from .models import Perk, Experience
from categories.models import Category
from booking.models import Booking
from .serializers import PerkSerializer, ExperiencesSerializer, ExperienceDetailSerializer
from booking.serializers import PublicExperienceBookingSerializer,CreateExperienceBookingSerializer


# Create your views here.


class Experiences(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request):
        all_Experiences = Experience.objects.all()
        serializer = ExperiencesSerializer(all_Experiences,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = ExperienceDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")
            try:
                category = Category.objects.get(pk = category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("The category kind should be 'EXPERIENCE' ")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            try:
                with transaction.atomic():
                    experience = serializer.save(
                        host=request.user,
                        category=category,
                        )
                    perks = request.data.get("perks")
                    for perk_pk in perks:
                        perk = Perk.objects.get(pk=perk_pk)
                        experience.perks.add(perk)
                    serializer = ExperienceDetailSerializer(experience)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Perks not found")
        else:
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)

class ExperienceDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self,pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        experience=self.get_object(pk)
        serializer=ExperiencesSerializer(experience)
        return Response(serializer.data)

    def put(self,request,pk):
        experience=self.get_object(pk)
        if experience.host != request.user:
            raise NotAuthenticated
        serializer = ExperienceDetailSerializer(
            experience,
            data = request.data,
            partial=True,
        )
        if serializer.is_valid():
            category_pk=request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required")

            try:
                category=Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("The category kind should be 'EXPERIENCE' ")
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            try:
                with transaction.atomic():
                    experience = serializer.save(
                        category = category
                    )
                    perks = request.data.get("perks")
                    for perk_pk in perks:
                        perk = Perk.objects.get(pk=perk_pk)
                        experience.perks.add(perk)
                    serializer = ExperienceDetailSerializer(perk)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Perks not found")
        else:
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise NotAuthenticated
        experience.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class ExperienceBooking(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self,pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        experience=self.get_object(pk)
        now = timezone.localtime(timezone.now()).date()
        booking = Booking.objects.filter(
            experiences=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time__gte=now,
            user=request.user,

        )
        serializer = PublicExperienceBookingSerializer(booking,many=True)
        return Response(serializer.data)

    def post(self,request,pk):
        experience=self.get_object(pk)
        serializer=CreateExperienceBookingSerializer(data = request.data)
        if serializer.is_valid():
            booking=serializer.save(
                experiences=experience,
                kind=Booking.BookingKindChoices.EXPERIENCE,
                user=request.user,
            )
            serializer=PublicExperienceBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)

class ExperienceBookingPersonal(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get_booking(self, experience, booking_pk, user):
        try:
            return Booking.objects.get(
                #booking pk를 찾아와서 받음
                pk=booking_pk,
                #experience pk를 받아와서 받음
                experiences=experience,
                #request.user를 받아와서 받음
                user=user,
                #choice 구분해서 받음
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
        except Booking.DoesNotExist:
            raise NotFound

    def get(self, request, pk, booking_pk):
        experience = self.get_object(pk)
        booking = self.get_booking(experience, booking_pk, request.user)
        serializer = PublicExperienceBookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, pk, booking_pk):
        experience = self.get_object(pk)
        booking = self.get_booking(experience, booking_pk, request.user)
        if booking.user != request.user:
            raise NotAuthenticated
        serializer = PublicExperienceBookingSerializer(booking,data=request.data,partial=True)
        if serializer.is_valid():
            booking=serializer.save()
            serializer=PublicExperienceBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)






class Perks(APIView):

    def get(self,request):
        all_perks = Perk.objects.all()
        serializer = PerkSerializer(all_perks,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = PerkSerializer(data = request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(PerkSerializer(perk).data,)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):

    def get_object(self,pk):
        try:
            return Perk.objects.get(pk = pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(perk)
        return Response(serializer.data)

    def put(self,request,pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(
            perk,
            data = request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_perk = serializer.save()
            return Response(PerkSerializer(updated_perk,).data,)
        else:
            return Response(serializer.errors)

    def delete(self,request,pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response (status=HTTP_204_NO_CONTENT)


class PerksInExperience(APIView):
    def get_object(self,pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self,request,pk):
        try:
            page=request.query_params.get('page',1)
            page=int(page)
        except ValueError:
            page=1
        page_size=settings.PAGE_SIZE
        start = (page-1) * page_size
        end = start + page_size

        experience = self.get_object(pk)
        serializer = PerkSerializer(experience.perks.all()[start:end],many=True)
        return Response(serializer.data)

