from django.db import models
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import (FieldPanel, HelpPanel, InlinePanel,
                                  MultiFieldPanel)
from wagtail.models import Orderable, Page, TranslatableMixin
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import SynchronizedField

from core.panels import ReadOnlyPanel, RichHelpPanel
from core.utils import purge_menu_cache_fragments

from .edit_handlers import SubMenuFieldPanel


class MenuListQuerySet(object):
    # Call as class()() to act as a function call, passes all menus to SubMenuPanel dropdown
    # Useful to make a function call in class declaration to make dynamic class variables 
    def __call__(self, *args, **kwds):
        return Menu.objects.all()
        
class MenuForm(WagtailAdminPageForm):
    """ MenuForm - provides validation for Menu & Menu Item orderables
        self.data['id'] comes from the read_only_edit_handler which injects a 
        hidden form field that isn't included in the cleaned_data"""

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        for form in self.formsets['sub_menu_items'].forms:
            if form.is_valid():
                cleaned_form_data = form.clean()
                try:
                    parent_id = self.data['id']
                except MultiValueDictKeyError as e:
                    parent_id = None
                if cleaned_form_data.get('submenu_id') == None:
                    form.add_error('title_of_submenu', "Sub Menu ID cannot be left blank")
                if parent_id != None:
                    if cleaned_form_data.get('submenu_id') == parent_id:
                        form.add_error('title_of_submenu', "Parent Menu cannot be a Sub Menu of itself")
        for form in self.formsets['link_menu_items'].forms:
            if form.is_valid():
                cleaned_form_data = form.clean()
                cleaned_title = cleaned_form_data.get('title')
                cleaned_image = cleaned_form_data.get('icon')
                cleaned_url = cleaned_form_data.get('link_url')
                cleaned_page = cleaned_form_data.get('link_page')
                if (cleaned_title == None) and (cleaned_image == None) and (cleaned_page == None):
                    msg = _("Title, icon and linked page cannot all be left empty. ")
                    form.add_error('title', msg)
                    form.add_error('icon', msg)
                    form.add_error('link_page', msg)
                if (cleaned_url == None) and (cleaned_page == None):
                    msg = _("Linked URL and Linked Page cannot both be left empty. ")
                    form.add_error('link_url', msg)
                    form.add_error('link_page', msg)
        for form in self.formsets['autofill_menu_items'].forms:
            if form.is_valid():
                cleaned_form_data = form.clean()
                cleaned_page = cleaned_form_data.get('link_page')
                if cleaned_page == None:
                    msg = _("Linked page cannot all be left empty. ")
                    form.add_error('link_page', msg)

        return cleaned_data

class MenuPanelsIterable(object):
    # Build the panels as an iterable. Probably not necessary here but it could be useful for a bit
    # of dynamic panel building later on
    # The panels for the submenu form are built here and passed into the InlinePanel 
    # rather than declared in the model itself

    def __iter__(self):
        # build submenu panels, including the FluidIterable for the widget
        submenu_panels = [
            HelpPanel(_("Select the menu that this sub-menu will load")),
            SubMenuFieldPanel("submenu_id", MenuListQuerySet()()),
            FieldPanel("display_option"),
            FieldPanel("show_when"),
            FieldPanel("menu_display_order"),
            FieldPanel("show_divider_after_this_item"),
        ]

        # two custom panels here:
        # ReadOnlyPanel - displays field as a non-field text, optionally adds a hidden input field to 
        #                 allow accessing that field in the clean() method
        # RichHelpPanel - like a django template, swap out {{vars}} for values (field or function returns)
        #                 also allows basic html (formatting, links etc)

        msg=_('Items in the menu will be arranged by <b>Menu Display Order</b> over the order in which they appear below.')
        style="margin-top: -1.5em; margin-bottom: -1.0em;"
        panels = [
            MultiFieldPanel(
                [
                    ReadOnlyPanel("id", heading="Menu ID", add_hidden_input=True),
                    FieldPanel("title"),
                    FieldPanel("icon"),
                ],
                heading=_("Menu Heading"),
            ),
            MultiFieldPanel(
                [
                    RichHelpPanel(
                        msg, 
                        style=style,
                    ),
                ],
                heading=_("Menu Items - Add items to show in the menu below. "),
            ),
            MultiFieldPanel(
                [
                    InlinePanel("sub_menu_items", label=_("Sub-menu"), panels=submenu_panels)
                ],
                heading="Submenus",
                classname="collapsible collapsed",
            ),
            MultiFieldPanel(
                [
                    InlinePanel("link_menu_items", label=_("Link")),
                ],
                heading="Links",
                classname="collapsible collapsed",
            ),
            MultiFieldPanel(
                [
                    InlinePanel("autofill_menu_items", label=_("Autofill Link")),
                ],
                heading="Autofill Links",
                classname="collapsible collapsed",
            ),
        ]
        return panels.__iter__()

@register_snippet
class Menu(TranslatableMixin, ClusterableModel):
    """ Menu Class creates menus to display - validation in MenuForm
        Holds a collection of Menu Item orderables """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    base_form_class = MenuForm

    title = models.CharField(
        max_length=50,
        help_text=_("Title will be used if this is a submenu")
    )

    # Optional image to display if submenu
    icon = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Optional image to display if submenu")
    )
    
    panels = MenuPanelsIterable()

    override_translatable_fields = [
        SynchronizedField("icon", overridable=False),
    ]    

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        purge_menu_cache_fragments()
        super(ClusterableModel, self).save(*args, **kwargs)

class MenuItem(TranslatableMixin, Orderable):
    """ MenuItem Class - orderables to display in Menu class
        Parent class to SubMenuItem and AutoMenuItem classes """

    # hidden field, links item to menu        
    menu = ParentalKey(
        "Menu",
        related_name="menu_items",
        help_text=_("Menu to which this item belongs"),
    )
    
    # show if user logged in, logged out or always
    show_when = models.CharField(
        max_length=15,
        choices=[
            ("always", _("Always")),
            ("logged_in", _("When logged in")),
            ("not_logged_in", _("When not logged in")),
        ],
        default="always",
        help_text=_("Determines if menu item is only shown if user logged in, logged out or always")
    )
    # adds a dividing line after the item if it's on a dropdown menu
    show_divider_after_this_item = models.BooleanField(
        default=False,
        help_text=_("Add a dividing line after this menu item if on a dropdown menu.")
    )
    # allow menu items to be sorted regardless of type
    menu_display_order = models.IntegerField(
        default=200,
        help_text=_("Enter digit to determine order in menu. Menu items of all types will be sorted by this number")
    )

    class Meta:
        abstract = True

    def show(self, authenticated):
        return (
            (self.show_when == "always")
            or (self.show_when == "logged_in" and authenticated)
            or (self.show_when == "not_logged_in" and not authenticated)
        )

    def __str__(self):
        return self.title

class LinkMenuItem(MenuItem):
    """
    Creates a standard link item for the menu.
    Use page link for internal pages, url for external links or routable pages
    If both are used, the text in url is appended to the page url 
    (eg /blog/catgories/ + events or /blog/ + ?cat=events)
    """
    # hidden field, links item to menu        
    menu = ParentalKey(
        "Menu",
        related_name="link_menu_items",
        help_text=_("Menu to which this item belongs"),
    )

    # the text to show in the menu - can only be blank if image is not also blank
    # or blank if link page (link page title will be used)
    title = models.CharField(
        max_length=50, 
        blank=True,
        null=True,
        help_text=_("Title to display in menu"),
    )
    # Optional image to display on menu - if title is blank, only image will show
    icon = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Optional image to display on menu - if title is blank, only image will show")
    )

    # this field can be used to provide an external url or internal url 
    # for internal url's, must omit the language code from the url (ie /accounts/ not /en/accounts/)
    # if used with a link page, provides a suffix to the url of that page
    link_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_(
            "If using link page, any text here will be appended to the page url. " +
            "For an internal url without page link, leave off the language specific part of the url " +
            "(ie /accounts/ not /en/accounts/)."
        ),
    )
    # wagtail page to link to
    # if value entered in link_url, it will be appended to the url of this page
    # eg link page = /blog/categories/, link_url = news -> menu item url = /blog/categories/news/
    # useful for routable pages
    # could also to POST arguments to a page (eg link_url = ?cat=news -> /blog/categories/?cat=news)
    link_page = models.ForeignKey(
        Page,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
        help_text=_(
            "Use this to link to an internal page. Link to the page in the language of this menu."
        ),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("icon"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
        FieldPanel("show_when"),
        FieldPanel("menu_display_order"),
        FieldPanel("show_divider_after_this_item"),
    ]

    override_translatable_fields = [
        SynchronizedField("icon", overridable=False),
        SynchronizedField("link_page", overridable=False),
    ]    

    class Meta:
        unique_together = ('translation_key', 'locale')

class AutofillMenuItem(MenuItem):
    """
    Creates links dynamically on the menu based on criteria
    Link to a page, choose what to return (most recent publish, most recent update, oldest), 
    and how many results to return. Also, if to include the linked page itself or not.
    This will not iterate down or create nested menus, for linear auto-fill only.
    To add another layer, create a submenu and add another autofill there.
    @TODO - look at autofilling from routable pages or other non-page urls
    """
    # hidden field, links item to menu        
    menu = ParentalKey(
        "Menu",
        related_name="autofill_menu_items",
        help_text=_("Menu to which this item belongs"),
    )

    # optional description to describe what this item will load
    description = models.CharField(
        max_length=50, 
        blank=True,
        null=True,
        help_text=_("Optional field to describe what this item will load. Titles will come from the pages."),
    )

    # wagtail page to link to
    # if value entered in link_url, it will be appended to the url of this page
    # eg link page = /blog/categories/, link_url = news -> menu item url = /blog/categories/news/
    # useful for routable pages
    # could also to POST arguments to a page (eg link_url = ?cat=news -> /blog/categories/?cat=news)
    link_page = models.ForeignKey(
        Page, 
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
        help_text=_(
            "Use this to link to an internal page. Link to the page in the language of this menu."
        ),
    )

    include_linked_page = models.BooleanField(
        verbose_name = _("Include Linked Page in Menu"),
        default=False,
        help_text=_("If selected, linked page will included before auto-filled items followed by dividing line")
    )
    only_show_in_menus = models.BooleanField(
        verbose_name = _("Include only 'Show In Menu' pages"),
        default=False,
        help_text=_("If selected, only pages with 'Show In Menu' selected will be shown.")
    )
    max_items = models.IntegerField(
        default=4,
        blank=False,
        help_text=_("Maximum results to display in the menu")
    )

    # the page order that the results will come from and display in
    order_by = models.CharField(
        max_length=20,
        choices=[
            ("-last_published_at", _("Newest (by most recently updated)")),
            ("-first_published_at", _("Newest to Oldest (by date originally published)")),
            ("first_published_at", _("Oldest to Newest")),
        ],
        default="-first_published_at",
        help_text=_("Choose the order in which to take results")
    )
    panels = [
        FieldPanel("description"),
        FieldPanel("link_page"),
        FieldPanel("include_linked_page"),
        FieldPanel("only_show_in_menus"),
        FieldPanel("max_items"),
        FieldPanel("show_when"),
        FieldPanel("order_by"),
        FieldPanel("menu_display_order"),
        FieldPanel("show_divider_after_this_item"),
    ]

    override_translatable_fields = [
        SynchronizedField("link_page", overridable=False),
    ]    

    class Meta:
        unique_together = ('translation_key', 'locale')

class SubMenuItem(MenuItem):
    """ Class SubMenuItem - child of MenuItem
        Used to add a sub menu to a parent menu - submenu must exist first 
        Panels declared in Menu Class
        Uses custom SubMenuPanel to filter drop down list of menus you can select
        List is filtered to only the same language as parent menu, and exclude parent menu itself
    """

    # hidden field, links item to menu        
    menu = ParentalKey(
        "Menu",
        related_name="sub_menu_items",
        help_text=_("Menu to which this item belongs"),
    )

    # kind of a foreign key, but to the menu table - link to load another menu as submenu
    submenu_id = models.IntegerField(
        blank=False,
        null=True,
        help_text=_("Select the sub-menu to load"),
        verbose_name=_("Submenu"),
    )

    # show if user logged in, logged out or always
    display_option = models.CharField(
        max_length=4,
        choices=[
            ("both", _("Icon & Title")),
            ("text", _("Title Only")),
            ("icon", _("Icon Only")),
        ],
        default="text",
        help_text=_("Display the sub-menu as icon, text or both.")
    )

    # panels = [Declared in Menu and added to InlinePanel]

    class Meta:
        unique_together = ('translation_key', 'locale')
 


