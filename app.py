from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT
import io, os

app = Flask(__name__)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    f = request.json
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)
    
    s_small = ParagraphStyle('small', fontSize=8, leading=11, textColor=colors.HexColor('#666666'))
    s_label = ParagraphStyle('label', fontSize=8, textColor=colors.HexColor('#888888'), leading=11)
    s_value = ParagraphStyle('value', fontSize=9, fontName='Helvetica-Bold', leading=13)
    story = []

    header_data = [
        [Paragraph(f'<b>{f["fournisseur"]}</b>', ParagraphStyle('fn', fontSize=14, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a1a2e'))),
         Paragraph('FACTURE', ParagraphStyle('fac', fontSize=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#2d3a8c'), alignment=TA_RIGHT))],
        [Paragraph(f.get('adresse',''), s_small),
         Paragraph(f'N° {f["num"]}', ParagraphStyle('num', fontSize=10, textColor=colors.HexColor('#2d3a8c'), alignment=TA_RIGHT))],
        [Paragraph(f'SIRET : {f.get("siret","")}', s_small),
         Paragraph(f'Date : {f["date"]}', ParagraphStyle('dt', fontSize=9, alignment=TA_RIGHT))],
        [Paragraph(f'N° TVA : {f.get("tva_num","")}', s_small), ''],
    ]
    header_table = Table(header_data, colWidths=[90*mm, 80*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(header_table)
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#2d3a8c')))
    story.append(Spacer(1, 6*mm))

    client_data = [
        [Paragraph('FACTURER À :', s_label)],
        [Paragraph('<b>PEINTHEA SAS</b>', s_value)],
        [Paragraph('12 rue des Artisans, 75011 Paris', s_small)],
        [Paragraph('SIRET : 852 741 963 00024', s_small)],
    ]
    client_table = Table(client_data, colWidths=[170*mm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f6fa')),
        ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (0,0), 8), ('BOTTOMPADDING', (0,-1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-2), 2),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 6*mm))

    table_data = [['Description', 'HT', 'TVA', 'TTC']]
    table_data.append([f'{f["fournisseur"]} — Facture corrigée', f'{f["ht"]}€', f'{f["tva"]}€', f'{f["ttc"]}€'])
    items_table = Table(table_data, colWidths=[95*mm, 25*mm, 25*mm, 25*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d3a8c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4*mm))

    totaux_data = [
        ['', 'Total HT :', f'{f["ht"]}€'],
        ['', 'TVA (20%) :', f'{f["tva"]}€'],
        ['', Paragraph('<b>TOTAL TTC :</b>', ParagraphStyle('ttc', fontSize=10, fontName='Helvetica-Bold')),
         Paragraph(f'<b>{f["ttc"]}€</b>', ParagraphStyle('ttcv', fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT))],
    ]
    totaux_table = Table(totaux_data, colWidths=[95*mm, 45*mm, 30*mm])
    totaux_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEABOVE', (1,2), (-1,2), 1, colors.HexColor('#2d3a8c')),
        ('BACKGROUND', (1,2), (-1,2), colors.HexColor('#eef0fa')),
    ]))
    story.append(totaux_table)
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph('Conditions de paiement : 30 jours à réception — Virement bancaire', s_small))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', 
                     download_name=f'facture_{f["fournisseur"]}_{f["num"]}_CORRIGEE.pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
