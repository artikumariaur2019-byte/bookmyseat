from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CastMember(models.Model):
    name = models.CharField(max_length=150)
    biography = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="cast/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)

    # New movie-management fields
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="movies",
    )
    languages = models.ManyToManyField(
        Language,
        blank=True,
        related_name="movies",
    )
    cast_members = models.ManyToManyField(
        CastMember,
        blank=True,
        related_name="movies",
    )
    trailer_url = models.URLField(blank=True)
    age_certification = models.CharField(
        max_length=10,
        blank=True,
    )
    duration_minutes = models.PositiveIntegerField(
        default=0,
    )
    release_date = models.DateField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def average_review_rating(self):
        result = self.reviews.aggregate(avg_rating=Avg("rating"))
        return round(result["avg_rating"], 1) if result["avg_rating"] is not None else 0    



class MoviePoster(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="posters",
    )
    image = models.ImageField(upload_to="movie_posters/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie"],
                condition=models.Q(is_primary=True),
                name="unique_primary_poster_per_movie",
            )
        ]

    def __str__(self):
        return f"{self.movie.name} poster"



class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="theaters",
    )
    time = models.DateTimeField()

    # New theater information
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    screen_name = models.CharField(max_length=100, default="Screen 1")

    def __str__(self):
        return f"{self.name} - {self.movie.name} at {self.time}"


class Seat(models.Model):
    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE,
        related_name="seats",
    )
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["theater", "seat_number"],
                name="unique_seat_per_theater",
            )
        ]

    def __str__(self):
        return f"{self.seat_number} in {self.theater.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Booking by {self.user.username} for "
            f"{self.seat.seat_number} at {self.theater.name}"
        )


class Review(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="movie_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_reported = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "user"],
                name="one_review_per_user_movie",
            )
        ]

    def __str__(self):
        return f"{self.movie.name} review by {self.user.username}"
