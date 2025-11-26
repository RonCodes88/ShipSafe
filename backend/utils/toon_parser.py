"""TOON (Token-Oriented Object Notation) parser utilities."""

from typing import Dict, Any


def parse_toon(toon_string: str) -> Dict[str, Any]:
    """
    Parse TOON format string to dictionary.
    
    TOON format uses pipe (|) for field separation and colon (:) for key-value pairs.
    Example: "vuln:SQL_INJ|sev:HIGH|file:auth.py|ln:45-47|type:unsanitized_input"
    
    Args:
        toon_string: String in TOON format
        
    Returns:
        Dictionary representation of the TOON data
        
    Example:
        >>> parse_toon("vuln:SQL_INJ|sev:HIGH|file:auth.py")
        {'vuln': 'SQL_INJ', 'sev': 'HIGH', 'file': 'auth.py'}
    """
    if not toon_string or not isinstance(toon_string, str):
        return {}
    
    result = {}
    
    # Split by pipe delimiter
    fields = toon_string.split("|")
    
    for field in fields:
        field = field.strip()
        if not field:
            continue
        
        # Split by colon to get key-value pairs
        if ":" in field:
            key, value = field.split(":", 1)
            result[key.strip()] = value.strip()
    
    return result


def to_toon(data: Dict[str, Any]) -> str:
    """
    Convert dictionary to TOON format string.
    
    Args:
        data: Dictionary to convert
        
    Returns:
        String in TOON format
        
    Example:
        >>> to_toon({'vuln': 'SQL_INJ', 'sev': 'HIGH', 'file': 'auth.py'})
        'vuln:SQL_INJ|sev:HIGH|file:auth.py'
    """
    if not data or not isinstance(data, dict):
        return ""
    
    # Convert dict to TOON format
    fields = []
    for key, value in data.items():
        # Convert value to string
        value_str = str(value)
        fields.append(f"{key}:{value_str}")
    
    return "|".join(fields)


def parse_toon_array(toon_array: str) -> list[Dict[str, Any]]:
    """
    Parse an array of TOON strings (comma-separated).
    
    Args:
        toon_array: Comma-separated TOON strings
        
    Returns:
        List of dictionaries
        
    Example:
        >>> parse_toon_array("vuln:XSS|sev:HIGH,vuln:SQL_INJ|sev:CRIT")
        [{'vuln': 'XSS', 'sev': 'HIGH'}, {'vuln': 'SQL_INJ', 'sev': 'CRIT'}]
    """
    if not toon_array:
        return []
    
    # Split by comma and parse each TOON string
    toon_strings = toon_array.split(",")
    return [parse_toon(toon_str.strip()) for toon_str in toon_strings if toon_str.strip()]


def to_toon_array(data_list: list[Dict[str, Any]]) -> str:
    """
    Convert list of dictionaries to comma-separated TOON strings.
    
    Args:
        data_list: List of dictionaries
        
    Returns:
        Comma-separated TOON strings
        
    Example:
        >>> to_toon_array([{'vuln': 'XSS', 'sev': 'HIGH'}, {'vuln': 'SQL_INJ', 'sev': 'CRIT'}])
        'vuln:XSS|sev:HIGH,vuln:SQL_INJ|sev:CRIT'
    """
    if not data_list:
        return ""
    
    return ",".join([to_toon(item) for item in data_list])

