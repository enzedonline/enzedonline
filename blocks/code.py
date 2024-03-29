from django.utils.translation import gettext_lazy as _
from wagtail.blocks import StructBlock, CharBlock, BooleanBlock, TextBlock
from .choices import DefaultChoiceBlock, CollapsibleChoiceBlock

class CodeChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('python', 'Python'),
        ('css', 'CSS'),
        ('html', 'HTML'),
        ('javascript', 'Javascript'),
        ('bash', 'Bash/Shell'),
        ('django', 'Django Template'),
        ('json', 'JSON'),
        ('sql', 'SQL'),
        ('xml', 'XML'),
        ('git', 'Git'),
        ('powershell', 'PowerShell'),
        ('r', 'R'),
        ('vba', 'VBA'),
        ('vbnet', 'VB.NET'),
    ]

class BlogCodeBlock(StructBlock):
    title = CharBlock(required=False)
    type = CollapsibleChoiceBlock(required=True, default='simple')
    language = CodeChoiceBlock(default='python')
    code = TextBlock()
    bottom_padding = BooleanBlock(
        label=_("Include extra space beneath code block?"),
        required=False,
        default=True
        )

    translatable_fields = []

    class Meta:
        template = "blocks/code_block_wrapper.html"
        icon = "code"
        label = _("Code Block")
        label_format = "{language} {title}"
        form_classname = 'struct-block flex-block blog-code-block'