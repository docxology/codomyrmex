"""Verification script for batch 3 module enhancements."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_compression_compare():
    """Test compression compare_formats function."""
    print("\nTesting Compression Enhancements...")
    from codomyrmex.compression.compressor import compare_formats, Compressor
    
    # Test compare_formats
    data = b"Hello World! " * 100
    results = compare_formats(data)
    
    print(f"Compared {len(Compressor.SUPPORTED_FORMATS)} formats:")
    for fmt, stats in results.items():
        if "error" in stats:
            print(f"  {fmt}: ERROR - {stats['error']}")
        else:
            print(f"  {fmt}: {stats['ratio']}% reduction in {stats['time_ms']}ms")
    
    assert len(results) >= 3
    print("✅ Compression Enhancements: PASSED")

def test_code_editor():
    """Test CodeEditor new methods."""
    print("\nTesting CodeEditor Enhancements...")
    from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor
    
    editor = CodeEditor()
    
    sample_code = '''
"""Sample module."""
import os

class MyClass:
    def __init__(self):
        pass
        
def my_function():
    # A comment
    return True
'''
    
    # Test analyze_code
    analysis = editor.analyze_code(sample_code)
    assert analysis["total_lines"] > 0
    assert len(analysis["classes"]) == 1
    assert len(analysis["functions"]) == 2  # __init__ + my_function
    print(f"Analysis: {analysis['total_lines']} lines, {len(analysis['functions'])} functions")
    
    # Test explain_code
    explanation = editor.explain_code(sample_code)
    assert "lines" in explanation
    assert "class" in explanation
    print(f"Explanation: {explanation[:80]}...")
    
    print("✅ CodeEditor Enhancements: PASSED")

def test_knowledge_base():
    """Test KnowledgeBase enhancements."""
    print("\nTesting KnowledgeBase Enhancements...")
    from codomyrmex.agents.theory.agent_architectures import KnowledgeBase
    
    kb = KnowledgeBase()
    
    # Test CRUD
    kb.add_fact("color", "blue")
    kb.add_fact("size", "large")
    assert kb.get_fact("color") == "blue"
    assert kb.has_fact("size") == True
    assert len(kb.list_facts()) == 2
    
    # Test remove
    result = kb.remove_fact("color")
    assert result == True
    assert kb.has_fact("color") == False
    
    # Test clear
    kb.clear()
    assert len(kb.list_facts()) == 0
    
    print("✅ KnowledgeBase Enhancements: PASSED")

if __name__ == "__main__":
    test_compression_compare()
    test_code_editor()
    test_knowledge_base()
    print("\n" + "="*50)
    print("ALL BATCH 3 TESTS PASSED ✅")
