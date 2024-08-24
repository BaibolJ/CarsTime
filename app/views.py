from django_filters.rest_framework import DjangoFilterBackend
from .filters import CarFilter
from .models import Car, Category, Rental
from .serializers import CarIndexSerializers, CarCategorySerializers, CarDetailSerializer, RentalSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserProfileSerializer
from .serializers import RegisterSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import Car, Category

User = get_user_model()


class RentalCreateView(generics.CreateAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer


class RentalUpdateView(generics.UpdateAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CarListView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarIndexSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_class = CarFilter

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CarDetailView(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer
    lookup_field = 'id'

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CarCategorySerializers

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreateRentalView(generics.CreateAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rental = serializer.save()
        rental.calculate_total_cost()
        rental.car.status = 1
        rental.car.save()

        return Response({
            "message": "Автомобиль успешно забронирован.",
            "rental": serializer.data
        }, status=status.HTTP_201_CREATED)


class CarIndexView(APIView):
    @swagger_auto_schema(
        operation_description="Получить категории и топ 10 машин",
        responses={200: openapi.Response('OK', CarIndexSerializers(many=True))},
        # manual_parameters=[
        #     openapi.Parameter('some_param', openapi.IN_QUERY, description="Пример параметра", type=openapi.TYPE_STRING)
        # ]
    )
    def get(self, request):
        # Получение всех категорий
        categories = Category.objects.all()
        # Получение топ 10 машин
        cars = Car.objects.all()[:10]

        category_serializers = CarCategorySerializers(categories, many=True)
        car_serializers = CarIndexSerializers(cars, many=True)

        data = {
            "categories": category_serializers.data,
            "cars": car_serializers.data,
        }

        return Response(data)