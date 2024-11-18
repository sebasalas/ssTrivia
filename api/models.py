from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Modelo personalizado de Usuario que extiende AbstractUser.
    Añade un campo de email único.
    """

    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class Question(models.Model):
    """
    Modelo para representar una pregunta en la trivia.
    Incluye texto y dificultad.
    """

    DIFFICULTY_CHOICES = [
        ("easy", "Fácil"),
        ("medium", "Medio"),
        ("hard", "Difícil"),
    ]
    text = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return self.text


class Option(models.Model):
    """
    Modelo para representar una opción de respuesta a una pregunta.
    Indica si la opción es correcta.
    """

    question = models.ForeignKey(
        Question, related_name="options", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correcta' if self.is_correct else 'Incorrecta'})"


class Trivia(models.Model):
    """
    Modelo para representar una trivia que contiene múltiples preguntas.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    questions = models.ManyToManyField(Question)
    users = models.ManyToManyField(User, through="Participation")

    def __str__(self):
        return self.name


class Participation(models.Model):
    """
    Modelo intermedio para representar la participación de un usuario en una trivia.
    Incluye el puntaje y estado de completitud.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.trivia.name}"
