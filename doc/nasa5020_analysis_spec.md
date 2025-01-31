# NASA 5020 Analysis Module Technical Specification
Version 1.0

## 1. Problem Statement

### 1.1 Background
ScrewPy currently provides data structures and utilities for representing bolted joints but lacks analysis capabilities. This specification describes the addition of analysis functionality based on NASA-STD-5020 and NASA TM 106943.

Task at hand:
- create ability represent loading conditions
- create ability to analyze joint safety margins
- create ability to validate joint designs against NASA standards

### 1.2 Design Principles
0. "LLM - implementable"
1. KISS: Keep solutions simple and focused
2. YAGNI: Only implement proven necessary features
3. SOLID: Design modular, maintainable components
4. flat: All program files shall be in a single directory
5. Separation of concerns: Keep data structures (existing) separate from analysis (new)
6. Unit safety: All numerical values must include units via Pint

## 2. Technical Requirements

### 2.1 Input Requirements

#### Environment Class
```python
class Environment:
    """Represents physical conditions for analysis"""
    tension: Quantity      # Axial load along fastener
    shear: Quantity       # Shear load perpendicular to fastener
    bending: Quantity     # Bending moment on fastener
    min_temp: Quantity      # Min environmental temperature
    nom_temp: Quantity    # Nominal assembly temperature
    max_temp: Quantity    # Max environmental temperature
    preload_torque: Quantity  # Installation torque

    @classmethod
    def set_force_from_6dof(cls, forces: List[Quantity], moments: List[Quantity], 
                  fastener_axis: str = 'x') -> 'Environment':
        """Create tension, shear, and bending from 6DOF loads"""

    def validate(self):
        """Validate inputs:
        - Temperature > absolute zero
        - Positive preload torque
        - Valid units for all quantities"""
```

#### Analysis Configuration
```python
analysis_config = {
    'unit_system': str,  # 'metric' or 'imperial'
    'friction_coefficient': float,  # Default 0.2 uncoated, 0.1 coated
    'safety_factors': {
        'ultimate': float,
        'yield': float,
        'separation': float
    },
    'fitting_factor': float
}
```

Required inputs for analysis:
- Valid Junction object (existing)
- Environment object
- Configuration dictionary
- All numerical values must include units using Pint

### 2.2 Output Format
All outputs will be Pint Quantity objects with appropriate units:
- Joint stiffness values
- Preload values (min, max, nominal)
- Margins of safety for each failure mode

## 3. System Architecture

### 3.1 Core Components
```
analysis/
    nasa5020.py      # NASA 5020 implementation
environments/
    environment.py   # Environment class definition
```

### 3.2 Component Specifications

#### 3.2.1 NASA 5020 Analysis
```python
class NASA5020Analysis:
    """Implements NASA-STD-5020 analysis methods"""
    
    def __init__(self, junction: Junction, environment: Environment, **kwargs):
        """Initialize with junction and environment"""
    
    def calculate_preloads(self) -> Dict[str, Quantity]:
        """Calculate min/max preloads per section 6.1
        Implements equations 6-2 through 6-5"""
    
    def calculate_joint_stiffness(self) -> Tuple[Quantity, Quantity]:
        """Calculate bolt and joint stiffness
        Returns (k_b, k_c) per equation 6-8"""
    
    def calculate_ultimate_margins(self) -> Dict[str, float]:
        """Calculate ultimate strength margins
        - Tension (6.2.1)
        - Shear (6.2.2)
        - Combined loading (6.2.3)
        Returns margins for each failure mode"""
    
    def calculate_yield_margins(self) -> Dict[str, float]:
        """Calculate yield strength margins per section 6.3
        Returns margins for applicable cases"""
    
    def calculate_slip_margin(self) -> float:
        """Calculate joint slip margin per section 6.4"""
    
    def calculate_separation_margin(self) -> float:
        """Calculate separation margin per section 6.5"""
```

## 4. Performance Requirements
None specified for initial implementation.

## 5. Monitoring and Logging
None specified for initial implementation.

## 6. Testing Requirements

### 6.1 Core Testing
- Unit tests for all public methods
- Test cases must include:
  - Valid/invalid input validation
  - Unit conversion scenarios
  - Basic calculation verification against NASA 5020 examples
  - Edge cases for temperature and load limits
  - Preload calculations with temperature effects
  - All margin calculations
  - Combined loading scenarios

## 7. Security Requirements
None specified for initial implementation.

## 8. Development Guidelines

### 8.1 Code Quality
- Type hints required
- Documentation strings required
- Maintain separation between data and analysis concerns. We're working on analysis, data is done.
- All equations must reference NASA 5020 equation numbers in docstring

### 8.2 Documentation
- Clear docstrings explaining calculations
- References to NASA-STD-5020 sections
- Validation criteria for all inputs
- Units specified for all quantities

## 9. Future Considerations
Features intentionally deferred:
1. Additional failure modes beyond tension/shear
2. Multiple load case handling
3. Results formatting and reporting
4. Dynamic analysis
5. Configuration object (using kwargs instead)
6. Result object hierarchy
7. Thread pull-out analysis for inserts
8. Fatigue analysis
9. Thermal compensation methods (like SAE AIR 1754A)

## 10. Definition of Done
Project is complete when:
1. Environment class properly validates inputs
2. NASA5020Analysis implements all specified equations
3. All margin calculations match NASA 5020 requirements
4. Temperature effects on preload are properly handled
5. Combined loading analysis is implemented
6. Test suite passes
7. A full system demonstration

## 11. Special Instructions
- Maintain strict unit safety throughout
- Follow existing project patterns for validation
- Keep separation of concerns between data structures and analysis
- All equations must match NASA 5020 exactly
- Document any assumptions clearly

## 12. Version History

- Version: 1.0
- Date: 2024-01-08
- Previous: None
- Approved By: Pending

## 13. Appendix: Present project structure

./
    demo.py
    nasa5020.md
    nasa5020_analysis_spec.md
    project_structure.txt
    README.md
    requirements.txt
    setup.py
    __init__.py
    .pytest_cache/
        README.md
    bot_files/
        final-report.md
    components/
        base_component.py
        clamped_components.py
        threaded_components.py
        threaded_plate.py
        __init__.py
    junctions/
        junction.py
        __init__.py
    materials/
        material.py
        standard_materials.py
        __init__.py
    requirements/
        base_component_req.txt
        clamped_components_req.txt
        junction_req.txt
        material_req.txt
        project_req.txt
        standard_materials_req.txt
        threaded_components_req.txt
        threaded_plate_req.txt
        thread_utils_req.txt
        units_config_req.txt
        unit_utils_req.txt
    tests/
        test_base_component.py
        test_clamped_components.py
        test_junction.py
        test_material.py
        test_standard_materials.py
        test_threaded_components.py
        test_threaded_plate.py
        test_thread_utils.py
        test_unit_utils.py
        __init__.py
    units_config/
        __init__.py
    utils/
        thread_utils.py
        unit_utils.py
        __init__.py
