from shark.base import BaseObject


class GoogleAnalyticsTracking(BaseObject):
    def __init__(self, tracking_code='', **kwargs):
        self.init(kwargs)
        self.tracking_code = self.param(tracking_code, 'string', 'The tracking code, somthing like "UA-1234567-1".')

    def get_js(self):
        js = []
        js.append("(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','//www.google-analytics.com/analytics.js','ga');")
        js.append("ga('create', '{}', 'auto');".format(self.tracking_code))
        js.append("ga('send', 'pageview');")
        return '\r\n'.join(js)