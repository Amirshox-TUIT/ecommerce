from django.urls import path

from apps.products import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListAPIView.as_view()),
    path('<int:pk>/', views.ProductDetailAPIView.as_view()),
    path('<int:pk>/update/', views.ProductPutAPIView.as_view()),
    path('<int:pk>/delete/', views.ProductDeleteAPIView.as_view()),
    path('<int:pk>/partial-update/', views.ProductPatchAPIView.as_view()),
    path('create/', views.ProductCreateAPIView.as_view()),
]