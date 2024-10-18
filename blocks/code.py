from django import forms
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (BooleanBlock, CharBlock, ChoiceBlock, RawHTMLBlock,
                            StructBlock)
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.telepath import register

class CodeChoiceBlock(ChoiceBlock):
    choices=[
        ('plaintext', _('Plain Text')),
        ('python', 'Python'),
        ('django', 'Django Template'),
        ('javascript', 'Javascript'),
        ('typescript', 'Typescript'),
        ('css', 'CSS'),
        ('scss', 'SCSS'),
        ('xml', 'HTML / XML'),
        ('shell', 'Bash/Shell'),
        ('json', 'JSON'),
        ('markdown', 'Markdown'),
        ('nginx', 'Nginx'),
        ('sql', 'SQL'),
        ('pgsql', 'PostGRES SQL'),
        ('r', 'R'),
        ('powershell', 'PowerShell'),
    ]

class CollapsibleChoiceBlock(ChoiceBlock):
    choices=[
        ('', _('Not Collapsible')),
        ('collapsible', _('Collapsible')),
        ('collapsed', _('Collapsed')),
    ]    

class BlogCodeBlock(StructBlock):
    title = CharBlock(label=_("Title"), required=False)
    collapsible = CollapsibleChoiceBlock(label=_("Format"), required=False)
    language = CodeChoiceBlock(label=_("Language"), default='python')
    code = RawHTMLBlock(label=_("Code"))
    bottom_padding = BooleanBlock(
        label=_("Include extra space beneath code block?"),
        required=False,
        default=True
        )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['expand_prompt'] = _("Click to expand")
        context['copy_button_text'] = {
            'copy': _("Copy"),
            'copied': _("Copied"),
            'error': _("Error"),
        }
        return context

    translatable_fields = []

    class Meta:
        template = "blocks/code-block-wrapper.html"
        icon = "code"
        label = _("Code Block")
        label_format = "{language} {title}"
        form_classname = 'struct-block code-block'

class CodeBlockAdapter(StructBlockAdapter):
    js_constructor = "blocks.code.BlogCodeBlock"

    base_library_path = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/"
    language_base_path = base_library_path + "languages/"
    admin_theme_path = base_library_path + "styles/github-dark.min.css"

    def js_args(self, block):
        args = super().js_args(block)
        # keys added to args[2] found in this.meta in StructBlockDefinition
        args[2]['language_base_path'] = self.language_base_path
        args[2]['text'] = {
            'languageScriptErrorLabel': _("Failed to load language"),
            'highlighterErrorLabel': _("Error highlighting code")
        }
        return args
        
    @cached_property
    def media(self):
        structblock_media = super().media
        return forms.Media(
            js=structblock_media._js + [
                "js/admin/code-block-adapter.js",
                f"{self.base_library_path}highlight.min.js"
            ],
            css={"all": (
                "css/admin/code-block-form.css",
                self.admin_theme_path
            )},
        )

register(CodeBlockAdapter(), BlogCodeBlock)
