from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.viewsets.pages import PageListingViewSet

from .detail_page import BlogDetailPage


class BlogPageListingViewSet(PageListingViewSet):
    model = BlogDetailPage
    menu_label = "Blog Pages"
    icon = "blog"
    add_to_admin_menu = True
    columns = list(PageListingViewSet.columns)
    columns.insert(
        3, DateColumn("first_published_at", label="First Published", sort_key="first_published_at")
    )
    ordering = ['-first_published_at']

    def get_index_view_kwargs(self, **kwargs):
        index_view_kwargs = super().get_index_view_kwargs(**kwargs)
        return index_view_kwargs
    
blog_page_listing_viewset = BlogPageListingViewSet("blog_detail_pages")
