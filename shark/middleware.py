import logging
import traceback

from django.http import HttpRequest

from shark.models import Log
from shark.settings import SharkSettings


class Logging:
    def process_request(self, request):
        try:
            log = Log()
            log.url = request.path
            log.referrer = request.META.get('HTTP_REFERER', '')
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')
            if SharkSettings.CLOUDFLARE_CLIENT_IP_ENABLED:
                real_ip = request.META.get('HTTP_TRUE_CLIENT_IP', '')
            else:
                forwarded_ips_str = request.META.get('HTTP_X_FORWARDED_FOR', '')
                if forwarded_ips_str:
                    forwarded_ips = [ip.strip() for ip in forwarded_ips_str.split(',')]
                    if len(forwarded_ips) < SharkSettings.PROXY_HOPS:
                        logging.warning('SharkSettings.proxy_hops is {}, but only {} hops detected. This is a security issues as this allows for IP spoofing.'.format(SharkSettings.PROXY_HOPS, len(forwarded_ips)))
                        real_ip = forwarded_ips[0]
                    else:
                        real_ip = forwarded_ips[-SharkSettings.PROXY_HOPS]
                else:
                    if SharkSettings.PROXY_HOPS:
                        logging.warning('SharkSettings.proxy_hops is {}, but no hops detected. This is a security issues as this allows for IP spoofing.'.format(SharkSettings.PROXY_HOPS))
                    real_ip = request.META.get('REMOTE_ADDR', '')

            print('IP', real_ip)
            log.ip_address = real_ip
            # CF-IPCountry
            request.shark_log = log
        except Exception:
            print('Exception in Shark logging middleware - process request')
            traceback.print_exc()
        return None

    def process_response(self, request, response):
        try:
            log = request.shark_log
            log.save()
        except Exception:
            print('Exception in Shark logging middleware - process request')
            traceback.print_exc()

        return response
