# AtlasAI Tag Number Generator

A Cognite Function for generating standardized tag numbers according to preset naming conventions for industrial equipment. This function can be used by AtlasAI to automatically create consistent tag numbers for new equipment or systems.

## Features

- **Configurable Naming Conventions**: Support for multiple tag naming templates
- **Equipment Type Support**: Predefined codes for common industrial equipment
- **Area-based Organization**: Support for different plant areas (process, utility, safety, etc.)
- **Validation**: Comprehensive validation of generated tag numbers
- **Duplicate Prevention**: Checks against existing tags in CDF
- **Time Series Creation**: Optional automatic creation of time series in CDF
- **Flexible Configuration**: Customizable naming rules and formats

## Tag Naming Convention

### Default Format
```
{area_code}-{equipment_type}-{sequence_number}
```

### Example Tags
- `P-P-0001` - Process Pump #1
- `U-V-0001` - Utility Valve #1
- `S-S-0001` - Safety Sensor #1
- `C-HX-0001` - Control Heat Exchanger #1

### Supported Equipment Types
- Pump (P)
- Valve (V)
- Tank (T)
- Heat Exchanger (HX)
- Compressor (C)
- Sensor (S)
- Transmitter (T)
- Controller (CTRL)
- Motor (M)
- Fan (F)
- Filter (FL)
- Separator (SEP)
- Reactor (R)
- Column (COL)
- Exchanger (EX)

### Supported Area Codes
- Process (P)
- Utility (U)
- Safety (S)
- Control (C)
- Electrical (E)
- Mechanical (M)

## Usage

### Input Data Format

```json
{
  "equipment_list": [
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
    }
  ],
  "naming_convention": {
    "format": "{area_code}-{equipment_type}-{sequence_number}",
    "sequence_length": 4
  },
  "create_time_series": true,
  "data_set_id": 123456789,
  "template": "standard"
}
```

### Available Templates

1. **standard**: `{area_code}-{equipment_type}-{sequence_number}`
2. **detailed**: `{area_code}-{equipment_type}-{location}-{sequence_number}`
3. **simple**: `{equipment_type}{sequence_number}`
4. **hierarchical**: `{plant}-{area_code}-{equipment_type}-{sequence_number}`
5. **functional**: `{function}-{equipment_type}-{sequence_number}`

### Response Format

```json
{
  "success": true,
  "message": "Generated 2 tag numbers",
  "results": {
    "generated_tags": [
      {
        "equipment": {
          "name": "Main Process Pump",
          "equipment_type": "pump",
          "area": "process"
        },
        "generated_tag": "P-P-0001",
        "validation": {
          "valid": true,
          "errors": [],
          "warnings": []
        }
      }
    ],
    "summary": {
      "total_equipment": 2,
      "successful_generations": 2,
      "validation_errors": 0
    }
  },
  "naming_convention_used": {
    "format": "{area_code}-{equipment_type}-{sequence_number}",
    "area_codes": {...},
    "equipment_types": {...}
  }
}
```

## Configuration Options

### Naming Convention Configuration

```json
{
  "format": "{area_code}-{equipment_type}-{sequence_number}",
  "area_codes": {
    "process": "P",
    "utility": "U",
    "safety": "S"
  },
  "equipment_types": {
    "pump": "P",
    "valve": "V",
    "sensor": "S"
  },
  "sequence_length": 4,
  "max_tag_length": 20,
  "allowed_characters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-",
  "reserved_prefixes": ["PI:", "AI:", "AO:", "DI:", "DO:"]
}
```

## Deployment

### As a Cognite Function

1. Deploy the function using the Cognite SDK or CDF UI
2. Configure the function with appropriate permissions
3. Call the function with equipment data

### Example Deployment Code

```python
from cognite.client import CogniteClient
from cognite.client.data_classes import Function

# Create function
function = Function(
    name="AtlasAI Tag Generator",
    external_id="atlasai-tag-generator",
    description="Generate tag numbers for industrial equipment",
    owner="your-email@company.com",
    file_id=file_id,  # Upload handler.py and tools.py
    function_path="handler.py",
    cpu=0.1,
    memory=128,
    timeout=30
)

client.functions.create(function)
```

## Validation Rules

The function validates generated tags against:

1. **Length**: Maximum tag length (default: 20 characters)
2. **Characters**: Only allowed characters (A-Z, 0-9, -)
3. **Reserved Prefixes**: Warns about reserved prefixes (PI:, AI:, etc.)
4. **Uniqueness**: Checks against existing tags in CDF
5. **Format**: Ensures tags follow the specified naming convention

## Error Handling

The function provides comprehensive error handling:

- Invalid input data validation
- Equipment list format validation
- Tag generation errors
- Time series creation failures
- CDF connection issues

## Integration with AtlasAI

This function can be integrated with AtlasAI workflows to:

1. Automatically generate tag numbers for new equipment
2. Maintain consistent naming conventions across the plant
3. Validate tag numbers before creation
4. Create corresponding time series in CDF
5. Support bulk equipment onboarding

## Customization

The function supports extensive customization:

- Custom naming formats
- Additional equipment types
- New area codes
- Custom validation rules
- Integration with external systems

## Requirements

- cognite-sdk>=6.0.0
- typing-extensions>=4.0.0

## License

This project is part of the learn-cognite-functions repository and follows the same license terms.

