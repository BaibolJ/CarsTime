from django.urls import path
from .views import CarListView, CategoryListView, CarDetailView, CreateRentalView, RentalCreateView, RentalUpdateView, CarIndexView
from .views import RegisterView, UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('index/', CarIndexView.as_view()),
    path('cars/', CarListView.as_view(), name='car-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('cars/<int:id>/', CarDetailView.as_view(), name='car-detail'),
    path('rentals/', CreateRentalView.as_view(), name='create-rental'),
    path('rentals/create/', RentalCreateView.as_view(), name='rental-create'),
    path('rentals/<int:pk>/update/', RentalUpdateView.as_view(), name='rental-update'),
]