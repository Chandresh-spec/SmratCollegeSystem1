from rest_framework import serializers
from .models import Sem, Subject
from accounts.models import User


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sem
        fields = ['id', 'sem_nmbr']


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SubjectSerializer(serializers.ModelSerializer):
    sem = SemesterSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'sub_code', 'sub_name', 'sem', 'faculty']


class SubjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['sub_code', 'sub_name', 'sem', 'faculty']