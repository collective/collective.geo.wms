import urllib, urllib2
import urlparse
from time import time
from five import grok
from plone.directives import dexterity, form
from plone.dexterity.events import AddCancelledEvent

from zope import schema
from zope.event import notify
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field
from z3c.form import button

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from Products.statusmessages.interfaces import IStatusMessage

from collective.geo.wms import MessageFactory as _

from plone.memoize import view, ram, instance

from owslib.wmts import WebMapTileService
#from owslib.wms import ServiceException

# Interface class; used to define content-type schema.

class IWMTSServer(form.Schema, IImageScaleTraversable):
    """
    TMS Server
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/tmsserver.xml to define the content type
    # and add directives here as necessary.

    remote_url = schema.TextLine(
            title=_(u"Server URL"),
            description=_(u"URL of the WMTS Server"),
            required=True,
        )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

#refresh WebMapTileService once every 100 minutes only
def _wmts_server_cachekey(context, fun, url):
    ckey = [url, time() // (6000)]
    return ckey


class WMTSServer(dexterity.Item):
    grok.implements(IWMTSServer)

    # Add your class methods and properties here

    @ram.cache(_wmts_server_cachekey)
    def _get_wmts_service(self, url):
        return WebMapTileService(url)

    def get_wmts_service(self):
        return self._get_wmts_service(self.remote_url)

    def layers(self):
        wms = self.get_wmts_service()
        return [(layer.title,id) for id, layer in wms.contents.items()]

    @property
    def getRemoteUrl(self):
        return self.remote_url


# View class
# The view will automatically use a similarly named template in
# tmsserver_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(grok.View):
    grok.context(IWMTSServer)
    grok.require('zope2.View')
    grok.name('view')

    #@view.memoize
    def get_layers(self):
        layers = self.context.layers()
        for layer in layers:
            yield layer[0]



class AddForm(dexterity.AddForm):
    grok.name('collective.geo.wms.wmtsserver')

    def updateWidgets(self):
        """ """
        self.fields = self.fields.select('remote_url')
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
            wmts = WebMapTileService(url)
        except urllib2.HTTPError as e:
            IStatusMessage(self.request).addStatusMessage(e, "error")
            return
        title= wmts.identification.title
        desc = wmts.identification.abstract
        tags = wmts.identification.keywords
        obj = self.createAndAdd(data)
        if obj is not None:
            obj.setTitle(title)
            obj.setDescription(desc)
            obj.remote_url = url
            if tags:
                obj.setSubject(tags)
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
    grok.context(IWMTSServer)

    def updateWidgets(self):
        """ """
        self.fields = self.fields.omit('remote_url')
        super(EditForm, self).updateWidgets()
