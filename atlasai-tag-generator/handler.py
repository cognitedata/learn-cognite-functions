"""
AtlasAI Tag Number Generator Handler Function

This handler function generates tag numbers according to preset naming conventions
for industrial equipment. It can be used by AtlasAI to automatically create
standardized tag numbers for new equipment or systems.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from tools import TagNamingConvention, generate_tag_numbers, create_time_series_with_tag, get_naming_convention_templates


def handle(client, data=None, secrets=None, function_call_info=None):
    """
    Handler Function for AtlasAI Tag Number Generation
    
    Args:
        client: Cognite Client (available when deployed)
        data: Configuration and equipment data needed by function
        secrets: Any secrets the function needs
        function_call_info: Additional information about the function call
        
    Returns:
        response: JSON response with generated tags and validation results
    """
    
    try:
        # Default configuration if no data provided
        if data is None:
            data = {}
        
        # Extract configuration from data
        equipment_list = data.get("equipment_list", [])
        naming_config = data.get("naming_convention", {})
        create_time_series = data.get("create_time_series", False)
        data_set_id = data.get("data_set_id")
        template_name = data.get("template", "standard")
        
        # Validate input
        if not equipment_list:
            return {
                "success": False,
                "error": "No equipment list provided",
                "message": "Please provide a list of equipment in the 'equipment_list' field"
            }
        
        # Get naming convention template if specified
        templates = get_naming_convention_templates()
        if template_name in templates:
            naming_config["format"] = templates[template_name]
        
        # Initialize naming convention
        naming_convention = TagNamingConvention(naming_config)
        
        # Generate tag numbers
        results = generate_tag_numbers(client, equipment_list, naming_convention)
        
        # Create time series if requested
        if create_time_series and results["summary"]["successful_generations"] > 0:
            created_ts = []
            failed_ts = []
            
            for item in results["generated_tags"]:
                if item["validation"]["valid"]:
                    success = create_time_series_with_tag(
                        client, 
                        item["generated_tag"], 
                        item["equipment"],
                        data_set_id
                    )
                    if success:
                        created_ts.append(item["generated_tag"])
                    else:
                        failed_ts.append(item["generated_tag"])
            
            results["time_series_creation"] = {
                "created": created_ts,
                "failed": failed_ts,
                "total_created": len(created_ts),
                "total_failed": len(failed_ts)
            }
        
        # Prepare response
        response = {
            "success": True,
            "message": f"Generated {results['summary']['successful_generations']} tag numbers",
            "results": results,
            "naming_convention_used": naming_convention.config,
            "timestamp": str(datetime.now())
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": "An error occurred while generating tag numbers"
        }
        return json.dumps(error_response, indent=2)


def validate_equipment_list(equipment_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate equipment list input
    
    Args:
        equipment_list: List of equipment dictionaries
        
    Returns:
        Validation results
    """
    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not isinstance(equipment_list, list):
        validation["valid"] = False
        validation["errors"].append("Equipment list must be a list")
        return validation
    
    required_fields = ["equipment_type"]
    optional_fields = ["area", "name", "description", "unit", "custom_format"]
    
    for i, equipment in enumerate(equipment_list):
        if not isinstance(equipment, dict):
            validation["valid"] = False
            validation["errors"].append(f"Equipment item {i} must be a dictionary")
            continue
        
        # Check required fields
        for field in required_fields:
            if field not in equipment:
                validation["valid"] = False
                validation["errors"].append(f"Equipment item {i} missing required field: {field}")
        
        # Check for unknown fields
        all_fields = required_fields + optional_fields
        unknown_fields = set(equipment.keys()) - set(all_fields)
        if unknown_fields:
            validation["warnings"].append(f"Equipment item {i} has unknown fields: {unknown_fields}")
    
    return validation


def get_equipment_types() -> List[str]:
    """
    Get list of supported equipment types
    
    Returns:
        List of equipment type names
    """
    convention = TagNamingConvention()
    return list(convention.config["equipment_types"].keys())


def get_area_codes() -> List[str]:
    """
    Get list of supported area codes
    
    Returns:
        List of area code names
    """
    convention = TagNamingConvention()
    return list(convention.config["area_codes"].keys())


# Example usage and testing
if __name__ == "__main__":
    # Example equipment list
    example_equipment = [
        {
            "name": "Main Process Pump",
            "equipment_type": "pump",
            "area": "process",
            "description": "Primary process pump for main line",
            "unit": "m³/h"
        },
        {
            "name": "Control Valve",
            "equipment_type": "valve", 
            "area": "control",
            "description": "Flow control valve",
            "unit": "%"
        },
        {
            "name": "Temperature Sensor",
            "equipment_type": "sensor",
            "area": "process",
            "description": "Process temperature measurement",
            "unit": "°C"
        }
    ]
    
    print("Example equipment list:")
    print(json.dumps(example_equipment, indent=2))
    
    print("\nSupported equipment types:")
    print(get_equipment_types())
    
    print("\nSupported area codes:")
    print(get_area_codes())
    
    print("\nAvailable templates:")
    templates = get_naming_convention_templates()
    for name, template in templates.items():
        print(f"{name}: {template}")
