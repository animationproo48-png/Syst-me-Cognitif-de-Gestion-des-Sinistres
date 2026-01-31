"""
Dictionnaire de traduction Darija → Français
Pour le contexte marocain (villes, termes d'assurance, etc.)
"""

# Villes et régions marocaines
MOROCCAN_CITIES = {
    # Grands centres
    "دار البيضاء": "Casablanca",
    "الدار البيضاء": "Casablanca",
    "الرباط": "Rabat",
    "فاس": "Fès",
    "مراكش": "Marrakech",
    "تطوان": "Tétouan",
    "طنجة": "Tanger",
    "أكادير": "Agadir",
    "سلا": "Salé",
    "الجديدة": "El Jadida",
    "مكناس": "Meknès",
    "قنيطرة": "Kénitra",
    "سلوان": "Sefrou",
    "اصيلة": "Asilah",
    "شفشاون": "Chefchaouen",
    "الحسيمة": "Al Hoceima",
    "خريبكة": "Khénifra",
    "بني ملال": "Béni Mellal",
    "قلعة السراغنة": "Kasbah Tadla",
    "الصويرة": "Essaouira",
    "ورزازات": "Ouarzazate",
    "زاكورة": "Zagora",
    "تيزنيت": "Tiznit",
    "سيدي إفني": "Sidi Ifni",
    
    # Variantes Darija
    "دارالبيضا": "Casablanca",
    "دار البيضا": "Casablanca",
    "كاسا": "Casablanca",
    "طنجة": "Tanger",
    "طنج": "Tanger",
}

# Termes d'assurance automobile
INSURANCE_TERMS = {
    # Véhicule
    "الموتور": "moteur",
    "السيارة": "voiture",
    "المركبة": "véhicule",
    "الكسيدة": "voiture",
    "الطوموبيل": "automobile",
    "الباربريز": "pare-chocs",
    "الزجاج": "vitre",
    "الباب": "porte",
    "العجلة": "roue",
    "الشاسيه": "châssis",
    "الإطار": "pneu",
    "المرآة": "miroir",
    "الصبغة": "peinture",
    "الهيكل": "carrosserie",
    "مصباح": "phare",
    "الفرامل": "freins",
    
    # Sinistre
    "الكسيدة": "sinistre",
    "الحادثة": "accident",
    "الاصطدام": "collision",
    "التصادم": "choc",
    "الضرر": "dégâts",
    "الأضرار": "dommages",
    "الحريق": "incendie",
    "الغمر": "inondation",
    "السرقة": "vol",
    "الكسر": "bris",
    "الخدش": "rayure",
    
    # Actions
    "جرح": "blessure",
    "مات": "mort",
    "أصيب": "blessé",
    "انقلب": "renversé",
    "انزلق": "dérapé",
    "اصطدم": "heurté",
    "اخترق": "percuté",
    
    # Participants
    "الطرف الآخر": "tiers",
    "الشاهد": "témoin",
    "الشرطة": "police",
    "الإسعاف": "ambulance",
    
    # Temps
    "الصباح": "matin",
    "المساء": "soir",
    "الليل": "nuit",
    "الأمس": "hier",
    "اليوم": "aujourd'hui",
    "غدا": "demain",
    "الآن": "maintenant",
}

# Mots courants du Darija
DARIJA_COMMON = {
    "واحد": "un",
    "وحدة": "une",
    "بزاف": "beaucoup",
    "شوية": "un peu",
    "كاين": "il y a",
    "ماكاينش": "pas",
    "خاص": "il faut",
    "واخا": "d'accord",
    "صافي": "c'est bon",
    "الله يخليك": "s'il te plaît",
    "شنو": "quoi",
    "فين": "où",
    "علاش": "pourquoi",
    "أشنو": "quel",
    "دابا": "maintenant",
    "بادي": "début",
    "سميت": "entendu",
}

# Nombres en darija
NUMBERS_DARIJA = {
    "واحد": "1",
    "جوج": "2",
    "ثلاثة": "3",
    "أربع": "4",
    "خمسة": "5",
    "ستة": "6",
    "سبع": "7",
    "ثمانية": "8",
    "تسعة": "9",
    "عشرة": "10",
}

# Tous les dictionnaires combinés
ALL_TRANSLATIONS = {
    **MOROCCAN_CITIES,
    **INSURANCE_TERMS,
    **DARIJA_COMMON,
}

def apply_dictionary_translation(text: str) -> str:
    """
    Applique le dictionnaire de traduction au texte.
    Remplace les termes Darija connus par leurs équivalents français.
    
    Args:
        text: Texte contenant du Darija
        
    Returns:
        Texte avec remplacements appliqués
    """
    result = text
    
    # Appliquer les remplacements (du plus spécifique au plus générique)
    for darija, french in sorted(ALL_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        # Remplacer en respectant la casse mais de manière intelligente
        import re
        result = re.sub(
            rf'\b{re.escape(darija)}\b',
            french,
            result,
            flags=re.IGNORECASE
        )
    
    return result

def get_translation_context() -> str:
    """Retourne le contexte du dictionnaire pour le prompt Groq."""
    context = "DICTIONNAIRE DE CONTEXTE MAROCAIN :\n"
    context += "\nVilles marocaines:\n"
    for k, v in list(MOROCCAN_CITIES.items())[:10]:
        context += f"- {k} = {v}\n"
    context += "\nTermes d'assurance automobile:\n"
    for k, v in list(INSURANCE_TERMS.items())[:10]:
        context += f"- {k} = {v}\n"
    return context
