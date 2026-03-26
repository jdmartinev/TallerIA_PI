import os
import numpy as np
from pathlib import Path
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


def safe_load_dotenv():
    """Loads openAI.env from current project root or parent if needed."""
    # Ruta relativa en proyectos Django (manage.py en DjangoProjectBase)
    candidates = [
        'openAI.env',
        '../openAI.env',
        str(Path(__file__).resolve().parents[3] / 'openAI.env'),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            load_dotenv(candidate)
            return candidate
    load_dotenv()  # intenta con valor por defecto
    return None


def get_embedding(client, text):
    response = client.embeddings.create(
        input=[text],
        model='text-embedding-3-small',
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a, b):
    if a.size == 0 or b.size == 0:
        raise ValueError('Embeddings no pueden estar vacíos')

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


class Command(BaseCommand):
    help = 'Comparar similitud de películas utilizando embeddings de OpenAI (coseno)'

    def add_arguments(self, parser):
        parser.add_argument('--movie1', type=str, default='Carmencita')
        parser.add_argument('--movie2', type=str, default='Blacksmith Scene')
        parser.add_argument('--prompt', type=str, default='película sobre un herrero en el taller')

    def handle(self, *args, **options):
        dotenv_path = safe_load_dotenv()
        self.stdout.write(self.style.NOTICE(f'Cargando variables de entorno de: {dotenv_path or "(auto)"}'))

        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write(self.style.ERROR('openai_apikey no encontrada. Revisa openAI.env'))
            return

        client = OpenAI(api_key=api_key)

        movie1_title = options['movie1']
        movie2_title = options['movie2']
        prompt_text = options['prompt']

        try:
            movie1 = Movie.objects.get(title=movie1_title)
        except Movie.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No existe película con título '{movie1_title}'"))
            return

        try:
            movie2 = Movie.objects.get(title=movie2_title)
        except Movie.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No existe película con título '{movie2_title}'"))
            return

        self.stdout.write(self.style.NOTICE(f"Obteniendo embedding de '{movie1.title}' y '{movie2.title}'"))

        emb1 = get_embedding(client, movie1.description or '')
        emb2 = get_embedding(client, movie2.description or '')

        similarity_movies = cosine_similarity(emb1, emb2)
        self.stdout.write(f"\U0001F3AC Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity_movies:.4f}")

        self.stdout.write(self.style.NOTICE(f"Obteniendo embedding del prompt: '{prompt_text}'"))
        prompt_emb = get_embedding(client, prompt_text)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")