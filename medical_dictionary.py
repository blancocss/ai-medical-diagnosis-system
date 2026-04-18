"""
Medical Knowledge Base
----------------------

This file contains:

1) Disease translation
2) Disease description
3) Medical advice
4) Risk level
5) Symptoms list
6) Recommendations
7) Severity classification

Used by:
medical_gui.py
"""

# =========================
# Disease Translation
# =========================

disease_translation = {

    "Flu": "إنفلونزا",
    "Common Cold": "نزلة برد",
    "Migraine": "صداع نصفي",
    "Hypertension": "ارتفاع ضغط الدم",
    "Diabetes": "داء السكري",
    "Asthma": "الربو",
    "Bronchitis": "التهاب الشعب الهوائية",
    "Pneumonia": "التهاب الرئة",
    "Heart attack": "نوبة قلبية",
    "Gastroenteritis": "التهاب المعدة والأمعاء",
    "Malaria": "الملاريا",
    "Tuberculosis": "السل",
    "Chicken pox": "جدري الماء",
    "Typhoid": "حمى التيفوئيد",
    "Hepatitis": "التهاب الكبد",
    "Arthritis": "التهاب المفاصل",
    "Anemia": "فقر الدم",
    "Depression": "الاكتئاب",
    "Anxiety": "القلق",
    "Kidney stones": "حصى الكلى",
    "Appendicitis": "التهاب الزائدة الدودية",
    "Food poisoning": "تسمم غذائي",
    "Sinusitis": "التهاب الجيوب الأنفية"

}

# =========================
# Disease Description
# =========================

disease_description = {

    "Flu":
        "عدوى فيروسية تصيب الجهاز التنفسي وتسبب الحمى والسعال.",

    "Common Cold":
        "مرض فيروسي خفيف يسبب سيلان الأنف والعطاس.",

    "Migraine":
        "صداع شديد متكرر يصاحبه حساسية للضوء.",

    "Hypertension":
        "ارتفاع ضغط الدم فوق المعدل الطبيعي.",

    "Diabetes":
        "مرض مزمن يسبب ارتفاع مستوى السكر في الدم.",

    "Asthma":
        "مرض تنفسي يسبب ضيق في الشعب الهوائية.",

    "Bronchitis":
        "التهاب في الشعب الهوائية يسبب السعال.",

    "Pneumonia":
        "التهاب في الرئتين بسبب عدوى.",

    "Heart attack":
        "انقطاع تدفق الدم إلى القلب.",

    "Food poisoning":
        "مرض ناتج عن تناول طعام ملوث."

}

# =========================
# Medical Advice
# =========================

medical_advice = {

    "Flu":
        "الراحة وشرب السوائل وتناول خافض حرارة.",

    "Common Cold":
        "اشرب سوائل دافئة وخذ قسطًا من الراحة.",

    "Migraine":
        "تجنب الضوء والضوضاء وخذ مسكنًا.",

    "Hypertension":
        "قلل من الملح وراقب ضغط الدم.",

    "Diabetes":
        "راقب مستوى السكر واتبع نظام غذائي.",

    "Asthma":
        "استخدم البخاخ وتجنب الغبار.",

    "Bronchitis":
        "اشرب سوائل دافئة وتجنب التدخين.",

    "Pneumonia":
        "راجع الطبيب فورًا.",

    "Heart attack":
        "اطلب المساعدة الطبية فورًا.",

    "Food poisoning":
        "اشرب سوائل وتجنب الطعام الملوث."

}

# =========================
# Symptoms Per Disease
# =========================

disease_symptoms = {

    "Flu": [
        "fever",
        "cough",
        "headache",
        "fatigue"
    ],

    "Common Cold": [
        "sneezing",
        "runny_nose",
        "cough"
    ],

    "Migraine": [
        "headache",
        "nausea",
        "sensitivity_to_light"
    ],

    "Hypertension": [
        "headache",
        "dizziness"
    ],

    "Diabetes": [
        "fatigue",
        "frequent_urination",
        "weight_loss"
    ]

}

# =========================
# Risk Level
# =========================

risk_level_info = {

    "Flu": "متوسط",
    "Common Cold": "منخفض",
    "Migraine": "متوسط",
    "Hypertension": "متوسط",
    "Diabetes": "متوسط",
    "Asthma": "متوسط",
    "Bronchitis": "متوسط",
    "Pneumonia": "مرتفع",
    "Heart attack": "مرتفع",
    "Food poisoning": "متوسط"

}

# =========================
# Severity Score
# =========================

severity_score = {

    "Flu": 5,
    "Common Cold": 2,
    "Migraine": 6,
    "Hypertension": 7,
    "Diabetes": 7,
    "Asthma": 6,
    "Bronchitis": 6,
    "Pneumonia": 9,
    "Heart attack": 10,
    "Food poisoning": 5

}

# =========================
# Recommendations
# =========================

general_recommendation = {

    "Low":
        "يمكن العلاج في المنزل.",

    "Medium":
        "يفضل مراجعة الطبيب.",

    "High":
        "اذهب إلى الطوارئ فورًا."

}