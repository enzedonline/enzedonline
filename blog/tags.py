from django.db import models
from modelcluster.models import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.models import TranslatableMixin


class TechBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'TechBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class PersonalBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PersonalBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )
