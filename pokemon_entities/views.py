import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime
from .models import Pokemon, PokemonEntity



MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()

    for entity in PokemonEntity.objects.all():
        if entity.appeared_at and entity.appeared_at > current_time:
            continue
        if entity.disappeared_at and entity.disappeared_at < current_time:
            continue
        if entity.pokemon.image:
            add_pokemon(
                folium_map,
                entity.lat,
                entity.lon,
                request.build_absolute_uri(entity.pokemon.image.url)
            )

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else '',
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()

    for entity in pokemon.pokemonentity_set.all():
        if entity.appeared_at and entity.appeared_at > current_time:
            continue
        if entity.disappeared_at and entity.disappeared_at < current_time:
            continue
        if pokemon.image:
            add_pokemon(
                folium_map,
                entity.lat,
                entity.lon,
                request.build_absolute_uri(pokemon.image.url)
            )

    pokemon_data = {
        'title_ru': pokemon.title,
        'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else '',
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data
    })