from django_pluggableappsettings import AppSettings, Setting, IntSetting, StringSetting


class SharkSettings(AppSettings):
    SHARK_PAGE_HANDLER = StringSetting('')
    SHARK_USE_STATIC_PAGES = Setting(True)
    SHARK_GOOGLE_ANALYTICS_CODE = StringSetting('')
    CLOUDFLARE_CLIENT_IP_ENABLED = Setting(False)
    PROXY_HOPS = IntSetting(2)
    SHARK_GOOGLE_VERIFICATION = StringSetting('')
    SHARK_BING_VERIFICATION = StringSetting('')
    SHARK_YANDEX_VERIFICATION = StringSetting('')
    SHARK_GOOGLE_BROWSER_API_KEY = StringSetting('')
    SHARK_FACEBOOK_APP_ID = StringSetting('')
    SHARK_FACEBOOK_SECRET = StringSetting('')