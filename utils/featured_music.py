from featuredapp.models import FeaturedMusic


def delete_featured_music(music):
    FeaturedMusic.objects.filter(id=music.id).delete()

