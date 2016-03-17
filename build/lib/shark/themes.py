from .base import BaseObject
from .resources import Resources


class ProfilePanel(BaseObject):
    def __init__(self, name='', profile_pic='', background_pic='', description='', **kwargs):
        self.init(kwargs)

        self.name = self.param(name, 'string', 'Name of the person')
        self.profile_pic = self.param(profile_pic, 'string', 'URL to the picture of the person')
        self.background_pic = self.param(background_pic, 'string', 'URL to a background picture')
        self.description = self.param(description, 'string', 'Description of the person')

    def get_html(self, html):
        html.append('<div class="panel panel-default panel-profile">')
        html.append('    <div class="panel-heading" style="background-image: url({});">'.format(self.background_pic))
        html.append('    </div>')
        html.append('    <div class="panel-body text-center">')
        html.append('        <img class="panel-profile-img" src="{}">'.format(self.profile_pic))
        html.append('        <h5 class="panel-title">{}</h5>'.format(self.name))
        html.append('        <p class="m-b">{}</p>'.format(self.description))
        html.append('    </div>')
        html.append('</div>')


class TwitterFeedWidget(BaseObject):
    def __init__(self, widget_id='', username='', **kwargs):
        self.init(kwargs)
        self.widget_id = self.param(widget_id, 'string', 'Widget ID of the twitter feed')
        self.username = self.param(username, 'string', 'Name of the twitter account')

    def get_html(self, html):
        html.append('<a class="twitter-timeline" href="https://twitter.com/{}" data-widget-id="{}">Tweets by @{}</a>'.format(self.username, self.widget_id, self.username))


Resources.add_resource('/static/shark/css/profile.css', 'css', 'themes', 'profile')