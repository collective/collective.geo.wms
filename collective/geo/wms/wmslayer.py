from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from Products.CMFCore.utils import getToolByName

from collective.geo.wms import MessageFactory as _
from collective.geo.wms.wmsserver import IWMSServer

@grok.provider(IContextSourceBinder)
def layers_vocab(context):
    terms = []
    for layer in context.server.to_object.layers(context.srs, context.img_format):
        terms.append(SimpleVocabulary.createTerm(layer[1],layer[1],layer[0]))
    return SimpleVocabulary(terms)


def isnotempty(value):
    return bool(value)

# Interface class; used to define content-type schema.

class IWMSLayer(form.Schema):
    """
    WMS/WMTS/TMS Layer
    """

    server = RelationChoice(
            title=_(u"Server"),
            description=_(u"Choose the WM(T)S Server providing this Layer"),
            source=ObjPathSourceBinder(object_provides=IWMSServer.__identifier__),
            required=True,

        )

    layers = schema.List(
            title=_(u"Layers"),
            description=_(u"WM(T)S Layers"),
            required=True,
            constraint=isnotempty,
            value_type=schema.Choice(
                 source=layers_vocab,
                 required=True,
                 ),
        )

    baselayer = schema.Bool(
            title=_(u"Base Layer"),
            description=_(u"Is the (first) Layer a base layer"),
            required=False,
            default = False,
    )

    # wms specific
    singlelayers = schema.Bool(
            title=_(u"Single Layers"),
            description=_(u"""Request the layers seperately from the
            server and overlay them on the client side"""),
            required=False,
            default=False,
    )

    #wmts specific
    img_format = schema.Choice(
         title=_(u'Format'),
         values=('png', 'jpeg'),
         default='png',
         required=True,
    )


    srs = schema.Choice(
         title=_(u'Projection'),
         description=_(u"""Projection (SRS) of the layer"""),
         #XXX Should the vocabulary come out of the layers?
         values=('EPSG:900913', 'EPSG:4326'),
         default='EPSG:900913',
         required=True,
    )



    opacity = schema.Float(
        title=_(u"Opacity"),
        min=0.0,
        max=1.0,
        required=True,
        default=0.7,
    )

    featureinfo = schema.Bool(
            title=_(u"Feature Info"),
            description=_(u"""Get feature info for layers and display it
            in a popup window"""),
            required=False,
            default=False,
    )

    body_text = RichText(
            title=_(u"Body text"),
            description=_(u"Enter an long descrition of your layer"),
            required=False,
    )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class WMSLayer(dexterity.Container):
    grok.implements(IWMSLayer)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# wmslayer_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.



class View(grok.View):
    grok.context(IWMSLayer)
    grok.require('zope2.View')
    grok.name('view')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def get_proxy_js(self):

        if self.context.featureinfo:
            js = """
             /*<![CDATA[*/
            $(window).bind("load", function() {
                OpenLayers.ProxyHost = '%s/@@openlayers_proxy_view?url=';
                var map = cgmap.config['default-cgmap'].map;

                info = new OpenLayers.Control.%sGetFeatureInfo({
                    url: '%s',
                    title: 'Identify features by clicking',
                    queryVisible: true,
                    eventListeners: {
                        getfeatureinfo: function(event) {
                            map.addPopup(new OpenLayers.Popup.FramedCloud(
                                "chicken",
                                map.getLonLatFromPixel(event.xy),
                                null,
                                event.text,
                                null,
                                true
                            ));
                        }
                    }
                });
                map.addControl(info);
                info.activate();
            });
            /*]]>*/
            """ % (self.portal.absolute_url(),
                self.context.server.to_object.protocol.upper(),
                self.context.server.to_object.remote_url)
            return js

class AddForm(dexterity.AddForm):
    grok.name('collective.geo.wms.wmslayer')

    def updateWidgets(self):
        """ """
        self.fields = self.fields.omit('layers')
        super(AddForm, self).updateWidgets()

class EditForm(dexterity.EditForm):
    grok.context(IWMSLayer)

    def updateWidgets(self):
        """ """
        self.fields = self.fields.omit('server', 'srs')
        if self.context.server.to_object.protocol == 'wmts':
            self.fields = self.fields.omit('singlelayers')
        elif self.context.server.to_object.protocol == 'wms':
            self.fields = self.fields.omit('img_format')
        else:
            self.fields = self.fields.omit('singlelayers', 'img_format',
                            'featureinfo')
        super(EditForm, self).updateWidgets()
