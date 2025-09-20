from django.urls import path
from .views import UploadView, AskQuestionView

urlpatterns = [
    path("upload/", UploadView.as_view(), name="upload"),
    path("ask-question/", AskQuestionView.as_view(), name="ask-question"),
]
