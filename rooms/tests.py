from django.test import TestCase
from rest_framework.test import APITestCase
from . import models
from users.models import User
# Create your tests here.

class TestAmenities(APITestCase):
    NAME = "Amenity Test"
    DESC = "Amenity des"
    URL = "/api/v1/rooms/amenities/"

    #다른 모든 테스트들이 시작되기전에 먼저 시작됨
    #기본 테스트용 데이터를 하나 만들어줌
    def setUp(self) -> None:
        models.Amenity.objects.create(
            name = self.NAME,
            description = self.DESC,
        )

    def test_all_amenities(self):
        response = self.client.get(self.URL)

        # 받아온 테스트 한결과를 data에 json 형태로 넣어줌, 하지만 빈 데이터를 반환함
        # (테스트는 테스트 데이터 베이스를 사용한후 데이터를 다시 삭제함, 진짜 데이터 베이스를 건들지 않음)
        data = response.json()

        # response(가져온url) 로 status를 테스트함.
        self.assertEqual(response.status_code,200,"status code isn`t 200")

        # data가 list인지 확인
        self.assertIsInstance(data,list)

        #데이터의 길이가 1인지 확인(1개인지)
        self.assertEqual(
            len(data),
            1
        )

        # 첫번째 데이터의 name이 NAME랑 같은지 확인
        self.assertEqual(
            data[0]["name"],
            self.NAME
        )
        #첫번째 데이터의 description이 DESC랑 같은지 확인
        self.assertEqual(
            data[0]["description"],
            self.DESC
        )

    def test_create_amenities(self):
        new_amenity_name="New amenity"
        new_amenity_desc="New amenity desc"
        response = self.client.post(
            self.URL,data = {"name":new_amenity_name,"description":new_amenity_desc},
        )
        data = response.json()
        self.assertEqual(
            response.status_code,
            200,
            "Not 200 status code",
        )
        self.assertEqual(
            data['name'],
            new_amenity_name,
        )
        self.assertEqual(
            data['description'],
            new_amenity_desc,
        )

        response=self.client.post(self.URL)

        data = response.json()

        self.assertEqual(response.status_code,400)
        #에러메세지의 data 안에 name이라는 객체가 있는지 확인
        self.assertIn("name",data)

class TestAmenity(APITestCase):
    NAME = "amenity NAME"
    DESC = "amenity DESC"

    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    #get_object를 따로 분리해서 테스트
    def test_amenity_not_found(self):
        # 에러가 잘 나고있는지 확인
        response = self.client.get("/api/v1/rooms/amenities/2")
        self.assertEqual(response.status_code, 404)

    #get을 테스트
    def test_get_amenity(self):

        #잘 작동됐을때 에러가 있는지 확인
        response = self.client.get("/api/v1/rooms/amenities/1")
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            data['name'],
            self.NAME,
        )
        self.assertEqual(
            data['description'],
            self.DESC,
        )

    def test_put_amenity(self):
        new_amenity_name = "New Amenity NAME"
        new_amenity_desc = "New Amenity DESC"
        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={"name":new_amenity_name,"description":new_amenity_desc},
        )
        data = response.json()
        self.assertEqual(
            response.status_code,200,"Not 200 status code"
        )
        self.assertIn("name",data)
        self.assertIn("description", data)
        self.assertEqual(data['name'],new_amenity_name)
        self.assertEqual(data['description'],new_amenity_desc)


    def test_delete_amenity(self):
        response =  self.client.delete("/api/v1/rooms/amenities/1")
        self.assertEqual(response.status_code,204)

class TestRooms(APITestCase):

    def setUp(self):

        user = User.objects.create(
            username="test"
        )
        user.set_password("123")
        user.save()

        self.user = user

        # 동일한 방법
        # user = User.objects.create_user(username="test",password="123")
        # self.user



    def test_create_room(self):

        response=self.client.post("/api/v1/rooms/")
        self.assertEqual(response.status_code,403,"Not 403")

        self.client.force_login(
            self.user
        )
        response = self.client.post("/api/v1/rooms/")
        print(response)