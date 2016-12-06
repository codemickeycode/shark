from shark.base import Text
from shark.objects.ui_elements import Carousel
from shark.renderer import Renderer

renderer = Renderer()

renderer.render('', Carousel([Text("Test"), Text("Test2")]))

print('Output:')
print('HTML', renderer.html)
print('CSS', renderer.css)
print('JS', renderer.js)
print(renderer.js_files)
print(renderer.js_resources)
print(renderer.css_files)
print(renderer.css_resources)
