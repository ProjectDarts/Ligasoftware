# Generated for Autodarts match statistics

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0004_alter_match_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="player1_avg_total",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 1 Gesamt AVG"),
        ),
        migrations.AddField(
            model_name="match",
            name="player1_avg_first9",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 1 First 9 AVG"),
        ),
        migrations.AddField(
            model_name="match",
            name="player1_avg_to_170",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 1 AVG to 170"),
        ),
        migrations.AddField(
            model_name="match",
            name="player1_checkout_percent",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 1 Checkquote %"),
        ),
        migrations.AddField(
            model_name="match",
            name="player2_avg_total",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 2 Gesamt AVG"),
        ),
        migrations.AddField(
            model_name="match",
            name="player2_avg_first9",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 2 First 9 AVG"),
        ),
        migrations.AddField(
            model_name="match",
            name="player2_avg_to_170",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 2 AVG to 170"),
        ),
        migrations.AddField(
            model_name="match",
            name="player2_checkout_percent",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Spieler 2 Checkquote %"),
        ),
    ]
