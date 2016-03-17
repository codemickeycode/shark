#TODO: Is there a Django version of this?
def safe_url(url):
    return url.replace('<', '').replace('>', '').replace('"', '').replace("'", '')

def iif(condition, value_true, value_false=''):
    return value_true if condition else value_false

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


