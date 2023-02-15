from django.db import models

# Create your models here.
class Categories(models.Model):
    name = models.TextField()

    def __str__(self) -> str:
        return self.name


class KeyWords(models.Model):
    name = models.TextField()


class Authors(models.Model):
    name = models.TextField()


class OriginalAuthors(models.Model):
    name = models.TextField()


class Article(models.Model):
    title = models.TextField()
    label = models.TextField(blank=True)
    key_words = models.ManyToManyField(KeyWords, blank=True)
    author = models.ManyToManyField(Authors, blank=True)
    date = models.DateTimeField()
    link = models.TextField()
    categories = models.ManyToManyField(Categories, blank=True)
    original_author = models.ManyToManyField(OriginalAuthors, blank=True)
    text = models.TextField()

    def __str__(self) -> str:
        return self.title

    def getKeyWords(self):
        return ", ".join([item.name for item in self.key_words.all()])

    def getCategories(self):
        return ", ".join([item.name for item in self.categories.all()])

    def getAuthors(self):
        return ", ".join([item.name for item in self.author.all()])

    def getOriginalAuthors(self):
        return ", ".join([item.name for item in self.original_author.all()])
