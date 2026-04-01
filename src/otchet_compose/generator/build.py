from pathlib import Path

from docx import Document

from .content import add_body_paragraph, add_figure, add_heading, add_toc
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

    setup_page(
        doc,
        hide_first_page_number=document_cfg.get("reserve_title_page", False),
    )
    setup_styles(doc)
    _remove_initial_empty_paragraph(doc)

    current_page_has_visible_content = False

    if document_cfg.get("reserve_title_page", False):
        doc.add_paragraph("")
        doc.add_page_break()
        current_page_has_visible_content = False

    if document_cfg["toc"]:
        add_toc(doc)
        current_page_has_visible_content = True

    figure_counter = 0

    for block in content:
        block_type = block["type"]

        if block_type == "heading":
            page_break_before = block["structural"] and current_page_has_visible_content
            add_heading(
                doc,
                text=block["text"],
                level=block["level"],
                structural=block["structural"],
                page_break_before=page_break_before,
            )
            current_page_has_visible_content = True
            continue

        if block_type == "paragraph":
            add_body_paragraph(doc, block["text"])
            current_page_has_visible_content = True
            continue

        if block_type == "figure":
            figure_counter += 1
            add_figure(
                doc,
                caption=block["caption"],
                image_path=block.get("path"),
                figure_number=figure_counter,
            )
            current_page_has_visible_content = True
            continue

        raise ValueError(f"Неподдерживаемый тип блока: {block_type!r}")

    add_page_number(doc.sections[0])

    output_path = Path(document_cfg["output"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))

    print(f"Отчёт сохранён: {output_path}")