from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import User, Question, Option, Trivia, Participation
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    QuestionSerializer,
    QuestionCreateSerializer,
    OptionReadSerializer,
    OptionCreateSerializer,
    TriviaSerializer,
    TriviaDetailSerializer,
    ParticipationSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)


# Vistas de Usuario
class UserViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar usuarios.
    Permite crear usuarios libremente y gestionar (listar, actualizar, eliminar) solo para administradores.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]


# Vistas de Pregunta
class QuestionViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar preguntas.
    Permite crear, actualizar y eliminar preguntas solo para administradores.
    """

    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return QuestionCreateSerializer
        return QuestionSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


# Vistas de Trivia
class TriviaViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar trivias.
    Permite crear, actualizar y eliminar trivias solo para administradores.
    Incluye acciones personalizadas para participar y enviar respuestas.
    """

    queryset = Trivia.objects.all()
    serializer_class = TriviaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def participate(self, request, pk=None):
        """
        Acción personalizada para que un usuario participe en una trivia.
        """
        trivia = self.get_object()
        participation, created = Participation.objects.get_or_create(
            user=request.user, trivia=trivia
        )
        if participation.completed:
            return Response(
                {"detail": "Ya has completado esta trivia."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TriviaDetailSerializer(trivia)
        # Reemplazar el serializer de preguntas para ocultar 'is_correct'
        questions = trivia.questions.all()
        questions_data = QuestionSerializer(questions, many=True).data
        data = serializer.data
        data["questions"] = questions_data
        return Response(data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def submit_answers(self, request, pk=None):
        """
        Acción personalizada para que un usuario envíe sus respuestas a una trivia.
        Calcula y guarda el puntaje obtenido.
        """
        trivia = self.get_object()
        try:
            participation = Participation.objects.get(user=request.user, trivia=trivia)
        except Participation.DoesNotExist:
            return Response(
                {"detail": "No estás participando en esta trivia."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if participation.completed:
            return Response(
                {"detail": "Ya has completado esta trivia."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = request.data.get("answers")
        if not answers:
            return Response(
                {"detail": "No se proporcionaron respuestas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_score = 0

        for answer in answers:
            question_id = answer.get("question")
            option_id = answer.get("option")

            try:
                question = trivia.questions.get(id=question_id)
                option = Option.objects.get(id=option_id, question=question)
            except (Question.DoesNotExist, Option.DoesNotExist):
                return Response(
                    {
                        "detail": f"Pregunta o opción inválida: pregunta_id={question_id}, opción_id={option_id}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.debug(
                f"Pregunta ID: {question.id}, Texto: {question.text}, Dificultad: {question.difficulty}"
            )
            logger.debug(
                f"Opción ID: {option.id}, Texto: {option.text}, Correcta: {option.is_correct}"
            )

            if option.is_correct:
                difficulty = question.difficulty.strip().lower()
                logger.debug(f"Dificultad normalizada: {difficulty}")
                if difficulty == "easy":
                    total_score += 1
                elif difficulty == "medium":
                    total_score += 2
                elif difficulty == "hard":
                    total_score += 3
                else:
                    logger.warning(f"Dificultad desconocida: {question.difficulty}")

                logger.debug(f"Puntaje acumulado: {total_score}")

        participation.score = total_score
        participation.completed = True
        participation.save()

        return Response({"score": total_score}, status=status.HTTP_200_OK)


# Vista para Ranking
class TriviaRankingView(APIView):
    """
    Vista para obtener el ranking de participantes en una trivia específica.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, trivia_id):
        participations = Participation.objects.filter(trivia_id=trivia_id).order_by(
            "-score"
        )
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
