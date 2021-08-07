from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag
from recipes import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """"Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Return object for current loggied in user"""
        return self.queryset \
                   .filter(user=self.request.user.id).order_by('-name')
