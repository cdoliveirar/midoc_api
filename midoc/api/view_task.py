from .tasks import family_plan_mail, personal_plan, recommendation, recovery
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


class SendEmailsView(APIView):
    def get(self, request, *args, **kwargs):
        family_plan_mail.delay()
        personal_plan.delay()
        recommendation.delay()
        recovery.delay()
        return Response({"status": "ok"})
