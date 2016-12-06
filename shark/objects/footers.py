from django.utils.timezone import now

from shark.handler import Container
from shark.objects.base import Raw
from shark.objects.layout import Footer, Row, Div, Paragraph, Spacer
from shark.objects.lists import UnorderedList, ListItem


def simple_footer(company_name, *items):
    list_items = []
    if items:
        list_items.append(ListItem(items[0]))

        for item in items[1:]:
            list_items.append(ListItem(Raw('&sdot;')))
            list_items.append(ListItem(item))

    return Footer(Container(Row(Div(_class='col-lg-12', items=[
        Spacer(),
        UnorderedList(_class='list-inline', items=[item for item in list_items]),
        Paragraph(_class='copyright text-muted small', items=[
            Raw('Copyright &copy;'), ' {} {}. All Rights Reserved'.format(company_name, now().year)
        ])
    ]))))
