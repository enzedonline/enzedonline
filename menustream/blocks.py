from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (BooleanBlock, CharBlock, IntegerBlock, ListBlock,
                            StreamBlock, StructBlock, StructValue)

from core.wagtail.blocks import (ChoiceBlock, ImageChooserBlock,
                                   PageChooserBlock, URLBlock)


class DisplayWhenChoiceBlock(ChoiceBlock):        
    choices=[
        ('ALWAYS', _("Always")),
        ('True', _("When logged in")),
        ('False', _("When not logged in"))
    ]
    default='ALWAYS'
    help_text=_("Determines if menu item is only shown if user logged in, logged out or always")

class MenuStructBlock(StructBlock):
    icon = ImageChooserBlock(
        required=False,
        widget_attrs={"show_edit_link":False},
        label=_("Optional image for display")
    )
    display_when = DisplayWhenChoiceBlock(required=True)

class PageLinkValue(StructValue):
    @property
    def url(self) -> str:
        page = self.get("page")
        return page.url if page else ''

    @property
    def title(self) -> str:
        display_title = self.get("display_title")
        page = self.get("page")
        return display_title or page.title if page else ''
    
class PageLinkBlock(MenuStructBlock):
    page = PageChooserBlock(widget_attrs={"show_edit_link":False})
    display_title = CharBlock(
        max_length=255, 
        required=False,
        label="Optional Text to Display on Menu",
        help_text="Leave blank to use page title."
    )

    class Meta:
        icon = 'doc-empty'
        template = "menu/link_block.html"
        value_class = PageLinkValue
        label = _("Link to Internal Page")
        label_format = label + ": {page}"

class PageLinkMenuBlock(PageLinkBlock):
    sticky = BooleanBlock(
        required=False,
        help_text=_("Item remains on menu bar in mobile view")
    )

class PageLinkSubMenuBlock(PageLinkBlock):
    pass

class URLLinkValue(StructValue):
    @property
    def url(self) -> str:
        return self.get("url")

    @property
    def title(self) -> str:
        return self.get("title")

class URLLinkBlock(MenuStructBlock):
    url = URLBlock(label="URL")
    title = CharBlock(
        max_length=255, 
        label=_("Text to Display on Menu")
    )

    class Meta:
        icon = 'link'
        template = "menu/link_block.html"
        label = _("URL Link")
        label_format = label + ": {title} ({url})"
        value_class = URLLinkValue

class URLLinkMenuBlock(URLLinkBlock):
    sticky = BooleanBlock(
        required=False,
        help_text=_("Item remains on menu bar in mobile view")
    )

class URLLinkSubMenuBlock(URLLinkBlock):
    pass

class AutoFillBlock(MenuStructBlock):
    # @TODO - look at autofilling from routable pages
    title = CharBlock(
        max_length=50, 
        label="Text to Display on Menu"
    )
    parent_page = PageChooserBlock()
    include_parent_page = BooleanBlock(
        verbose_name = _("Include Parent Page in Sub-Menu"),
        default=False,
        required=False,
        help_text=_("If selected, linked page will included before auto-filled items followed by dividing line")
    )
    only_show_in_menus = BooleanBlock(
        verbose_name = _("Include only 'Show In Menu' pages"),
        default=False,
        required=False,
        help_text=_("If selected, only child pages with 'Show In Menu' selected will be shown.")
    )
    order_by = ChoiceBlock(
        choices=[
            ("-last_published_at", _("Newest (by most recently updated)")),
            ("-first_published_at", _("Newest to Oldest (by date originally published)")),
            ("first_published_at", _("Oldest to Newest")),
            ("title", _("Title (A-Z)")),
        ],
        default="-first_published_at",
        help_text=_("Choose the order in which to show results")
    )
    max_items = IntegerBlock(
        default=4,
        min_value=1,
        blank=False,
        help_text=_("Maximum results to display in the menu")
    )

    class Meta:
        icon = 'list-ul'
        template = "menu/autolink_menu.html"
        label = _("Auto Links Sub-Menu")
        label_format = label + ": {title} ({parent_page})"

class AutoFillMenuBlock(AutoFillBlock):
    sticky = BooleanBlock(
        required=False,
        help_text=_("Item remains on menu bar in mobile view")
    )

class AutoFillSubMenuBlock(AutoFillBlock):
    open_direction = ChoiceBlock(
        choices=[
            ("end", _("Open items to the right")),
            ("start", _("Open items to the left")),
            ("inline", _("Expand submenu inline (accordian)")),
        ],
        default="inline",
        help_text=_("Choose submenu direction.")
    )

    class Meta:
        template = "menu/autolink_submenu.html"

class SubMenuLinkBlock(StreamBlock):
    page_link = PageLinkSubMenuBlock()
    url_link = URLLinkSubMenuBlock()

class SubMenuStreamBlock(SubMenuLinkBlock):
    autofill_submenu = AutoFillSubMenuBlock()

class SubMenuBlock(MenuStructBlock):
    title = CharBlock(
        max_length=50, 
        label=_("Text to Display on Menu")
    )
    sticky = BooleanBlock(
        required=False,
        help_text=_("Item remains on menu bar in mobile view")
    )
    items = SubMenuStreamBlock()

    class Meta:
        icon = 'folder-open-1'
        template = "menu/submenu.html"
        label = _("Sub Menu")
        label_format = label + ": {title}"

class StickyValue(StructValue):
    @property
    def sticky(self):
        return True
    
class SearchMenuBlock(StructBlock):
    display_when = DisplayWhenChoiceBlock(required=True)

    class Meta:
        icon = 'search'
        template = "menu/search.html"
        label = _("Search Form")
        label_format = label
        value_class = StickyValue

class DisplayAlwaysValue(StructValue):
    @property
    def display_when(self):
        return "ALWAYS"
        
class UserMenuBlock(StructBlock):
    logged_in_title = CharBlock(
        max_length=50,
        help_text=_("Menu title when user is logged in.")
    )
    logged_in_text = CharBlock(
        max_length=150,
        required=False,
        help_text=_("Message to display to logged in users. Use @username or @display_name to display those values inline.")
    )
    logged_out_title = CharBlock(
        max_length=50,
        help_text=_("Menu title when user is not logged in.")
    )
    login_in_social_label = CharBlock(
        max_length=50,
        help_text=_("Social connect login label when user is not logged in.")
    )
    items = SubMenuLinkBlock()
    sticky = BooleanBlock(
        required=False,
        help_text=_("Item remains on menu bar in mobile view")
    )

    class Meta:
        icon = 'user'
        template = "menu/user.html"
        label = _("User Menu")
        label_format = label
        value_class = DisplayAlwaysValue

class MenuStreamBlock(StreamBlock):
    page_link = PageLinkMenuBlock()
    url_link = URLLinkMenuBlock()
    autofill_menu = AutoFillMenuBlock()
    sub_menu = SubMenuBlock()
    search_form = SearchMenuBlock(max_num=1)
    user_menu = UserMenuBlock(max_num=1)

    class Meta:
        block_counts = {
            'search_form': {'min_num': 0, 'max_num': 1},
            'user_menu': {'min_num': 0, 'max_num': 1},
        }