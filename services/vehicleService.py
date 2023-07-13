import re

def verificarPatente(patente):
    formato1 = r'^[A-Z]{3}\s\d{3}$'
    formato2 = r'^[A-Z]{2}\s\d{3}\s?[A-Z]{2}$'
    
    if re.match(formato1, patente) or re.match(formato2, patente):
        return True
    else:
        return False