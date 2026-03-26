import os
import random
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


def cosine_similarity(a, b):
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


class Command(BaseCommand):
    help = 'Selecciona una película al azar y muestra su embedding.'

    def handle(self, *args, **options):
        load_dotenv('../openAI.env')
        api_key = os.environ.get('openai_apikey')

        if not api_key:
            self.stderr.write(self.style.ERROR('openai_apikey no encontrada en openAI.env'))
            return

        client = OpenAI(api_key=api_key)

        movies = list(Movie.objects.all())
        if not movies:
            self.stderr.write(self.style.ERROR('No hay películas en la base de datos.'))
            return

        movie = random.choice(movies)
        self.stdout.write(self.style.SUCCESS(f"Película aleatoria seleccionada: {movie.title}"))
        self.stdout.write(f"Descripción: {movie.description}")

        self.stdout.write('Generando embedding con OpenAI...')
        response = client.embeddings.create(
            input=[movie.description],
            model='text-embedding-3-small'
        )
        embedding = np.array(response.data[0].embedding, dtype=np.float32)

        self.stdout.write(self.style.SUCCESS(f'Embedding length: {len(embedding)}'))
        first_values = ', '.join([f"{x:.6f}" for x in embedding[:10]])
        self.stdout.write(f'Primeros 10 valores: [{first_values}]')

        prompt = 'película de un cortometraje de animación francés dirigido por Émile Reynaud en 1892.'
        prompt_response = client.embeddings.create(
            input=[prompt],
            model='text-embedding-3-small'
        )
        prompt_emb = np.array(prompt_response.data[0].embedding, dtype=np.float32)

        similarity = cosine_similarity(prompt_emb, embedding)
        self.stdout.write(self.style.SUCCESS(f"Similitud con '{prompt}': {similarity:.4f}"))