from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0002_player_is_blocked"),
    ]

    operations = [
        migrations.RenameField(
            model_name="player",
            old_name="first_name",
            new_name="discord_name",
        ),
        migrations.RenameField(
            model_name="player",
            old_name="last_name",
            new_name="autodarts_name",
        ),
    ]