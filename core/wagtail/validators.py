import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse, urlunparse

import validators
from django.utils.translation import gettext_lazy as _


class ParsedURI:
    # create an editable ParseResult object
    def __init__(self, url):
        self.url = url
        self._parsed = urlparse(url)

    @property
    def scheme(self):
        return self._parsed.scheme

    @scheme.setter
    def scheme(self, value):
        self._parsed = self._parsed._replace(scheme=value)

    @property
    def netloc(self):
        return self._parsed.netloc

    @netloc.setter
    def netloc(self, value):
        self._parsed = self._parsed._replace(netloc=value)

    @property
    def path(self):
        return self._parsed.path

    @path.setter
    def path(self, value):
        self._parsed = self._parsed._replace(path=value)

    @property
    def params(self):
        return self._parsed.params

    @params.setter
    def params(self, value):
        self._parsed = self._parsed._replace(params=value)

    @property
    def query(self):
        return self._parsed.query

    @query.setter
    def query(self, value):
        self._parsed = self._parsed._replace(query=value)

    @property
    def fragment(self):
        return self._parsed.fragment

    @fragment.setter
    def fragment(self, value):
        self._parsed = self._parsed._replace(fragment=value)

    @property
    def unparse(self):
        components = [
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        ]
        return urlunparse(components)


class ParsedError(ValueError):
    def __bool__(self):
        return False


def is_valid_href(
    uri,
    protocols=[
        "http",
        "https",
        "ftp",
        "ftps",
        "callto",
        "skype",
        "chrome-extension",
        "facetime",
        "gtalk",
        "mailto",
        "tel",
    ],
    relative=True # allow relative links
):

    result = False
    error = ""

    try:
        parsed_uri = ParsedURI(uri)

        if not parsed_uri.scheme:
            if parsed_uri.path.startswith("/"):
                # handle relative link - assume http/https
                if not (relative and any(scheme in ['http', 'https'] for scheme in protocols)): 
                    raise ParsedError(_("Relative link not permitted."))
                result = validators.url(f"https://example.com{uri}")
                if not result:
                    raise ParsedError(_("Invalid relative path."))
            else:
                # handle missing protocol, try https > mailto > tel
                path = parsed_uri.path.split("/")
                if validators.domain(path[0]):
                    # uri has domain before any '/' character, assume https
                    parsed_uri.scheme = "https"
                    parsed_uri.netloc = path.pop(0)
                    parsed_uri.path = "/".join(path)
                    uri = parsed_uri.unparse
                elif validators.email(parsed_uri.path):
                    # path is email address, assume mailto link
                    parsed_uri.scheme = "mailto"
                    uri = parsed_uri.unparse
                elif parsed_uri.path and re.match(r"^[+\[\] \(\)\-\d,]*$", parsed_uri.path):
                    # path matches phone number, assume tel link
                    parsed_uri.scheme = "tel"
                    uri = parsed_uri.unparse
                elif parsed_uri.scheme and not parsed_uri.scheme in protocols:
                    raise ParsedError(_(f"{parsed_uri.scheme}: Link type not permitted."))
                else:
                    raise ParsedError(
                        _(
                            "Unable to determine link type. Please include full link including URI protocol."
                        )
                    )

        match parsed_uri.scheme:
            case scheme if scheme in ["http", "https", "ftp", "ftps"]:
                result = validators.url(uri)
                if not result:
                    raise ParsedError(_("Invalid URL"))
                
            case "mailto":
                # mailto:<address>[?<header1>=<value1>[&<header2>=<value2>]]
                # each header is one of "to", "cc", "bcc", "subject", "body"
                result = validate_email_uri(uri)
                if not result:
                    error = result
                    raise ValueError()
                
            case "tel":
                # tel://+19995551234
                parsed_uri.path = re.sub(r"[ ()-]", "", parsed_uri.path)
                result = validate_tel_value(parsed_uri.path)
                if not result:
                    error = result
                    raise ValueError()
                
            case "facetime":
                # facetime://+19995551234
                # strip unwanted punctuation
                parsed_uri.netloc = re.sub(r"[ ()-]", "", parsed_uri.netloc)
                result = validate_tel_value(parsed_uri.netloc)
                if not result:
                    error = result
                    raise ValueError()
                
            case url if url in ["callto", "skype"]:
                # skype:<username|phonenumber>[?[add|call|chat|sendfile|userinfo]]
                # callto:<username|phonenumber>
                if re.match(r"^[+\[\] \(\)\-\d,]*$", parsed_uri.path):
                    # link is a phone number
                    parsed_uri.path = re.sub(r"[ ()-]", "", parsed_uri.path)
                    result = validate_tel_value(parsed_uri.path)
                    if not result:
                        error = result
                        raise ValueError()
                else:
                    # link uses username, just check it's alphanumeric
                    if not parsed_uri.path.isalnum():
                        raise ParsedError(f'{parsed_uri.scheme}:username must be alphanumeric.')
                if parsed_uri.scheme == "skype":
                    result = parsed_uri.query in [
                        "",
                        "add",
                        "call",
                        "chat",
                        "sendfile",
                        "userinfo",
                    ]
                    if not result:
                        raise ParsedError('skype link format must be skype:<username|phonenumber>[?[add|call|chat|sendfile|userinfo]]')
                else:
                    result = (parsed_uri.query == "")
                    if not result:
                        raise ParsedError('callto: links do not accept parameters, use skype: instead.')

            case "chrome-extension":
                # chrome-extension://<extensionID>/<pageName>.html
                if not parsed_uri.netloc.isalnum():
                    raise ParsedError(_(f'{parsed_uri.netloc}: chrome extension ID must be alphanumeric'))
                if not len(parsed_uri.netloc) == 32:
                    raise ParsedError(_(f'{parsed_uri.netloc}: chrome extension ID should be 32 characters'))
                match = re.search(r'/([^/]+)\.html', parsed_uri.path)
                if match:
                    match = validators.slug(match.group(1).lower())
                if not match or parsed_uri.path.count('/') != 1:
                    raise ParsedError(_('Incorrect format, use chrome-extension://<extensionID>/<pageName>.html'))
                result = True

            case "gtalk":
                # gtalk:chat?jid=example@gmail.com
                result = (
                    all(
                        item == ""
                        for item in (
                            parsed_uri.netloc,
                            parsed_uri.params,
                            parsed_uri.fragment,
                        )
                    )
                    and parsed_uri.query.startswith("jid=")
                    and validators.email(unquote(parsed_uri.query[4:]))
                )
                if not result:
                    raise ParsedError('gtalk links require the forma gtalk:chat?jid=example@gmail.com')

    except ParsedError as e:
        error = e
    except ValueError:
        pass

    return parsed_uri.unparse if result else error


def validate_email_uri(string):
    valid_params = {"to", "cc", "bcc", "subject", "body"}

    url_parts = urlparse(string)

    try:
        if url_parts.scheme != "mailto":
            raise ParsedError(
                _(
                    "Missing mailto protocol. Reformat link with mailto:user1@domain.com,user2@domain.com?..."
                )
            )

        if not all(
            validators.email(email) for email in unescape(url_parts.path.split(","))
        ):
            raise ParsedError(
                _(
                    "Invalid email address in link. Reformat with mailto:user1@domain.com,user2@domain.com?..."
                )
            )

        if url_parts.query:
            key_value_pairs = unescape(url_parts.query).split("&")
            if not all(
                "=" in pair and all(pair.split("=")) for pair in key_value_pairs
            ):
                raise ParsedError(
                    _(
                        "Value missing key in query string. Reformat with ?key1=value1&key2=value2a,value2b"
                    )
                )
            for key, values in parse_qs(unescape(url_parts.query)).items():
                if key in {"to", "cc", "bcc"}:
                    addresses = values[0].split(",")
                    if not all(validators.email(address) for address in addresses):
                        raise ParsedError(
                            _(f"{key}: Invalid email address for this key")
                        )
                elif key not in valid_params:
                    raise ParsedError(
                        _(
                            f'{key}: Unsupported key - key must be one of {", ".join(valid_params)}'
                        )
                    )

    except Exception as error:
        return error

    return True


def validate_tel_value(value):
    try:
        # Check if string is digits, +'s and commas
        if not re.match(r"^[+\d,]+$", value):
            raise ParsedError(
                _(
                    "Invalid phone number format. Enter an optional '+' followed by digits only. Commas can be used to create a pause for extension dialling."
                )
            )

        # Check if the first character is digit or '+' followed by digit
        if not re.match(r"^(\d|\+\d)", value):
            raise ParsedError(
                _(
                    "Invalid phone number format. Enter an optional '+' followed by digits only. Commas can be used to create a pause for extension dialling."
                )
            )

        # Check that any commas are both preceded and followed by only a comma or digit
        if "," in value and not re.search(r"(?<=[\d,]),(?=[\d,])", value):
            raise ParsedError(
                _(
                    "Invalid phone number format. All commas must be both preceded and followed by only a comma or digit"
                )
            )
    except Exception as error:
        return error

    return True
