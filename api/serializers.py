from rest_framework import serializers
from .models import User, Question, Option, Trivia, Participation
from django.contrib.auth import get_user_model

User = get_user_model()


# Serializador para Usuarios (Lectura)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para leer información de usuarios.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email"]


# Serializador para Crear Usuarios (Escritura)
class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear nuevos usuarios.
    Incluye validación para username y email únicos.
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está en uso.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Encriptar la contraseña
        user.save()
        return user


# Serializador de Opción (Lectura) - Oculta 'is_correct'
class OptionReadSerializer(serializers.ModelSerializer):
    """
    Serializador para leer opciones de respuestas, ocultando la información de 'is_correct'.
    """

    class Meta:
        model = Option
        fields = ["id", "text"]


# Serializador de Opción (Escritura) - Incluye 'is_correct'
class OptionCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear opciones de respuestas, incluyendo la información de 'is_correct'.
    """

    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]


# Serializador de Pregunta (Lectura)
class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializador para leer preguntas junto con sus opciones.
    """

    options = OptionReadSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "options"]


# Serializador de Pregunta (Escritura)
class QuestionCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear preguntas junto con sus opciones.
    """

    options = OptionCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "difficulty", "options"]

    def create(self, validated_data):
        options_data = validated_data.pop("options")
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question


# Serializador de Trivia (Lectura y Escritura)
class TriviaSerializer(serializers.ModelSerializer):
    """
    Serializador para leer y crear trivias.
    Incluye la relación con usuarios y preguntas.
    """

    users = UserSerializer(many=True, read_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    questions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Question.objects.all()
    )

    class Meta:
        model = Trivia
        fields = ["id", "name", "description", "questions", "users", "user_ids"]

    def create(self, validated_data):
        users = validated_data.pop("user_ids", [])
        questions = validated_data.pop("questions", [])
        trivia = Trivia.objects.create(**validated_data)
        trivia.questions.set(questions)

        # Crear participaciones para cada usuario
        for user in users:
            Participation.objects.create(user=user, trivia=trivia)

        return trivia


# Serializador Detallado de Trivia (Lectura)
class TriviaDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detallado para trivias, incluyendo todas las preguntas y sus opciones.
    """

    questions = QuestionSerializer(many=True)

    class Meta:
        model = Trivia
        fields = ["id", "name", "description", "questions"]


# Serializador de Participación
class ParticipationSerializer(serializers.ModelSerializer):
    """
    Serializador para leer la participación de un usuario en una trivia.
    Incluye el puntaje total posible y el porcentaje alcanzado.
    """

    user = UserSerializer(read_only=True)  # Incluir información del usuario
    total_possible_score = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = [
            "id",
            "user",
            "trivia",
            "score",
            "total_possible_score",
            "percentage",
            "completed",
        ]

    def get_total_possible_score(self, obj):
        return sum(
            [
                1 if q.difficulty == "easy" else 2 if q.difficulty == "medium" else 3
                for q in obj.trivia.questions.all()
            ]
        )

    def get_percentage(self, obj):
        total = self.get_total_possible_score(obj)
        if total == 0:
            return 0
        return round((obj.score / total) * 100, 2)
