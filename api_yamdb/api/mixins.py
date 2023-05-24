from rest_framework import filters, mixins, viewsets
from api.permissions import IsAdmin, ReadOnly


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = [IsAdmin | ReadOnly]
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
