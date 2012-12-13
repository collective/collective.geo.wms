from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IGeoWMSLayer(IDefaultPloneLayer):
    """
    Marker interface that defines a browser layer against which you can register views and viewlets.

    When your theme is selected this layer becomes active and all overrides associated with
    override default Plone render actions.
    """
