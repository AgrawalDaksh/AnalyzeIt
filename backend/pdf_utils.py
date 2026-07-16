import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_interview_pdf(candidate_name, difficulty, questions_data):
    """
    Generates a tailored interview guide using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'InterviewTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=10
    )
    
    meta_style = ParagraphStyle(
        'InterviewMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )
    
    category_style = ParagraphStyle(
        'CategoryHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    question_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    answer_style = ParagraphStyle(
        'IdealAnswerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#16a34a'),
        leftIndent=15,
        spaceAfter=4
    )
    
    criteria_style = ParagraphStyle(
        'CriteriaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4b5563'),
        leftIndent=15,
        spaceAfter=8
    )
    
    story.append(Paragraph("AI-Generated Interview Questions Guide", title_style))
    story.append(Paragraph(f"<b>Candidate:</b> {candidate_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Difficulty:</b> {difficulty.capitalize()}", meta_style))
    
    categories = {
        "technical": "💻 Technical Questions",
        "behavioral": "🤝 Behavioral Questions",
        "project": "🚀 Project-based Questions",
        "missing_skill": "⚠️ Missing Skill Questions"
    }
    
    for key, label in categories.items():
        q_list = questions_data.get(key, [])
        if not q_list:
            continue
            
        story.append(Paragraph(label, category_style))
        
        # Horizontal divider line via table
        divider = Table([['']], colWidths=[540], rowHeights=[1])
        divider.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider)
        story.append(Spacer(1, 6))
        
        for idx, item in enumerate(q_list):
            q_num = idx + 1
            story.append(Paragraph(f"Q{q_num}: {item.get('question', '')}", question_style))
            story.append(Paragraph(f"<b>Ideal Answer:</b> {item.get('ideal_answer', '')}", answer_style))
            story.append(Paragraph(f"<b>Evaluation Criteria:</b> {item.get('criteria', '')}", criteria_style))
            
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_reportlab_pdf(job_profile, ranked_candidates):
    """
    Generates a structured recruitment match report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    normal_text = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    
    bold_text = ParagraphStyle(
        'BoldText',
        parent=normal_text,
        fontName='Helvetica-Bold'
    )
    
    # 1. Document Title
    story.append(Paragraph("AnalyzeIt - Recruitment & Match Report", title_style))
    
    # Timestamp
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<b>Generated Timestamp:</b> {now}", normal_text))
    story.append(Spacer(1, 15))
    
    # 2. Job Description Summary Section
    story.append(Paragraph("📋 Job Description Summary", section_heading))
    
    # Fetch parameters
    jd_title = job_profile.get("job_title") or "N/A"
    company = job_profile.get("company") or "N/A"
    req_skills = ", ".join(job_profile.get("required_skills", [])) or "None"
    pref_skills = ", ".join(job_profile.get("preferred_skills", [])) or "None"
    min_exp = str(job_profile.get("minimum_experience") or "N/A")
    min_cgpa = str(job_profile.get("minimum_cgpa") or "N/A")
    req_degree = str(job_profile.get("degree") or "N/A")
    
    jd_data = [
        [Paragraph("<b>Job Title:</b>", normal_text), Paragraph(jd_title, normal_text),
         Paragraph("<b>Company:</b>", normal_text), Paragraph(company, normal_text)],
        [Paragraph("<b>Min Experience:</b>", normal_text), Paragraph(min_exp, normal_text),
         Paragraph("<b>Required Degree:</b>", normal_text), Paragraph(req_degree, normal_text)],
        [Paragraph("<b>Min CGPA:</b>", normal_text), Paragraph(min_cgpa, normal_text),
         Paragraph("", normal_text), Paragraph("", normal_text)],
        [Paragraph("<b>Required Skills:</b>", normal_text), Paragraph(req_skills, normal_text),
         Paragraph("", normal_text), Paragraph("", normal_text)],
        [Paragraph("<b>Preferred Skills:</b>", normal_text), Paragraph(pref_skills, normal_text),
         Paragraph("", normal_text), Paragraph("", normal_text)]
    ]
    
    jd_table = Table(jd_data, colWidths=[100, 170, 100, 170])
    jd_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('SPAN', (1,3), (3,3)),
        ('SPAN', (1,4), (3,4)),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(jd_table)
    story.append(Spacer(1, 20))
    
    # 3. Candidate Rankings Section
    story.append(Paragraph("🏆 Candidate Match Rankings", section_heading))
    
    rankings_header = [
        Paragraph("<b>Rank</b>", bold_text),
        Paragraph("<b>Candidate Name</b>", bold_text),
        Paragraph("<b>Match %</b>", bold_text),
        Paragraph("<b>Matched Skills</b>", bold_text),
        Paragraph("<b>Missing Skills</b>", bold_text)
    ]
    
    table_data = [rankings_header]
    
    for idx, c in enumerate(ranked_candidates):
        rank = str(idx + 1)
        name = c["name"]
        score = f"{c['score']}%"
        matched = ", ".join(c["matched_required"]) or "None"
        missing = ", ".join(c["missing_required"]) or "None"
        
        table_data.append([
            Paragraph(rank, normal_text),
            Paragraph(name, normal_text),
            Paragraph(score, bold_text),
            Paragraph(matched, normal_text),
            Paragraph(missing, normal_text)
        ])
        
    rankings_table = Table(table_data, colWidths=[40, 110, 50, 170, 170])
    rankings_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(rankings_table)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
