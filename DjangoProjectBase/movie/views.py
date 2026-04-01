import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
from openai import OpenAI

from .models import Movie


def safe_load_dotenv():
    candidates = [
        str(Path(__file__).resolve().parents[2] / 'openAI.env'),
        str(Path(__file__).resolve().parents[1] / 'openAI.env'),
        'openAI.env',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            load_dotenv(candidate)
            return candidate
    load_dotenv()
    return None


def get_embedding(client, text):
    response = client.embeddings.create(
        input=[text],
        model='text-embedding-3-small'
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a, b):
    if a.size == 0 or b.size == 0:
        return 0.0

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name':'Paola Vallejo'})
    searchTerm = request.GET.get('searchMovie') # GET se usa para solicitar recursos de un servidor
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies})


def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email') 
    return render(request, 'signup.html', {'email':email})


def recommendation(request):
    prompt = request.GET.get('prompt', '').strip()
    recommended = None
    similarity = None
    message = None

    if prompt:
        dotenv_path = safe_load_dotenv()
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            message = 'openai_apikey no encontrada. Revisa openAI.env'
        else:
            client = OpenAI(api_key=api_key)
            try:
                prompt_emb = get_embedding(client, prompt)
            except Exception as exc:
                message = f'No se pudo generar el embedding del prompt: {exc}'
            else:
                best_movie = None
                max_similarity = -1.0
                movies_with_emb = Movie.objects.exclude(emb__isnull=True)
                for movie in movies_with_emb:
                    if not movie.emb:
                        continue
                    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                    sim = cosine_similarity(prompt_emb, movie_emb)
                    if sim > max_similarity:
                        max_similarity = sim
                        best_movie = movie

                if best_movie is not None:
                    recommended = best_movie
                    similarity = max_similarity
                else:
                    message = 'No hay películas con embeddings almacenados. Ejecuta python manage.py movie_embeddings.'

    return render(request, 'recommendation.html', {
        'prompt': prompt,
        'recommended': recommended,
        'similarity': similarity,
        'message': message,
    })


def statistics_view0(request):
    matplotlib.use('Agg')
    # Obtener todas las películas
    all_movies = Movie.objects.all()

    # Crear un diccionario para almacenar la cantidad de películas por año
    movie_counts_by_year = {}

    # Filtrar las películas por año y contar la cantidad de películas por año
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    # Ancho de las barras
    bar_width = 0.5
    # Posiciones de las barras
    bar_positions = range(len(movie_counts_by_year))

    # Crear la gráfica de barras
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')

    # Personalizar la gráfica
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)

    # Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    # Renderizar la plantilla statistics.html con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic})

def statistics_view(request):
    matplotlib.use('Agg')
    # Gráfica de películas por año
    all_movies = Movie.objects.all()
    movie_counts_by_year = {}
    for movie in all_movies:
        print(movie.genre)
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    year_graphic = generate_bar_chart(movie_counts_by_year, 'Year', 'Number of movies')

    # Gráfica de películas por género
    movie_counts_by_genre = {}
    for movie in all_movies:
        # Obtener el primer género
        genres = movie.genre.split(',')[0].strip() if movie.genre else "None"
        if genres in movie_counts_by_genre:
            movie_counts_by_genre[genres] += 1
        else:
            movie_counts_by_genre[genres] = 1

    genre_graphic = generate_bar_chart(movie_counts_by_genre, 'Genre', 'Number of movies')

    return render(request, 'statistics.html', {'year_graphic': year_graphic, 'genre_graphic': genre_graphic})


def generate_bar_chart(data, xlabel, ylabel):
    keys = [str(key) for key in data.keys()]
    plt.bar(keys, data.values())
    plt.title('Movies Distribution')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic