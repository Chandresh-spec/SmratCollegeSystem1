from rest_framework import serializers
from .models import Resource
from Academic.serializers import SubjectSerializer
from accounts.models import User


class ResourceSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = ['status', 'is_official', 'view_count']


class ResourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            'title',
            'description',
            'file',
            'reference_url',
            'file_type',
            'subject'
        ]

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
    



from rest_framework import serializers
from .models import Resource
from Academic.serializers import SubjectSerializer
from django.utils.text import format_lazy

class ResourceSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    uploaded_by = serializers.StringRelatedField()
    file_size = serializers.SerializerMethodField()  # New

    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = ['status', 'is_official', 'view_count']

    def get_file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024*1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024*1024):.1f} MB"
        return "N/A"