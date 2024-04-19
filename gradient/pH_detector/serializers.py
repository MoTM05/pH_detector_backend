from rest_framework import serializers
from .models import PHAnalysis

class PHAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PHAnalysis
        fields = '__all__'
        read_only_fields = ['photo']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        photo_url = instance.photo.image.url if instance.photo else None
        representation['photo'] = photo_url
        return representation
