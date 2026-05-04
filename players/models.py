from django.db import models


class Player(models.Model):
    discord_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Discord Name"
    )
    autodarts_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Autodarts Name"
    )
    display_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Spieler aktiv")
    is_blocked = models.BooleanField(default=False, verbose_name="Spieler gesperrt")

    class Meta:
        ordering = ["display_name"]
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"

    def __str__(self):
        return self.display_name or f"{self.discord_name} / {self.autodarts_name}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.discord_name} / {self.autodarts_name}"
        super().save(*args, **kwargs)