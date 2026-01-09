"""Tests for generator decorator system"""
import pytest
from core.decorators.generator import (
    Generator,
    GeneratorDefinition,
    GENERATORS,
    get_generators_by_category,
    get_generator,
)


class TestGeneratorDecorator:
    """Tests for @Generator decorator"""
    
    def test_decorator_registers_generator(self):
        """Should register generator to global registry"""
        # Create a test generator
        @Generator(category="test", priority=50)
        class TestGenerator:
            """Test generator"""
            pass
        
        assert "TestGenerator" in GENERATORS
        assert GENERATORS["TestGenerator"].category == "test"
        assert GENERATORS["TestGenerator"].priority == 50
        
        # Cleanup
        del GENERATORS["TestGenerator"]
    
    def test_decorator_with_all_options(self):
        """Should handle all decorator options"""
        condition = lambda c: True
        
        @Generator(
            category="custom",
            priority=25,
            requires=["OtherGenerator"],
            conflicts=["ConflictGenerator"],
            enabled_when=condition,
            description="Custom test generator"
        )
        class FullOptionsGenerator:
            pass
        
        gen_def = GENERATORS["FullOptionsGenerator"]
        assert gen_def.category == "custom"
        assert gen_def.priority == 25
        assert gen_def.requires == ["OtherGenerator"]
        assert gen_def.conflicts == ["ConflictGenerator"]
        assert gen_def.enabled_when == condition
        assert gen_def.description == "Custom test generator"
        
        # Cleanup
        del GENERATORS["FullOptionsGenerator"]
    
    def test_decorator_default_values(self):
        """Should use default values when not specified"""
        @Generator(category="default_test")
        class DefaultGenerator:
            pass
        
        gen_def = GENERATORS["DefaultGenerator"]
        assert gen_def.priority == 10  # Default priority
        assert gen_def.requires == []
        assert gen_def.conflicts == []
        assert gen_def.enabled_when is None
        
        # Cleanup
        del GENERATORS["DefaultGenerator"]
    
    def test_decorator_uses_docstring_as_description(self):
        """Should use class docstring as description if not provided"""
        @Generator(category="doc_test")
        class DocstringGenerator:
            """This is the docstring description"""
            pass
        
        gen_def = GENERATORS["DocstringGenerator"]
        assert "docstring description" in gen_def.description
        
        # Cleanup
        del GENERATORS["DocstringGenerator"]


class TestGeneratorDefinition:
    """Tests for GeneratorDefinition dataclass"""
    
    def test_create_definition(self):
        """Should create definition with all fields"""
        gen_def = GeneratorDefinition(
            name="TestGen",
            category="test",
            priority=10,
            requires=["Dep1"],
            conflicts=["Conflict1"],
            enabled_when=lambda c: True,
            generator_class=object,
            description="Test"
        )
        
        assert gen_def.name == "TestGen"
        assert gen_def.category == "test"
        assert gen_def.priority == 10
    
    def test_definition_default_lists(self):
        """Should have empty lists as defaults"""
        gen_def = GeneratorDefinition(
            name="Test",
            category="test",
            priority=10
        )
        
        assert gen_def.requires == []
        assert gen_def.conflicts == []


class TestGetGeneratorsByCategory:
    """Tests for get_generators_by_category function"""
    
    def test_get_by_category(self):
        """Should return generators of specified category"""
        @Generator(category="cat_test_a", priority=1)
        class CatTestA1:
            pass
        
        @Generator(category="cat_test_a", priority=2)
        class CatTestA2:
            pass
        
        @Generator(category="cat_test_b", priority=1)
        class CatTestB1:
            pass
        
        result = get_generators_by_category("cat_test_a")
        names = [g.name for g in result]
        
        assert "CatTestA1" in names
        assert "CatTestA2" in names
        assert "CatTestB1" not in names
        
        # Cleanup
        del GENERATORS["CatTestA1"]
        del GENERATORS["CatTestA2"]
        del GENERATORS["CatTestB1"]
    
    def test_get_empty_category(self):
        """Should return empty list for non-existent category"""
        result = get_generators_by_category("nonexistent_category")
        assert result == []


class TestGetGenerator:
    """Tests for get_generator function"""
    
    def test_get_existing_generator(self):
        """Should return generator definition by name"""
        @Generator(category="get_test", priority=5)
        class GetTestGenerator:
            pass
        
        result = get_generator("GetTestGenerator")
        assert result is not None
        assert result.name == "GetTestGenerator"
        assert result.priority == 5
        
        # Cleanup
        del GENERATORS["GetTestGenerator"]
    
    def test_get_nonexistent_generator(self):
        """Should return None for non-existent generator"""
        result = get_generator("NonExistentGenerator")
        assert result is None
