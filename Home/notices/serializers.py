from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField()

    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['posted_by']


class NoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'semester']