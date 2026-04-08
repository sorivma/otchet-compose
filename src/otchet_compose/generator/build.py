from pathlib import Path

from docx import Document

from .blocks import REGISTRY, RenderContext
from .content import add_toc
from .page import add_page_number, setup_page
from .styles import setup_styles


def _remove_initial_empty_paragraph(doc) -> None:
    if len(doc.paragraphs) == 1 and not doc.paragraphs[0].text:
        paragraph = doc.paragraphs[0]._element
        paragraph.getparent().remove(paragraph)


def generate_document(config: dict) -> None:
    document_cfg = config["document"]
    content = config["content"]

    doc = Document()

    setup_page(doc, hide_first_page_number=document_cfg.get("reserve_title_page", False))
    setup_styles(doc)
    _remove_initial_empty_paragraph(doc)

    ctx = RenderContext()

    if document_cfg.get("reserve_title_page", False):
        doc.add_paragraph("")
        doc.add_page_break()

    if document_cfg["toc"]:
        add_toc(doc)
        ctx.current_page_has_content = True

    for block in content:
        REGISTRY[block["type"]].render(doc, block, ctx)

    add_page_number(doc.sections[0])

    output_path = Path(document_cfg["output"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))

    print(f"Отчёт сохранён: {output_path}")
