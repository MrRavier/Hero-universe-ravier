from pathlib import Path
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
VOL_DIR = ROOT / "canon" / "volumes"
PDF_DIR = ROOT / "canon" / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if regular.exists():
    pdfmetrics.registerFont(TTFont("CanonSans", str(regular)))
    pdfmetrics.registerFont(TTFont("CanonSans-Bold", str(bold)))
    FONT = "CanonSans"
    BOLD = "CanonSans-Bold"
else:
    FONT = "Helvetica"
    BOLD = "Helvetica-Bold"

styles = getSampleStyleSheet()
body = ParagraphStyle("Body", parent=styles["BodyText"], fontName=FONT, fontSize=9.4, leading=13, spaceAfter=5)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName=BOLD, fontSize=20, leading=24, textColor=HexColor("#24364B"), spaceAfter=12)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=BOLD, fontSize=11.5, leading=14, textColor=HexColor("#3667A6"), spaceBefore=8, spaceAfter=3)
meta = ParagraphStyle("Meta", parent=body, fontSize=9, textColor=HexColor("#555555"))
title = ParagraphStyle("Title", parent=h1, fontSize=26, leading=31, alignment=TA_CENTER, spaceAfter=14)
subtitle = ParagraphStyle("Subtitle", parent=body, fontSize=11, leading=15, alignment=TA_CENTER, textColor=HexColor("#555555"))

def clean_inline(s: str) -> str:
    s = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.*?)`", r"<font name='Courier'>\1</font>", s)
    return s

def parse_md(path: Path):
    items=[]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line=="---":
            continue
        if line.startswith("# "):
            items.append(("title", line[2:]))
        elif line.startswith("### "):
            items.append(("h2", line[4:]))
        elif line.startswith("**") and line.endswith("**"):
            items.append(("meta", line.replace("**","")))
        elif line.startswith("- "):
            items.append(("body", "• " + line[2:]))
        else:
            items.append(("body", line))
    return items

def make_pdf(md_path: Path, pdf_path: Path, label: str):
    doc=SimpleDocTemplate(str(pdf_path), pagesize=A4,
        rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=17*mm,
        title=label, author="Hero Universe Ravier")
    story=[Paragraph("HERO UNIVERSE RAVIER", title),
           Paragraph(label, subtitle), Spacer(1,8*mm)]
    for kind,text in parse_md(md_path):
        text=clean_inline(text)
        if kind=="title":
            continue
        if kind=="h2":
            story.append(Paragraph(text,h2))
        elif kind=="meta":
            story.append(Paragraph(text,meta))
        else:
            story.append(Paragraph(text,body))
    doc.build(story)

volumes=sorted(VOL_DIR.glob("volume-*.md"))
for p in volumes:
    make_pdf(p, PDF_DIR / (p.stem + ".pdf"), p.stem.replace("-", " ").title())

master_header = """# BÍBLIA MESTRE - HERO UNIVERSE RAVIER

**Estado:** Cânone Base v0.25  
**Abrangência:** Regras 1-716  
**Continuidade:** única; sem multiverso e sem viagem no tempo.

## Síntese executiva

A Terra segue uma história essencialmente reconhecível. Seres extraordinários existiram desde eras antigas, tornaram-se extremamente raros e voltaram a crescer de forma perceptível entre 1945 e 1960.

Nos últimos anos, aproximadamente 70% da população apresenta algum tipo de manifestação, mas a maioria das capacidades é fraca, cotidiana ou de utilidade limitada. Uma minúscula fração alcança escalas extremas.

Não existe origem única para poderes. Hereditariedade, magia, acidentes, alienígenas, artefatos, entidades, fenômenos espirituais e outras causas coexistem. A ciência compreende mecanismos parciais, não uma teoria total.

Heroísmo é profissão regulamentada, porém os sistemas variam por país. Existem escolas, agências, órgãos públicos, rankings, vigilantes, forças militares extraordinárias e organizações internacionais sobrepostas.

A cosmologia não possui multiverso nem viagem no tempo. Céu, Purgatório e Inferno existem no cânone autoral, embora os personagens não possuam comprovação universal. O teto de poder é desconhecido.

A narrativa é um universo compartilhado de elenco múltiplo. Pode alternar cotidiano escolar, humor, investigação, política, guerra, magia, horror e escala cósmica. Consequências importantes permanecem.

---

"""
parts=[master_header]
for p in volumes:
    txt=p.read_text(encoding="utf-8")
    txt=re.sub(r"^# .*?\n","",txt,count=1)
    parts.append(txt.strip()+"\n")
master=ROOT/"canon"/"BIBLIA_MESTRE.md"
master.write_text("\n\n".join(parts),encoding="utf-8")
make_pdf(master, PDF_DIR/"BIBLIA_MESTRE.pdf", "Bíblia Mestre - Regras 1-716")
print("Generated", len(volumes)+1, "PDFs")
