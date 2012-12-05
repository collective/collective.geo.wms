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

from collective.geo.wms import MessageFactory as _
from collective.geo.wms.wmsserver import IWMSServer

@grok.provider(IContextSourceBinder)
def layers_vocab(context):
    terms = []
    for layer in context.server.to_object.layers():
        terms.append(SimpleVocabulary.createTerm(layer[1],layer[1],layer[0]))
    return SimpleVocabulary(terms)


def isnotempty(value):
    return bool(value)

# Interface class; used to define content-type schema.

class IWMSLayer(form.Schema):
    """
    WMS Layer
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/wmslayer.xml to define the content type
    # and add directives here as necessary.

    server = RelationChoice(
            title=_(u"Server"),
            description=_(u"Choose the WMS Server providing this Layer"),
            source=ObjPathSourceBinder(object_provides=IWMSServer.__identifier__),
            required=True,

        )

    layers = schema.List(
            title=_(u"Layers"),
            description=_(u"WMS Layers"),
            required=True,
            constraint=isnotempty,
            value_type=schema.Choice(
                 source=layers_vocab,
                 required=True,
                 ),
        )

    baselayer = schema.Bool(
            title=_(u"Base Layer"),
            description=_(u"Is the Layer a base layer"),
            required=False,
            default = False,
    )

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class WMSLayer(dexterity.Item):
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
        self.fields = self.fields.omit('server')
        super(EditForm, self).updateWidgets()
