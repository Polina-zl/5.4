from django import template
import re

register = template.Library()


@register.filter(name='censor')
def censor(value):
    """
    Заменяет нежелательные слова на звёздочки
    """
    if not isinstance(value, str):
        return value

    forbidden_words = ['редиска', 'дурак', 'идиот', 'глупый', 'журналист']
    result = value

    for word in forbidden_words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        replacement = '*' * len(word)
        result = pattern.sub(replacement, result)

    return result