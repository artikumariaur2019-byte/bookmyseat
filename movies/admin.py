from django.contrib import admin
from .models import (
    Movie,
    Genre,
    Language,
    CastMember,
    MoviePoster,
    Theater,
    Seat,
    Booking,
    Review,
)


class MoviePosterInline(admin.TabularInline):
    model = MoviePoster
    extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "rating",
        "duration_minutes",
        "age_certification",
        "release_date",
    )
    search_fields = ("name", "cast", "description")
    list_filter = ("genres", "languages", "age_certification")
    filter_horizontal = ("genres", "languages", "cast_members")
    inlines = [MoviePosterInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "movie",
        "city",
        "screen_name",
        "time",
    )
    list_filter = ("city", "movie")
    search_fields = ("name", "city", "movie__name")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("theater", "seat_number", "is_booked")
    list_filter = ("is_booked", "theater")
    search_fields = ("seat_number", "theater__name")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "seat",
        "movie",
        "theater",
        "booked_at",
    )
    list_filter = ("movie", "theater", "booked_at")
    search_fields = ("user__username", "movie__name")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "movie",
        "user",
        "rating",
        "is_reported",
        "created_at",
    )
    list_filter = ("rating", "is_reported", "created_at")
    search_fields = ("movie__name", "user__username", "comment")