"""
Tag generation utilities for AtlasAI tag naming convention
"""

import re
import string
from typing import Dict, List, Optional, Any
from datetime import datetime


class TagNamingConvention:
    """Configurable tag naming convention for industrial equipment"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize tag naming convention with configuration
        
        Args:
            config: Configuration dictionary with naming rules
        """
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default naming convention configuration"""
        return {
            "format": "{area_code}-{equipment_type}-{sequence_number}",
            "area_codes": {
                "process": "P",
                "utility": "U", 
                "safety": "S",
                "control": "C",
                "electrical": "E",
                "mechanical": "M"
            },
            "equipment_types": {
                "pump": "P",
                "valve": "V",
                "tank": "T",
                "heat_exchanger": "HX",
                "compressor": "C",
                "sensor": "S",
                "transmitter": "T",
                "controller": "CTRL",
                "motor": "M",
                "fan": "F",
                "filter": "FL",
                "separator": "SEP",
                "reactor": "R",
                "column": "COL",
                "exchanger": "EX"
            },
            "sequence_length": 4,
            "max_tag_length": 20,
            "allowed_characters": string.ascii_uppercase + string.digits + "-",
            "reserved_prefixes": ["PI:", "AI:", "AO:", "DI:", "DO:"]
        }
    
    def validate_tag(self, tag: str) -> Dict[str, Any]:
        """
        Validate a tag against naming convention rules
        
        Args:
            tag: Tag to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check length
        if len(tag) > self.config["max_tag_length"]:
            result["valid"] = False
            result["errors"].append(f"Tag too long: {len(tag)} > {self.config['max_tag_length']}")
        
        # Check allowed characters
        invalid_chars = set(tag) - set(self.config["allowed_characters"])
        if invalid_chars:
            result["valid"] = False
            result["errors"].append(f"Invalid characters: {invalid_chars}")
        
        # Check for reserved prefixes
        for prefix in self.config["reserved_prefixes"]:
            if tag.upper().startswith(prefix):
                result["warnings"].append(f"Tag starts with reserved prefix: {prefix}")
        
        return result
    
    def generate_tag(self, area: str, equipment_type: str, sequence: int, 
                    custom_format: str = None) -> str:
        """
        Generate a tag number based on naming convention
        
        Args:
            area: Area code (e.g., 'process', 'utility')
            equipment_type: Type of equipment (e.g., 'pump', 'valve')
            sequence: Sequence number
            custom_format: Custom format string (optional)
            
        Returns:
            Generated tag number
        """
        format_str = custom_format or self.config["format"]
        
        # Get area code
        area_code = self.config["area_codes"].get(area.lower(), area.upper())
        
        # Get equipment type code
        eq_type_code = self.config["equipment_types"].get(equipment_type.lower(), equipment_type.upper())
        
        # Format sequence number
        seq_str = str(sequence).zfill(self.config["sequence_length"])
        
        # Generate tag
        tag = format_str.format(
            area_code=area_code,
            equipment_type=eq_type_code,
            sequence_number=seq_str
        )
        
        return tag.upper()


def generate_tag_numbers(client, equipment_list: List[Dict[str, Any]], 
                        naming_convention: TagNamingConvention = None) -> Dict[str, Any]:
    """
    Generate tag numbers for a list of equipment
    
    Args:
        client: Cognite client
        equipment_list: List of equipment dictionaries
        naming_convention: Tag naming convention instance
        
    Returns:
        Dictionary with generated tags and validation results
    """
    if naming_convention is None:
        naming_convention = TagNamingConvention()
    
    results = {
        "generated_tags": [],
        "validation_results": [],
        "errors": [],
        "summary": {
            "total_equipment": len(equipment_list),
            "successful_generations": 0,
            "validation_errors": 0
        }
    }
    
    # Get existing tags to check for duplicates
    existing_tags = set()
    try:
        # Query existing time series to get current tag numbers
        existing_ts = client.time_series.list(limit=1000)
        existing_tags.update([ts.external_id for ts in existing_ts if ts.external_id])
    except Exception as e:
        results["errors"].append(f"Could not retrieve existing tags: {str(e)}")
    
    sequence_counters = {}
    
    for equipment in equipment_list:
        try:
            area = equipment.get("area", "process")
            eq_type = equipment.get("equipment_type", "equipment")
            custom_format = equipment.get("custom_format")
            
            # Get or initialize sequence counter for this area-equipment combination
            key = f"{area}_{eq_type}"
            if key not in sequence_counters:
                sequence_counters[key] = 1
            else:
                sequence_counters[key] += 1
            
            # Generate tag
            tag = naming_convention.generate_tag(
                area=area,
                equipment_type=eq_type,
                sequence=sequence_counters[key],
                custom_format=custom_format
            )
            
            # Validate tag
            validation = naming_convention.validate_tag(tag)
            
            # Check for duplicates
            if tag in existing_tags:
                validation["valid"] = False
                validation["errors"].append("Tag already exists")
            
            # Add to results
            result_item = {
                "equipment": equipment,
                "generated_tag": tag,
                "validation": validation
            }
            
            results["generated_tags"].append(result_item)
            results["validation_results"].append(validation)
            
            if validation["valid"]:
                results["summary"]["successful_generations"] += 1
                existing_tags.add(tag)  # Add to existing tags to prevent duplicates
            else:
                results["summary"]["validation_errors"] += 1
                
        except Exception as e:
            error_msg = f"Error processing equipment {equipment}: {str(e)}"
            results["errors"].append(error_msg)
            results["summary"]["validation_errors"] += 1
    
    return results


def create_time_series_with_tag(client, tag: str, equipment_info: Dict[str, Any], 
                               data_set_id: int = None) -> bool:
    """
    Create a time series in CDF with the generated tag
    
    Args:
        client: Cognite client
        tag: Generated tag number
        equipment_info: Equipment information
        data_set_id: Dataset ID for the time series
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create time series
        ts_data = {
            "external_id": tag,
            "name": f"{tag} - {equipment_info.get('name', 'Equipment')}",
            "description": f"Time series for {equipment_info.get('description', 'equipment')}",
            "unit": equipment_info.get("unit", ""),
            "is_step": False,
            "is_string": False
        }
        
        if data_set_id:
            ts_data["data_set_id"] = data_set_id
        
        client.time_series.create([ts_data])
        return True
        
    except Exception as e:
        print(f"Error creating time series for tag {tag}: {str(e)}")
        return False


def get_naming_convention_templates() -> Dict[str, str]:
    """
    Get common naming convention templates
    
    Returns:
        Dictionary of template names and formats
    """
    return {
        "standard": "{area_code}-{equipment_type}-{sequence_number}",
        "detailed": "{area_code}-{equipment_type}-{location}-{sequence_number}",
        "simple": "{equipment_type}{sequence_number}",
        "hierarchical": "{plant}-{area_code}-{equipment_type}-{sequence_number}",
        "functional": "{function}-{equipment_type}-{sequence_number}"
    }

