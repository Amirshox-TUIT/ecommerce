from django.urls import path

from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartRetrieveAPIView.as_view()),
    path('cart/item/', views.CartItemCreateAPIView.as_view()),
    path('cart/item/<int:pk>', views.CartItemUpdateAPIView.as_view()),
    path('cart/item/<int:pk>/delete/', views.CartItemDeleteAPIView.as_view()),
    path('checkout/', views.OrderCreateAPIView.as_view()),
]