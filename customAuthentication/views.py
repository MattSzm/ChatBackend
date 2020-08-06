from django.http import Http404
from allauth.account.views import ConfirmEmailView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        """
        Response for registration confirmation
        """
        try:
            self.object = self.get_object()
        except Http404:
            self.object = None
            return JsonResponse({"confirmed": False})

        confirmation = self.object
        confirmation.confirm(self.request)
        request.user = None
        return JsonResponse({"confirmed": True})


@api_view(['GET'])
def redirect_after_social_auth(request, *args, **kwargs):
    return Response(status=status.HTTP_200_OK)


