from django.db import models


class Pokemon(models.Model):
    title = models.CharField('Название', max_length=200)
    title_en = models.CharField('Название (англ.)', max_length=200, blank=True)
    title_jp = models.CharField('Название (яп.)', max_length=200, blank=True)
    image = models.ImageField(
        'Изображение',
        upload_to='pokemons',
        blank=True,
        null=True
    )
    description = models.TextField('Описание', blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='Из кого эволюционирует',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='next_evolutions'
    )

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        'Pokemon',
        verbose_name='Покемон',
        on_delete=models.CASCADE,
        related_name='entities'
    )
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    appeared_at = models.DateTimeField(
        'Время появления',
        blank=True,
        null=True
    )
    disappeared_at = models.DateTimeField(
        'Время исчезновения',
        blank=True,
        null=True
    )

    level = models.PositiveSmallIntegerField('Уровень', blank=True, null=True)
    health = models.PositiveSmallIntegerField('Здоровье', blank=True, null=True)
    strength = models.PositiveSmallIntegerField('Атака', blank=True, null=True)
    defence = models.PositiveSmallIntegerField('Защита', blank=True, null=True)
    stamina = models.PositiveSmallIntegerField('Выносливость', blank=True, null=True)

    def __str__(self):
        return f"{self.id}: {self.pokemon.title} ({self.lat}, {self.lon})"
