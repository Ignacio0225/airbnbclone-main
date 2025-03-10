from django.core.serializers import serialize
from django.template.context_processors import request
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Category
from .serializers import CategorySerializer

# Create your views here.

# class Categories(APIView):
# """적당히 쉽게 하는방법"""
# #카테고리 의 모든 정보를 보여줌 , 한개가 아니기때문에  many = True를 써서 다 보여줌
#     def get(self,request):
#         all_categories = Category.objects.all()
#         serializer = CategorySerializer(all_categories, many=True)
#         return Response(
#             serializer.data,
#         )
#
# #유저가
#     def post(self, request):
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             new_category = serializer.save()
#             return Response(CategorySerializer(new_category).data)
#         else:
#             return Response(serializer.errors)
#
#
# class CategoryDetail(APIView):
# """적당히 쉽게하는방법"""
# #pk 넘버를 받아와서 유효한 url인지 확인후 답변
#     def get_object(self,pk):
#         try:
#             return Category.objects.get(pk=pk)
#         except Category.DoesNotExist:
#             raise NotFound
# #유효한 pk 넘버를 받아서 보여줌
#     def get(self,request,pk):
#         serializer = CategorySerializer(self.get_object(pk), )
#         return Response(serializer.data, )
# #pk 넘버에 있는 정보에 유저가 보낸(request.data)를 유효성을 확인한후 partial로 .save 해주고 변경된 내용을 보여줌
#     def put(self,request,pk):
#         serializer = CategorySerializer(
#             self.get_object(pk),
#             data=request.data,
#             partial=True, )
#         if serializer.is_valid():
#             updated_category = serializer.save()
#             return Response(CategorySerializer(updated_category).data)
#         else:
#             return Response(serializer.errors)
# #pk 정보를 삭제하고 즉시  204 에러를 보여줌
#     def delete(self,request,pk):
#         self.get_object(pk).delete()
#         return Response(status=HTTP_204_NO_CONTENT)



class CategoryViewSet(ModelViewSet):
    """제일 쉽게 하는방법"""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
