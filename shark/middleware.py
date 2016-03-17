from django.http import HttpRequest

from shark.models import Log


class Logging:
    def process_request(self, request):
        try:
            log = Log()
            log.url = request.path
            log.referrer = request.META.get('HTTP_REFERER', '')
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')
            cloudflare_ip = request.META.get('HTTP_TRUE_CLIENT_IP', '')
            heroku_ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
            ip_address = request.META.get('REMOTE_ADDR', '')
            log.ip_address = cloudflare_ip or heroku_ip or ip_address
            # CF-IPCountry
            request.shark_log = log
        except Exception:
            print('Exception in Shark logging middleware - process request')

        return None

    def process_response(self, request, response):
        try:
            log = request.shark_log
            log.save()
        except Exception:
            print('Exception in Shark logging middleware - process request')

        return response
