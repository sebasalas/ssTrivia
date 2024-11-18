from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, QuestionViewSet, TriviaViewSet, TriviaRankingView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"trivias", TriviaViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # Endpoint para obtener tokens
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # Endpoint para refrescar tokens
    path(
        "trivias/<int:trivia_id>/ranking/",
        TriviaRankingView.as_view(),
        name="trivia-ranking",
    ),
]
