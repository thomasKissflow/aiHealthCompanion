"""
Script to create sample medical knowledge PDFs for the AI Health Companion.

This creates simple text-based PDFs with medical information about:
1. Migraines and headaches
2. Common symptoms and their causes
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def create_migraine_pdf():
    """Create a PDF about migraines and headaches."""
    
    filename = "knowledge/migraines_and_headaches.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    body_style = styles['BodyText']
    
    story = []
    
    # Title
    story.append(Paragraph("Migraines and Headaches: A Medical Reference", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph("Introduction", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Headaches are one of the most common medical complaints. They can range from mild tension "
        "headaches to severe migraines that significantly impact daily life. Understanding the different "
        "types of headaches and their characteristics is important for proper management.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Types of Headaches
    story.append(Paragraph("Types of Headaches", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Tension Headaches", heading_style))
    story.append(Paragraph(
        "Tension headaches are the most common type of headache. They typically cause a dull, aching "
        "sensation on both sides of the head. People often describe it as feeling like a tight band "
        "around their head. These headaches are usually caused by stress, poor posture, or muscle tension "
        "in the neck and shoulders.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Migraines", heading_style))
    story.append(Paragraph(
        "Migraines are a neurological condition characterized by intense, throbbing pain, usually on one "
        "side of the head. They can last from 4 to 72 hours and are often accompanied by other symptoms. "
        "Migraines affect approximately 12% of the population and are three times more common in women "
        "than men.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Migraine Symptoms
    story.append(Paragraph("Common Migraine Symptoms", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Migraine symptoms can include: intense throbbing or pulsing pain, usually on one side of the head; "
        "nausea and vomiting; sensitivity to light (photophobia) and sound (phonophobia); visual disturbances "
        "known as aura, which may include seeing flashing lights, zigzag lines, or temporary vision loss; "
        "dizziness or vertigo; and difficulty concentrating.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Triggers
    story.append(Paragraph("Common Migraine Triggers", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Migraine triggers vary from person to person but commonly include: stress and anxiety; hormonal "
        "changes, particularly in women; certain foods and drinks such as aged cheese, processed meats, "
        "alcohol, and caffeine; sleep disturbances, either too much or too little sleep; weather changes "
        "and barometric pressure fluctuations; strong sensory stimuli like bright lights or strong smells; "
        "and dehydration.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # When to Seek Help
    story.append(Paragraph("When to Seek Medical Attention", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "While most headaches are not serious, certain symptoms warrant immediate medical attention. "
        "Seek emergency care if you experience: a sudden, severe headache unlike any you've had before; "
        "headache accompanied by fever, stiff neck, confusion, vision changes, difficulty speaking, or "
        "numbness; headache after a head injury; or a chronic headache that worsens after coughing, "
        "exertion, or sudden movement.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Management
    story.append(Paragraph("Managing Headaches and Migraines", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Management strategies include: identifying and avoiding triggers; maintaining regular sleep "
        "patterns; staying hydrated; managing stress through relaxation techniques; regular exercise; "
        "and keeping a headache diary to track patterns. For frequent or severe headaches, consult a "
        "healthcare provider who can recommend appropriate treatment options.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print(f"Created {filename}")


def create_common_symptoms_pdf():
    """Create a PDF about common symptoms and their causes."""
    
    filename = "knowledge/common_symptoms_guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    body_style = styles['BodyText']
    
    story = []
    
    # Title
    story.append(Paragraph("Common Symptoms: A Medical Reference Guide", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph("Introduction", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "This guide provides information about common symptoms and their potential causes. It is intended "
        "for educational purposes only and should not replace professional medical advice. Always consult "
        "a healthcare provider for proper diagnosis and treatment.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Nausea
    story.append(Paragraph("Nausea and Vomiting", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Nausea is an uncomfortable sensation in the stomach that may lead to vomiting. Common causes "
        "include: viral gastroenteritis (stomach flu); food poisoning; motion sickness; pregnancy "
        "(morning sickness); migraines; medication side effects; anxiety and stress; and digestive "
        "disorders. Nausea accompanied by severe headache may indicate a migraine. If nausea persists "
        "for more than 24 hours or is accompanied by severe abdominal pain, seek medical attention.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Dizziness
    story.append(Paragraph("Dizziness and Vertigo", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Dizziness is a term used to describe sensations of lightheadedness, unsteadiness, or vertigo "
        "(a spinning sensation). Common causes include: inner ear problems; dehydration; low blood sugar; "
        "low blood pressure; anxiety; migraines; and certain medications. Sudden severe dizziness with "
        "other symptoms like chest pain or difficulty breathing requires immediate medical attention.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Fatigue
    story.append(Paragraph("Fatigue and Tiredness", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Fatigue is a feeling of tiredness, exhaustion, or lack of energy. It differs from drowsiness, "
        "where you feel you need to sleep. Common causes include: insufficient sleep; stress and anxiety; "
        "depression; poor nutrition; dehydration; anemia; thyroid problems; chronic conditions like "
        "diabetes or heart disease; and certain medications. Persistent fatigue lasting more than two "
        "weeks should be evaluated by a healthcare provider.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Fever
    story.append(Paragraph("Fever", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "A fever is a temporary increase in body temperature, often due to an illness. Normal body "
        "temperature is around 98.6°F (37°C), and a fever is generally considered to be 100.4°F (38°C) "
        "or higher. Common causes include: viral infections like colds and flu; bacterial infections; "
        "heat exhaustion; inflammatory conditions; and reactions to medications or vaccines. Seek medical "
        "attention for fevers above 103°F (39.4°C), fevers lasting more than three days, or fevers "
        "accompanied by severe symptoms.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Cough
    story.append(Paragraph("Cough", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "A cough is a reflex action that clears the airways of irritants and secretions. Coughs can be "
        "acute (lasting less than three weeks) or chronic (lasting more than eight weeks). Common causes "
        "include: viral infections like the common cold or flu; allergies; asthma; acid reflux; "
        "postnasal drip; and environmental irritants. A persistent cough, cough with blood, or cough "
        "with difficulty breathing requires medical evaluation.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Chest Pain
    story.append(Paragraph("Chest Pain", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Chest pain can have many causes, ranging from minor to life-threatening. While not all chest "
        "pain indicates a heart problem, it should always be taken seriously. Causes include: heart-related "
        "issues such as angina or heart attack; digestive problems like acid reflux or heartburn; muscle "
        "strain; anxiety and panic attacks; and lung conditions. Chest pain accompanied by shortness of "
        "breath, sweating, nausea, or pain radiating to the arm or jaw requires immediate emergency care.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Breathing Difficulty
    story.append(Paragraph("Difficulty Breathing", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Difficulty breathing (dyspnea) is the sensation of not getting enough air. It can range from "
        "mild breathlessness to severe respiratory distress. Common causes include: asthma; chronic "
        "obstructive pulmonary disease (COPD); anxiety and panic attacks; heart conditions; pneumonia; "
        "and allergic reactions. Sudden severe difficulty breathing, especially with chest pain, is a "
        "medical emergency requiring immediate attention.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    story.append(Paragraph("Important Reminders", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "This guide provides general information about common symptoms. Individual experiences may vary, "
        "and symptoms can have multiple causes. Always consult with a healthcare professional for proper "
        "diagnosis and treatment. Trust your instincts - if something feels seriously wrong, seek medical "
        "attention promptly.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print(f"Created {filename}")


if __name__ == "__main__":
    print("Creating sample medical knowledge PDFs...")
    create_migraine_pdf()
    create_common_symptoms_pdf()
    print("Done!")
