import urllib, urllib2
import urlparse
from zope.interface import implements, Interface
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('collective.geo.wms')


ALLOWED_CONTENT_TYPES = (
    "application/xml", "text/xml",
    "application/vnd.ogc.se_xml",           # OGC Service Exception
    "application/vnd.ogc.se+xml",           # OGC Service Exception
    "application/vnd.ogc.success+xml",      # OGC Success (SLD Put)
    "application/vnd.ogc.wms_xml",          # WMS Capabilities
    "application/vnd.ogc.context+xml",      # WMC
    "application/vnd.ogc.gml",              # GML
    "application/vnd.ogc.sld+xml",          # SLD
    "application/vnd.google-earth.kml+xml", # KML
    "text/html",                            # HTML returned by get feature info
    )


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
        servers = self.portal_catalog(type=['WMSServer'])
        for brain in servers:
            if brain.getRemoteUrl:
                if brain.getRemoteUrl == baseurl:
                    o = urllib.urlopen(url)
                    if o.headers.type in ALLOWED_CONTENT_TYPES:
                        data = o.read()
                        return data
                    else:
                        logger.error('Response of type "%s" not allowed' %
                            o.headers.type)
