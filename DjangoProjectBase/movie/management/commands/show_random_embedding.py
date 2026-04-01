import os
import random
import numpy as np
from pathlib import Path
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


def safe_load_dotenv():
    candidates = [
        'openAI.env',
        '../openAI.env',
        str(Path(__file__).resolve().parents[3] / 'openAI.env'),
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
        model='text-embedding-3-small',
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


class Command(BaseCommand):
    help = 'Compara dos películas y un prompt usando embeddings de OpenAI.'

    def add_arguments(self, parser):
        parser.add_argument('--movie1', type=str, help='Título de la primera película', default=None)
        parser.add_argument('--movie2', type=str, help='Título de la segunda película', default=None)
        parser.add_argument('--prompt', type=str, help='Texto para comparar con las películas',
                            default='película sobre la Segunda Guerra Mundial')

    def handle(self, *args, **options):
        dotenv_path = safe_load_dotenv()
        self.stdout.write(self.style.NOTICE(f'Cargando variables de entorno de: {dotenv_path or "(auto)"}'))

        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write(self.style.ERROR('openai_apikey no encontrada en openAI.env'))
            return

        client = OpenAI(api_key=api_key)

        movies = list(Movie.objects.all())
        if len(movies) < 2:
            self.stderr.write(self.style.ERROR('Se requieren al menos 2 películas en la base de datos.'))
            return

        movie1_title = options['movie1']
        movie2_title = options['movie2']
        prompt_text = options['prompt']

        if movie1_title and movie2_title:
            try:
                movie1 = Movie.objects.get(title=movie1_title)
                movie2 = Movie.objects.get(title=movie2_title)
            except Movie.DoesNotExist as exc:
                self.stderr.write(self.style.ERROR(str(exc)))
                return
        else:
            movie1, movie2 = random.sample(movies, 2)
            self.stdout.write(self.style.WARNING('No se especificaron títulos. Usando dos películas aleatorias.'))

        self.stdout.write(self.style.SUCCESS(f"Película 1: {movie1.title}"))
        self.stdout.write(self.style.SUCCESS(f"Película 2: {movie2.title}"))
        self.stdout.write(f"Prompt: {prompt_text}")

        desc1 = movie1.description or ''
        desc2 = movie2.description or ''

        self.stdout.write('Generando embeddings con OpenAI...')
        emb1 = get_embedding(client, desc1)
        emb2 = get_embedding(client, desc2)

        similarity_movies = cosine_similarity(emb1, emb2)
        self.stdout.write(self.style.SUCCESS(f"🎬 Similitud entre '{movie1.title}' y '{movie2.title}': {similarity_movies:.4f}"))

        prompt_emb = get_embedding(client, prompt_text)
        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(self.style.SUCCESS(f"📝 Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}"))
        self.stdout.write(self.style.SUCCESS(f"📝 Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}"))