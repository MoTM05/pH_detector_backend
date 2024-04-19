from rest_framework.response import Response
from rest_framework import status
from .serializers import PHAnalysisSerializer
from .utils import calculate_ph
from .models import Photo, PHAnalysis
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def analyze_photo(request):
    if request.method == 'POST':
        # Проверяем, что в запросе есть изображение
        if 'image' not in request.data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем изображение из запроса
        image = request.data['image']

        # Проверяем, что gradient_type имеет корректное значение
        gradient_type = int(request.data.get('gradient_type', 1))
        print("Gradient Type:", gradient_type)
        if gradient_type not in [0, 1]:
            return Response({'error': 'Invalid gradient_type value. Must be 0 or 1.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Выполняем анализ pH
        try:
            ph_value, red, green, blue = calculate_ph(image, gradient_type=int(request.data.get('gradient_type', 1)))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Сохраняем фотографию
        photo = Photo.objects.create(image=image, created_by=request.user)

        # Сохраняем данные анализа pH
        ph_analysis = PHAnalysis.objects.create(
            photo=photo,
            red=red,
            green=green,
            blue=blue,
            ph_value=ph_value
        )

        # Возвращаем результат анализа
        return Response({'ph_value': ph_value}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_ph_analysis(request):
    if request.method == 'GET':
        user = request.user
        ph_analyses = PHAnalysis.objects.filter(photo__created_by=user)
        serialized_data = PHAnalysisSerializer(ph_analyses, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)


