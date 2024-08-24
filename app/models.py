from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .signals import update_car_status


class CustomUser(AbstractUser):
    phone_number = PhoneNumberField(unique=True, blank=False, null=False)

    def __str__(self):
        return self.username


class ImgFile(models.Model):
    file = models.ImageField(upload_to='photo_details/')

    def __str__(self):
        return self.file.name


class BrandCars(models.Model):
    title = models.CharField(max_length=123)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=123)

    def __str__(self):
        return self.title


class Car(models.Model):
    created_at = models.DateTimeField(default=timezone.now, help_text="Дата добавления автомобиля")
    title = models.CharField(max_length=500)
    price_day = models.PositiveIntegerField(help_text="Цена аренды за день в рублях")
    img_main = models.ImageField(upload_to='media/logo')
    detail_img = models.ManyToManyField(ImgFile, related_name='car_images')
    volume = models.DecimalField(max_digits=8, decimal_places=1, help_text="Объем двигателя в литрах")
    power = models.IntegerField(help_text="Мощность двигателя в лошадиных силах")
    fuel_type = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Дизель'),
            (2, 'Бензин'),
            (3, 'Электро')
        ],
        help_text="Тип топлива"
    )
    gearbox = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Механика'),
            (2, "Автомат")
        ],
        help_text="Тип коробки передач"
    )
    type_car_body = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Гибрид'),
            (2, 'Электро'),
            (3, 'ДВС')
        ],
        help_text="Тип кузова"
    )
    brand = models.ForeignKey(BrandCars, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Забронирован'),
            (2, "Свободен")
        ],
        default=2,  # по умолчанию свободен
        help_text="Статус доступности автомобиля"
    )
    year = models.PositiveIntegerField(help_text="Год выпуска автомобиля")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата добавления автомобиля")

    def __str__(self):
        return self.title

    def is_available(self):
        return self.status == 2  # Возвращает True, если автомобиль свободен


class Rental(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rentals', help_text="Пользователь, который арендовал автомобиль")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField(help_text="Дата начала аренды")
    end_date = models.DateField(help_text="Дата окончания аренды")
    total_cost = models.PositiveIntegerField(help_text="Общая стоимость аренды")
    status = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Активно'),
            (2, 'Завершено'),
            (3, 'Отменено')
        ],
        default=1,
        help_text="Статус аренды"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rental of {self.car.title} by {self.user.username} from {self.start_date} to {self.end_date}"

    def calculate_total_cost(self):
        total_days = (self.end_date - self.start_date).days
        self.total_cost = total_days * self.car.price_day
        self.save()
        return self.total_cost

    def is_active(self):
        return self.status == 1

    def cancel(self):
        self.status = 3
        self.car.status = 2  # Освобождаем автомобиль
        self.car.save()
        self.save()

    def complete(self):
        self.status = 2
        self.car.status = 2  # Освобождаем автомобиль
        self.car.save()
        self.save()