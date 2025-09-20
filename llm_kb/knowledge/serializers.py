from rest_framework import serializers
from .models import Document, QAInteraction

class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False)

class AskSerializer(serializers.Serializer):
    question = serializers.CharField()
    top_k = serializers.IntegerField(default=4)

class QAInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAInteraction
        fields = "__all__"
