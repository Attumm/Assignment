from typing import Optional, Union

from fastapi import Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from dicttoxml2 import dicttoxml  # type: ignore


from .models import Quote

OUTPUT_FORMAT = {
    "xml": "application/xml",
    "html": "text/html",
    "json": "application/json",
    "text": "text/plain",
}


def get_format_from_url(url_path: str, output_format: Optional[dict[str, str]] = None) -> Union[str, None]:
    """Extract format from URL path if it matches allowed output formats.

    Args:
        url_path: The URL path to extract format from.
        output_format: Optional list of allowed output formats.

    Returns:
        Extracted format if found and allowed, else None.
    """
    if output_format is None:
        output_format = OUTPUT_FORMAT
    if "." in url_path:
        val = url_path.split(".")[-1]
        if val in output_format:
            return val
    return None


def get_output_format(request: Request) -> str:
    """Determine output format based on URL and Accept header.

    Args:
        request: The incoming HTTP request.

    Returns:
        output_format (str): Determined output format as a string.
            Can be 'json', 'xml', etc. based on Accept header and URL.

    Warning:
        Doesn't fully adhere to rfc7231.
        https://www.rfc-editor.org/rfc/rfc7231#section-5.3.2
    """
    output_format = get_format_from_url(request.url.path)
    if output_format is not None:
        return output_format

    output_format = "json"

    accept_header = request.headers.get("Accept")
    if accept_header is None:
        return output_format

    if "text/html" in accept_header:
        output_format = "html"
    elif "application/xml" in accept_header:
        output_format = "xml"
    elif "text/plain" in accept_header:
        output_format = "text"

    return output_format


def quote_to_html(quote: Quote) -> str:
    """Convert a quote dictionary to an HTML string.

    Should be done with Jinja templating, but sonic we have to go fast.

    Args:
        quote: Dictionary containing 'content' and 'author' of the quote.

    Returns:
        HTML string representation of the quote.
    """
    return f"""
<div style="font-family: Arial, sans-serif; max-width: 500px; margin: 20px auto; padding: 15px;
border: 1px solid #e1e8ed; border-radius: 12px; background-color: #ffffff;">
    <p style="font-size: 18px; line-height: 1.4; margin-bottom: 10px;">"{quote.text}"</p>
    <p style="color: #657786; font-size: 15px; margin: 0;">— {quote.author}</p>
</div>
"""


def response_formatter(quote: Quote, output_format: str) -> Response:
    """Format response data based on specified output format.

    Args:
        quote: quote containing response quote.
        output_format: Desired output format (json, xml, html, or text).

    Returns:
        Formatted response object based on output_format.

    """
    if output_format == "json":
        return JSONResponse(content=quote.to_dict())
    if output_format == "xml":
        xml = dicttoxml(quote.to_dict(), custom_root='response', attr_type=False)
        return Response(content=xml, media_type="application/xml")
    if output_format == "html":
        html_content = quote_to_html(quote)
        return HTMLResponse(content=html_content)
    if output_format == "text":
        return PlainTextResponse(str(quote.to_dict()))

    return JSONResponse(
        status_code=400,
        content={"message": f"Unsupported format: {format}"}
    )
