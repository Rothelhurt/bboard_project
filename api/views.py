from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from main.models import Bb, Comment, Rubric
from .serializers import *


@api_view(['GET'])
def bbs(request):
    """Контроллер, выводяший последние 10 активных объявлений."""
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)


class BbDetailView(RetrieveAPIView):
    """Контроллер, выводящий сведнья об одном объявлении."""
    queryset = Bb.objects.filter(is_active=True)
    serializer_class = BbDetailSerializer


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def comments(request, pk):
    """Контроллер просмотра и добавления комментариев."""
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)
    else:
        comment = Comment.objects.filter(is_active=True, bb=pk)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def rubrics(request):
    """Контроллер просмотра всех рубрик."""
    if request.method == 'GET':
        rubrics = Rubric.objects.all()
        serializer = RubricSerializer(rubrics, many=True)
        return Response(serializer.data)
