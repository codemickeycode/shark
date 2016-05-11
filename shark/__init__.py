default_app_config = 'shark.apps.SharkConfig'

def urls():
    from shark.urls import get_urls
    return get_urls(), 'shark', 'shark'

