from rest_framework import serializers
from .models import Notice
from Academic.serializers import SemesterSerializer


class NoticeSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer(read_only=True)
    posted_by = serializers.StringRelatedField()

    class Meta:
        model = Notice
        fields = "__all__"


class NoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['title', 'message', 'notice_type', 'semester']

    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)