"""后处理 pandoc 生成的 docx：压缩行距与段前段后间距。

用法:
    python scripts/adjust_docx_spacing.py path/to/file.docx [--body-line 1.15]

默认: 正文 1.15 倍行距、段前 0 / 段后 4pt；标题段前 8pt / 段后 4pt；
表格单元格与代码块 1.0 倍行距、无段前段后。
"""
from __future__ import annotations

import argparse

from docx import Document
from docx.shared import Pt


def adjust(path: str, body_line: float = 1.15) -> None:
    doc = Document(path)

    for p in doc.paragraphs:
        name = (p.style.name or "").lower()
        pf = p.paragraph_format
        if name.startswith("heading"):
            pf.line_spacing = 1.15
            pf.space_before = Pt(8)
            pf.space_after = Pt(4)
        elif name in {"title"}:
            pf.space_after = Pt(10)
        else:
            pf.line_spacing = body_line
            pf.space_before = Pt(0)
            pf.space_after = Pt(4)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    pf = p.paragraph_format
                    pf.line_spacing = 1.0
                    pf.space_before = Pt(0)
                    pf.space_after = Pt(0)

    doc.save(path)
    print(f"adjusted: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="压缩 docx 行距与段间距")
    parser.add_argument("path", help="目标 docx 文件")
    parser.add_argument("--body-line", type=float, default=1.15,
                        help="正文行距倍数，默认 1.15")
    args = parser.parse_args()
    adjust(args.path, args.body_line)
