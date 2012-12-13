import urllib, urllib2
import urlparse
from time import time
from zope import schema
from zope.event import notify
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from five import grok
from Products.Five import BrowserView

from plone.directives import dexterity, form
from plone.dexterity.events import AddCancelledEvent


from z3c.form import group, field
from z3c.form import button

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize import view, ram, instance

from collective.geo.wms import MessageFactory as _


from owslib.wms import WebMapService
try:
    from owslib.wmts import WebMapTileService
    protocols = ('wms', 'wmts')
    default_protocol = u'wmts'
except ImportError:
    protocols = ('wms', )
    default_protocol = u'wms'

from owslib.wms import ServiceException

# Interface class; used to define content-type schema.



class IWMSServer(form.Schema, IImageScaleTraversable):
    """
    WMS Server
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/wmsserver.xml to define the content type
    # and add directives here as necessary.


    protocol = schema.Choice(
         title=_(u'Protocol'),
         values=protocols,
         required=True,
         default=default_protocol,
    )


    remote_url = schema.TextLine(
            title=_(u"Server URL"),
            description=_(u"URL of the WM(T)S Server"),
            required=True,
        )





# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

#refresh WebMapService once every 100 minutes only
def _wms_server_cachekey(context, fun, url, protocol):
    ckey = [url, time() // (6000), protocol]
    return ckey


class WMSServer(dexterity.Item):
    grok.implements(IWMSServer)

    # Add your class methods and properties here

    @ram.cache(_wms_server_cachekey)
    def _get_service(self, url, protocol):
        if protocol == 'wms':
            return WebMapService(url)
        elif protocol == 'wmts':
            return WebMapTileService(url)

    def get_service(self):
        return self._get_service(self.remote_url, self.protocol)

    def layers(self):
        wms = self.get_service()
        return [(layer.title,id) for id, layer in wms.contents.items()]

    @property
    def getRemoteUrl(self):
        return self.remote_url


# View class
# The view will automatically use a similarly named template in
# wmsserver_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.


class View(grok.View):
    grok.context(IWMSServer)
    grok.require('zope2.View')
    grok.name('view')

    #@view.memoize
    def get_layers(self):
        layers = self.context.layers()
        for layer in layers:
            yield layer[0]



class AddForm(dexterity.AddForm):
    grok.name('collective.geo.wms.wmsserver')



    def updateWidgets(self):
        """ """
        self.fields = self.fields.select('remote_url', 'protocol')
        super(AddForm, self).updateWidgets()


    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        urlobj = urlparse.urlparse(data['remote_url'])
        if urlobj.scheme not in ['http', 'https']:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Invalid URL - must be http or https"), "error")
            return
        if not urlobj.hostname:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Invalid URL - no hostname qualified"), "error")
            return
        url = urlparse.urlunparse([urlobj.scheme, urlobj.netloc,
                                    urlobj.path, None, None, None])
        try:
            if data['protocol'] == 'wms':
                wms = WebMapService(url)
            elif data['protocol'] == 'wmts':
                wms = WebMapTileService(url)
        except (urllib2.HTTPError, ServiceException) as e:
            IStatusMessage(self.request).addStatusMessage(e, "error")
            return
        title= wms.identification.title
        desc = wms.identification.abstract
        tags = wms.identification.keywords
        obj = self.createAndAdd(data)
        if obj is not None:
            obj.setTitle(title)
            obj.setDescription(desc)
            if tags:
                obj.setSubject(tags)
            obj.remote_url = url
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(
                                        _(u"Item created"), "info")

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
                _(u"Add New Item operation cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        notify(AddCancelledEvent(self.context))

class EditForm(dexterity.EditForm):
    grok.context(IWMSServer)

    def updateWidgets(self):
        """ """
        self.fields = self.fields.omit('remote_url', 'protocol')
        super(EditForm, self).updateWidgets()
