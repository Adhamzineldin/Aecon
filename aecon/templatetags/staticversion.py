import os
import posixpath
import stat
import urllib

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders

register = template.Library()

@register.simple_tag
def staticversion(path):
    normalized_path = posixpath.normpath(urllib.parse.unquote(path)).lstrip('/')
    absolute_path = finders.find(normalized_path)
    if not absolute_path and getattr(settings, 'STATIC_ROOT', None):
        absolute_path = os.path.join(settings.STATIC_ROOT, path)
    if absolute_path:
        #print("abolute path",absolute_path)#,settings.DEBUG,settings.STATIC_URL, path, os.stat(absolute_path)[stat.ST_MTIME])
        if settings.DEBUG:
            #print(path)
           # print(' full path would be /%s%s?v=%s' % (path.split("/")[0] + settings.STATIC_URL, path.split("/")[1:], "HI"))

            return '%s%s?v=%s' % (settings.STATIC_URL, path, os.stat(absolute_path)[stat.ST_MTIME])
        else:
            return '%s%s?v=%s' % (settings.STATIC_URL, path, os.stat(absolute_path)[stat.ST_MTIME])
            #print(' full path would be /%s%s?v=%s' % (path.split("/")[0]   + settings.STATIC_URL,  path.split("/")[1:], os.stat(absolute_path)[stat.ST_MTIME]))
            return '/%s%s?v=%s' % (path.split("/")[0]   + settings.STATIC_URL,  path.split("/")[1:], os.stat(absolute_path)[stat.ST_MTIME])
    return path



if __name__ == "__main__":
    print(staticversion("aecon/static/media/icons/flat-packs/style.css"))