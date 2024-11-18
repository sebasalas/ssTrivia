from django.contrib import admin
from .models import User, Question, Option, Trivia, Participation

# Registro de modelos en el administrador de Django
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Trivia)
admin.site.register(Participation)
