from typing import Any

from jinja2 import Template

from app.core.config import BASE_DIR


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template = (
        BASE_DIR / "app" / "email-templates" / "build" / template_name
    ).read_text()
    return Template(source=template).render(context)
