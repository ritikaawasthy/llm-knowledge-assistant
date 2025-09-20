from django.db import models

class Document(models.Model):
    id = models.AutoField()
    title = models.CharField(max_length=512)
    filename = models.CharField(max_length=512)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    chunk_id = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class QAInteraction(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    # optional: user/token, latency, prompt used
    meta = models.JSONField(default=dict)