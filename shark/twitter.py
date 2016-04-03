from shark.base import BaseObject
from shark.resources import Resources

class TwitterFeedWidget(BaseObject):
    def __init__(self, widget_id='', username='', **kwargs):
        self.init(kwargs)
        self.widget_id = self.param(widget_id, 'string', 'Widget ID of the twitter feed')
        self.username = self.param(username, 'string', 'Name of the twitter account')

    def get_html(self, html):
        html.append('<a class="twitter-timeline" href="https://twitter.com/{}" data-widget-id="{}">Tweets by @{}</a>'.format(self.username, self.widget_id, self.username))

        html.append_js('function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?\'http\':\'https\';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");')
