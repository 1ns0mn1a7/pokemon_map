import folium

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime
from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def get_active_entities(qs, current_time):
    return qs.filter(
        Q(appeared_at__lte=current_time) | Q(appeared_at__isnull=True),
        Q(disappeared_at__gte=current_time) | Q(disappeared_at__isnull=True)
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

    entities = get_active_entities(PokemonEntity.objects, current_time)
    for entity in entities:
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

    entities = get_active_entities(pokemon.entities, current_time)
    for entity in entities:
        if pokemon.image:
            add_pokemon(
                folium_map,
                entity.lat,
                entity.lon,
                request.build_absolute_uri(pokemon.image.url)
            )

    next_evolution = None
    evolution = pokemon.next_evolutions.first()
    if evolution:
        next_evolution = {
            'pokemon_id': evolution.id,
            'title_ru': evolution.title,
            'img_url': request.build_absolute_uri(evolution.image.url) if evolution.image else '',
        }

    pokemon_data = {
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else '',
        'description': pokemon.description,
        'previous_evolution': {
            'pokemon_id': pokemon.previous_evolution.id,
            'title_ru': pokemon.previous_evolution.title,
            'img_url': request.build_absolute_uri(pokemon.previous_evolution.image.url) if pokemon.previous_evolution.image else '',
        } if pokemon.previous_evolution else None,
        'next_evolution': next_evolution,
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data
    })
