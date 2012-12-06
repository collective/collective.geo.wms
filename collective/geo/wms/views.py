import urllib, urllib2
import urlparse
from zope.interface import implements, Interface
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

class IProxy(Interface):
    """
    Proxy view interface
    """

class Proxy(BrowserView):
    """
    A simple proxy to redirect Openlayers request to a remote server
    """


    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def __call__(self):
        url = urllib.unquote(self.request['url'])
        urlobj = urlparse.urlparse(url)
        if urlobj.scheme not in ['http', 'https']:
            return
        if not urlobj.hostname:
            return
        baseurl = urlparse.urlunparse([urlobj.scheme, urlobj.netloc,
                    urlobj.path, None, None, None])
        servers = self.portal_catalog(type=['TMSServer', 'WMSServer'])
        for brain in servers:
            if brain.getRemoteUrl:
                if brain.getRemoteUrl == baseurl:
                    data = urllib.urlopen(url).read()
                    return data

