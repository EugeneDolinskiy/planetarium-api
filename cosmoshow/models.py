from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    themes = models.ManyToManyField(ShowTheme, related_name="astronomy_shows")

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show}({self.planetarium_dome}) start at {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets_taken"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return f"Row: {self.row} - Seat: {self.seat} ({self.show_session.show_time})"

    @staticmethod
    def validate_row(row: int, num_rows: int, error_to_raise):
        if not (1 <= row <= num_rows):
            raise error_to_raise(
                {
                    "row": f"row must be in range [1 , {num_rows}], not {row}"
                }
            )

    @staticmethod
    def validate_seat(seat: int, num_seats: int, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {
                    "seat": f"seat must be in range [1 , {num_seats}], not {seat}"
                }
            )
