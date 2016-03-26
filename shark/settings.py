from django_pluggableappsettings import AppSettings, Setting, IntSetting, StringSetting


class SharkSettings(AppSettings):
    SHARK_PAGE_HANDLER = Setting(None)
    SHARK_USE_STATIC_PAGES = Setting(True)
    SHARK_STATIC_AMP = Setting(False)
    SHARK_GOOGLE_ANALYTICS_CODE = Setting(None)
    CLOUDFLARE_CLIENT_IP_ENABLED = Setting(False)
    PROXY_HOPS = IntSetting(2)
    SHARK_GOOGLE_VERIFICATION = StringSetting(None)
    SHARK_BING_VERIFICATION = StringSetting(None)
    SHARK_YANDEX_VERIFICATION = StringSetting(None)
    SHARK_GOOGLE_BROWSER_API_KEY = StringSetting(None)
    SHARK_FACEBOOK_APP_ID = StringSetting(None)
    SHARK_FACEBOOK_SECRET = StringSetting(None)