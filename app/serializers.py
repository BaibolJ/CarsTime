from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Car, Category, ImgFile, Rental

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number')


class ImgFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImgFile
        fields = ('file',)


class CarIndexSerializers(serializers.ModelSerializer):
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    gearbox_display = serializers.CharField(source='get_gearbox_display', read_only=True)

    class Meta:
        model = Car
        fields = (
            'id', 'title', 'price_day', 'img_main', 'volume', 'power',
            'fuel_type_display', 'gearbox_display', 'type_car_body', 'status', 'year'
        )


class CarDetailSerializer(serializers.ModelSerializer):
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    gearbox_display = serializers.CharField(source='get_gearbox_display', read_only=True)
    detail_img = ImgFileSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = (
            'id', 'title', 'price_day', 'img_main', 'detail_img', 'volume', 'power',
            'fuel_type_display', 'gearbox_display', 'type_car_body', 'status', 'year'
        )


class CarCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class RentalSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())

    class Meta:
        model = Rental
        fields = ('user', 'car', 'start_date', 'end_date', 'total_cost', 'status')
        read_only_fields = ('total_cost', 'status')

    def validate(self, attrs):
        if 'car' in self.initial_data:
            car_id = self.initial_data['car']
            car = Car.objects.get(id=car_id)
            if car.status == 1:
                raise serializers.ValidationError("Этот автомобиль уже забронирован.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        car = validated_data.get('car')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        if car.status == 1:
            raise serializers.ValidationError("Этот автомобиль уже забронирован.")

        total_days = (end_date - start_date).days

        discount_rate = 0
        if total_days >= 20:
            discount_rate = 0.20
        elif total_days >= 10:
            discount_rate = 0.10
        elif total_days >= 5:
            discount_rate = 0.05

        base_cost = total_days * car.price_day
        discount_amount = base_cost * discount_rate
        total_cost = base_cost - discount_amount

        rental = Rental.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost
        )

        car.status = 1
        car.save(update_fields=['status'])
        rental.status = 1
        rental.save(update_fields=['status'])

        return rental
