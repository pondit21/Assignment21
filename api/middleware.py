import uuid

from django.utils.deprecation import MiddlewareMixin


class VisitorMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        from .models import Visitor

        visitor_id = request.META.get('HTTP_X_VISITOR_ID') or request.COOKIES.get('visitor_id')
        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        Visitor.objects.get_or_create(visitor_id=visitor_id)
        response['X-Visitor-Id'] = visitor_id
        response.set_cookie('visitor_id', visitor_id, max_age=60 * 60 * 24 * 30, httponly=False, samesite='Lax')
        return response
