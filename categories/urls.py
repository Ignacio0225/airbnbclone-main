from django.urls import path
from . import views

urlpatterns = [
    #적당히 쉬운방법 용도
# path("", views.Categories.as_view()),
# path("<int:pk>",views.CategoryDetail.as_view()),
    #제일쉬운 방법 용도
path("", views.CategoryViewSet.as_view({
    'get':'list',
    'post':'create',
})),
path("<int:pk>",
    views.CategoryViewSet.as_view(
        {
            'get':'retrieve',
            'put':'partial_update',
            'delete':'destroy',
        }
)),

]