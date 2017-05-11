from shark.base import Text
from shark.objects.dashboard import StatBox
from shark.objects.font_awesome import Icon
from shark.objects.ui_elements import Carousel
from shark.renderer import Renderer

renderer = Renderer()

renderer.render('', StatBox(12, 'Foorbars', Icon.tachometer, 'More', 'http://google.com'))

print('Output:')
print('HTML', renderer.html)
print('CSS', renderer.css)
print('JS', renderer.js)
print(renderer.js_files)
print(renderer.js_resources)
print(renderer.css_files)
print(renderer.css_resources)
