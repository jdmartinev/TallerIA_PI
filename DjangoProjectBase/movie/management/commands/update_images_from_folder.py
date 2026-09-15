import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign already-generated images from media/movie/images/ to each movie"

    def handle(self, *args, **kwargs):
        images_folder = 'TallerIA_PI/DjangoProjectBase/media/movie/images/'
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        updated_count = 0
        missing_count = 0

        for movie in movies:
            image_filename = f"m_{movie.title}.png"
            image_path_full = os.path.join(images_folder, image_filename)

            if os.path.exists(image_path_full):
                movie.image = os.path.join('movie/images', image_filename)
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Assigned image to: {movie.title}"))
            else:
                missing_count += 1
                self.stderr.write(f"Image not found for: {movie.title} (expected {image_filename})")

        self.stdout.write(self.style.SUCCESS(
            f"Finished. Updated: {updated_count}, Missing: {missing_count}"
        ))