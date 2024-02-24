from decimal import Decimal as D

from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone
from rest_framework.request import Request

from sapp.models import SM, ImageField, AbstractUser, cls
from .profile_meta import ProfileMeta


class Hood(SM):
    icon = "fas fa-search-location"
    cols_css_class = cls.COL_LG6
    list_field_names = ("id", "name", "city")
    queryset_names = ("profiles",)
    api_methods = ("get_hood_profile_stats_api",)

    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    geo_long = models.FloatField(blank=True, null=True)
    geo_lat = models.FloatField(blank=True, null=True)
    maps_url = models.URLField(
        max_length=512, blank=True, null=True, serialize=cls.CLS_COL_12
    )

    def __str__(self):
        return f"{self.city} - {self.name}"

    @classmethod
    def get_hood_profile_stats_api(cls, request: Request, kwds: dict):
        return cls.get_hood_profile_stats()

    @classmethod
    def get_hood_profile_stats(cls):
        data = {}
        for i in Hood.objects.all():
            data[f"{i.name}"] = i.profiles.count()
        return data

    @cached_property
    def profiles(self):
        return Profile.objects.filter(hood=self)

    def set_location(self):
        self.location = self.location or self.city

    def save(self, *args, **kwargs):
        self.set_location()
        return super().save(*args, **kwargs)


class Profile(SM, ProfileMeta):
    icon = "fas fa-user-alt"
    list_field_names = (
        "id",
        "profile_pic",
        "user",
        "username",
        "hood",
        "gender",
        "sexuality",
        "age",
    )
    filter_field_names = ("hood", "gender", "sexuality", "ih")
    serializer_list_field_names = (
        "id",
        "profile_pic",
        "user",
        "username",
        "hood",
        "gender",
        "sexuality",
        "age",
        "about",
        "location",
        "work",
        "education",
    ) + ProfileMeta.fields
    api_methods = (
        "get_profile_ctx_api",
        "update_last_seen_api",
        "update_ih_api",
        "get_profile_gender_stats_api",
        "get_profile_sexuality_stats_api",
    )
    ctx_fields = (
        "id",
        "full_name",
        "hood",
        "profile_pic",
        "verified",
        "ih",
        "serialized_hood",
    )

    hood = models.ForeignKey(Hood, on_delete=models.SET_NULL, blank=True, null=True)
    user: models.OneToOneField[AbstractUser] = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    username = models.CharField(max_length=256, unique=True)
    full_name = models.CharField(max_length=256)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=SM.iter_as_choices("M", "F", "O"))
    sexuality = models.CharField(
        max_length=10, choices=SM.iter_as_choices("Straight", "Lesbian", "Bi-Sexual")
    )
    profile_pic = ImageField()
    pic_1 = ImageField(blank=True, null=True)
    pic_2 = ImageField(blank=True, null=True)
    pic_3 = ImageField(blank=True, null=True)
    height = models.DecimalField(max_digits=3, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=D("0.00"))
    work = models.CharField(max_length=256, blank=True, null=True)
    education = models.CharField(max_length=256, blank=True, null=True)
    about = models.TextField(max_length=1024, blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    hive_counts = models.PositiveSmallIntegerField(default=0)
    hive_ratings_count = models.PositiveSmallIntegerField(default=0)
    hive_rating = models.FloatField(blank=True, null=True)
    ih = models.BooleanField("I Am Horny", default=True)
    verified = models.BooleanField(default=False)
    dm = models.URLField(max_length=512, blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.username

    @classmethod
    def update_last_seen_api(cls, request: Request, kwds: dict):
        Profile.objects.filter(user_id=request.user.id).update(last_seen=timezone.now())

    @classmethod
    def update_ih_api(cls, request: Request, kwds: dict):
        profiles = Profile.objects.filter(user_id=request.user.id)
        profiles.update(ih=not profiles.first().ih)

    @classmethod
    def get_profile_gender_stats_api(cls, request: Request, kwds: dict):
        return cls.get_profile_gender_stats()

    @classmethod
    def get_profile_gender_stats(cls):
        data = {}
        for i, _ in cls._meta.get_field("gender").choices:
            data[i] = Profile.objects.filter(gender=i).count()
        return data

    @classmethod
    def get_profile_sexuality_stats_api(cls, request: Request, kwds: dict):
        return cls.get_profile_sexuality_stats()

    @classmethod
    def get_profile_sexuality_stats(cls):
        data = {}
        for i, _ in cls._meta.get_field("sexuality").choices:
            data[i] = Profile.objects.filter(sexuality=i).count()
        return data

    @classmethod
    def get_profile_from_request(cls, request: Request):
        return Profile.objects.filter(user=request.user).first()

    @classmethod
    def get_profile_ctx_api(cls, request: Request, kwds: dict):
        profile = cls.get_profile_from_request(request)
        if not profile:
            return None
        serializer_class = profile.get_serializer(request, cls.ctx_fields)
        return serializer_class(instance=profile).data

    @SM.get_serialized_property("id", "name", "city", "country")
    def serialized_hood(self):
        return self.hood

    @property
    def age(self):
        return (timezone.now().date() - self.date_of_birth).days // 365

    def set_location(self):
        if self.hood:
            self.location = self.location or self.hood.location

    def save(self, *args, **kwargs):
        self.set_location()
        return super().save(*args, **kwargs)


class Like(SM):
    icon = "fas fa-hand-holding-heart"
    list_field_names = ("id", "state", "liker", "liked")
    api_methods = ("set_state_api",)

    state = models.CharField(
        max_length=32,
        choices=SM.iter_as_choices(
            "l",
        ),
    )
    liker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="profile_likings"
    )
    liked = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="profile_likes"
    )
    message = models.TextField(max_length=512, blank=True, null=True)

    @classmethod
    def set_state_api(cls, request: Request, kwds: dict):
        Like.objects.filter(
            liked__profile__user=request.user, id=request.data["id"]
        ).update(state=request.data["state"])

    @SM.get_serialized_property(Profile.list_field_names)
    def serialized_liker(self):
        return self.liker

    @SM.get_serialized_property(Profile.list_field_names)
    def serialized_liked(self):
        return self.liked
