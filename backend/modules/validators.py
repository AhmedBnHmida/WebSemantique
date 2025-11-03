"""Validation utilities for education domain entities"""

import re
from datetime import datetime
from typing import Dict, List, Optional

def validate_required(value: any, field_name: str) -> Optional[str]:
    """Validate that a required field is not empty"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return f"{field_name} est requis"
    return None

def validate_string_length(value: str, field_name: str, min_len: int = 1, max_len: int = 500) -> Optional[str]:
    """Validate string length"""
    if not isinstance(value, str):
        return f"{field_name} doit être une chaîne de caractères"
    if len(value) < min_len:
        return f"{field_name} doit contenir au moins {min_len} caractère(s)"
    if len(value) > max_len:
        return f"{field_name} ne peut pas dépasser {max_len} caractères"
    return None

def validate_email(email: str) -> Optional[str]:
    """Validate email format"""
    if not email:
        return None  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "Format d'email invalide"
    return None

def validate_integer(value: any, field_name: str, min_val: int = None, max_val: int = None) -> Optional[str]:
    """Validate integer value"""
    if value is None:
        return None  # Optional field
    try:
        int_value = int(value)
        if min_val is not None and int_value < min_val:
            return f"{field_name} doit être supérieur ou égal à {min_val}"
        if max_val is not None and int_value > max_val:
            return f"{field_name} doit être inférieur ou égal à {max_val}"
    except (ValueError, TypeError):
        return f"{field_name} doit être un nombre entier"
    return None

def validate_float(value: any, field_name: str, min_val: float = None, max_val: float = None) -> Optional[str]:
    """Validate float value"""
    if value is None:
        return None  # Optional field
    try:
        float_value = float(value)
        if min_val is not None and float_value < min_val:
            return f"{field_name} doit être supérieur ou égal à {min_val}"
        if max_val is not None and float_value > max_val:
            return f"{field_name} doit être inférieur ou égal à {max_val}"
    except (ValueError, TypeError):
        return f"{field_name} doit être un nombre"
    return None

def validate_date(date_str: str, field_name: str) -> Optional[str]:
    """Validate date format (YYYY-MM-DD)"""
    if not date_str:
        return None  # Optional field
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return f"{field_name} doit être au format YYYY-MM-DD"
    return None

def validate_code(code: str, field_name: str) -> Optional[str]:
    """Validate code format (alphanumeric, uppercase)"""
    if not code:
        return None
    if not re.match(r'^[A-Z0-9]+$', code):
        return f"{field_name} doit contenir uniquement des lettres majuscules et des chiffres"
    return None

def validate_cours(data: Dict) -> Dict[str, str]:
    """Validate Cours entity"""
    errors = {}
    
    # Required fields
    if error := validate_required(data.get('intitule'), 'Intitule'):
        errors['intitule'] = error
    
    if error := validate_required(data.get('codeCours'), 'Code cours'):
        errors['codeCours'] = error
    elif data.get('codeCours'):
        if error := validate_code(data.get('codeCours'), 'Code cours'):
            errors['codeCours'] = error
    
    # Optional fields with validation
    if data.get('creditsECTS'):
        if error := validate_integer(data.get('creditsECTS'), 'Credits ECTS', 0, 30):
            errors['creditsECTS'] = error
    
    if data.get('volumeHoraire'):
        if error := validate_integer(data.get('volumeHoraire'), 'Volume horaire', 0):
            errors['volumeHoraire'] = error
    
    if data.get('intitule'):
        if error := validate_string_length(data.get('intitule'), 'Intitule', 1, 200):
            errors['intitule'] = error
    
    return errors

def validate_competence(data: Dict) -> Dict[str, str]:
    """Validate Competence entity"""
    errors = {}
    
    if error := validate_required(data.get('nomCompetence'), 'Nom compétence'):
        errors['nomCompetence'] = error
    
    if data.get('nomCompetence'):
        if error := validate_string_length(data.get('nomCompetence'), 'Nom compétence', 1, 200):
            errors['nomCompetence'] = error
    
    if data.get('descriptionCompetence'):
        if error := validate_string_length(data.get('descriptionCompetence'), 'Description', 1, 1000):
            errors['descriptionCompetence'] = error
    
    return errors

def validate_projet(data: Dict) -> Dict[str, str]:
    """Validate ProjetAcademique entity"""
    errors = {}
    
    if error := validate_required(data.get('titreProjet'), 'Titre projet'):
        errors['titreProjet'] = error
    
    if data.get('titreProjet'):
        if error := validate_string_length(data.get('titreProjet'), 'Titre projet', 1, 300):
            errors['titreProjet'] = error
    
    if data.get('noteProjet'):
        if error := validate_float(data.get('noteProjet'), 'Note projet', 0.0, 20.0):
            errors['noteProjet'] = error
    
    return errors

def validate_ressource(data: Dict) -> Dict[str, str]:
    """Validate RessourcePedagogique entity"""
    errors = {}
    
    if error := validate_required(data.get('titreRessource'), 'Titre ressource'):
        errors['titreRessource'] = error
    
    if data.get('titreRessource'):
        if error := validate_string_length(data.get('titreRessource'), 'Titre ressource', 1, 300):
            errors['titreRessource'] = error
    
    return errors

def validate_technologie(data: Dict) -> Dict[str, str]:
    """Validate TechnologieEducative entity"""
    errors = {}
    
    if error := validate_required(data.get('nomTechnologie'), 'Nom technologie'):
        errors['nomTechnologie'] = error
    
    if data.get('nomTechnologie'):
        if error := validate_string_length(data.get('nomTechnologie'), 'Nom technologie', 1, 200):
            errors['nomTechnologie'] = error
    
    return errors

def validate_evaluation(data: Dict) -> Dict[str, str]:
    """Validate Evaluation entity"""
    errors = {}
    
    if error := validate_required(data.get('typeEvaluation'), 'Type évaluation'):
        errors['typeEvaluation'] = error
    
    if data.get('dateEvaluation'):
        if error := validate_date(data.get('dateEvaluation'), 'Date évaluation'):
            errors['dateEvaluation'] = error
    
    return errors

def validate_orientation(data: Dict) -> Dict[str, str]:
    """Validate OrientationAcademique entity"""
    errors = {}
    
    if error := validate_required(data.get('objectifOrientation'), 'Objectif orientation'):
        errors['objectifOrientation'] = error
    
    if data.get('objectifOrientation'):
        if error := validate_string_length(data.get('objectifOrientation'), 'Objectif orientation', 1, 500):
            errors['objectifOrientation'] = error
    
    if data.get('dateOrientation'):
        if error := validate_date(data.get('dateOrientation'), 'Date orientation'):
            errors['dateOrientation'] = error
    
    return errors

def validate_personne(data: Dict) -> Dict[str, str]:
    """Validate Personne entity"""
    errors = {}
    
    if error := validate_required(data.get('nom'), 'Nom'):
        errors['nom'] = error
    
    if error := validate_required(data.get('prenom'), 'Prénom'):
        errors['prenom'] = error
    
    if data.get('email'):
        if error := validate_email(data.get('email')):
            errors['email'] = error
    
    return errors

def validate_specialite(data: Dict) -> Dict[str, str]:
    """Validate Specialite entity"""
    errors = {}
    
    if error := validate_required(data.get('nomSpecialite'), 'Nom spécialité'):
        errors['nomSpecialite'] = error
    
    return errors

def validate_universite(data: Dict) -> Dict[str, str]:
    """Validate Universite entity"""
    errors = {}
    
    if error := validate_required(data.get('nomUniversite'), 'Nom université'):
        errors['nomUniversite'] = error
    
    return errors

