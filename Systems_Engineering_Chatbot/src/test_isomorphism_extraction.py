"""
Unit tests for isomorphism extraction and visualization.

Tests the complete flow: LLM prompt generation → mock LLM response → JSON extraction → validation.
"""

import json
import pytest
from unittest.mock import Mock, patch
from isomorphism_visualizer import (
    IsomorphismExtractor,
    IsomorphismAnalyzer,
    IsomorphismVisualizer,
    IsomorphismVisualizerError
)
from prompts import get_isomorphism_extraction_prompt


class TestIsomorphismExtractor:
    """Tests for JSON extraction and validation."""

    @staticmethod
    def get_valid_isomorphism_json() -> str:
        """Returns a valid isomorphism graph JSON string for testing."""
        return json.dumps({
            "systems": [
                {
                    "system_id": "system_1",
                    "system_name": "Mechanical Spring System",
                    "nodes": [
                        {
                            "node_id": "input_1",
                            "node_type": "input",
                            "label": "Applied Force",
                            "mathematical_form": "F(t)",
                            "position": {"x": 50, "y": 50}
                        },
                        {
                            "node_id": "output_1",
                            "node_type": "output",
                            "label": "Displacement",
                            "mathematical_form": "x(t)",
                            "position": {"x": 250, "y": 50}
                        },
                        {
                            "node_id": "tf_1",
                            "node_type": "transfer_function",
                            "label": "Mechanical Transfer Function",
                            "mathematical_form": "H(s) = 1/(ms² + cs + k)",
                            "position": {"x": 150, "y": 200}
                        },
                        {
                            "node_id": "state_1",
                            "node_type": "state_function",
                            "label": "State Vector",
                            "mathematical_form": "[x, ẋ]",
                            "position": {"x": 150, "y": 300}
                        },
                        {
                            "node_id": "interface_1",
                            "node_type": "interface",
                            "label": "System Parameters",
                            "mathematical_form": "m (mass), c (damping), k (stiffness)",
                            "position": {"x": 150, "y": 400}
                        }
                    ]
                },
                {
                    "system_id": "system_2",
                    "system_name": "RLC Circuit",
                    "nodes": [
                        {
                            "node_id": "input_2",
                            "node_type": "input",
                            "label": "Input Voltage",
                            "mathematical_form": "V(t)",
                            "position": {"x": 550, "y": 50}
                        },
                        {
                            "node_id": "output_2",
                            "node_type": "output",
                            "label": "Charge",
                            "mathematical_form": "q(t)",
                            "position": {"x": 750, "y": 50}
                        },
                        {
                            "node_id": "tf_2",
                            "node_type": "transfer_function",
                            "label": "Electrical Transfer Function",
                            "mathematical_form": "H(s) = 1/(Ls² + Rs + 1/C)",
                            "position": {"x": 650, "y": 200}
                        },
                        {
                            "node_id": "state_2",
                            "node_type": "state_function",
                            "label": "State Vector",
                            "mathematical_form": "[q, q̇]",
                            "position": {"x": 650, "y": 300}
                        },
                        {
                            "node_id": "interface_2",
                            "node_type": "interface",
                            "label": "System Parameters",
                            "mathematical_form": "L (inductance), R (resistance), C (capacitance)",
                            "position": {"x": 650, "y": 400}
                        }
                    ]
                }
            ],
            "morphisms": [
                {
                    "morphism_id": "morph_input",
                    "from_node": "input_1",
                    "to_node": "input_2",
                    "morphism_type": "1-to-1",
                    "confidence": 0.95,
                    "reasoning": "Both serve as driving inputs."
                },
                {
                    "morphism_id": "morph_output",
                    "from_node": "output_1",
                    "to_node": "output_2",
                    "morphism_type": "1-to-1",
                    "confidence": 0.90,
                    "reasoning": "Both represent primary outputs."
                },
                {
                    "morphism_id": "morph_tf",
                    "from_node": "tf_1",
                    "to_node": "tf_2",
                    "morphism_type": "structural_isomorphism",
                    "confidence": 0.98,
                    "reasoning": "Identical 2nd-order structure."
                },
                {
                    "morphism_id": "morph_state",
                    "from_node": "state_1",
                    "to_node": "state_2",
                    "morphism_type": "1-to-1",
                    "confidence": 0.92,
                    "reasoning": "Dimensionally equivalent state vectors."
                },
                {
                    "morphism_id": "morph_interface",
                    "from_node": "interface_1",
                    "to_node": "interface_2",
                    "morphism_type": "parameter_mapping",
                    "confidence": 0.96,
                    "reasoning": "m↔L, c↔R, k↔1/C."
                }
            ],
            "overall_assessment": {
                "is_isomorphic": True,
                "isomorphism_type": "full_structural_isomorphism",
                "summary": "Complete structural isomorphism across all components."
            }
        })

    def test_validate_json_structure_valid(self):
        """Test that valid JSON passes validation."""
        json_str = self.get_valid_isomorphism_json()
        data = json.loads(json_str)
        
        # Should not raise
        assert IsomorphismExtractor.validate_json_structure(data) is True

    def test_validate_json_structure_missing_top_level_keys(self):
        """Test that missing top-level keys cause validation failure."""
        data = {
            "systems": [],
            "morphisms": []
            # Missing "overall_assessment"
        }
        
        with pytest.raises(IsomorphismVisualizerError, match="missing required top-level keys"):
            IsomorphismExtractor.validate_json_structure(data)

    def test_validate_json_structure_wrong_system_count(self):
        """Test that non-2-system configs fail validation."""
        data = {
            "systems": [{"system_id": "s1", "system_name": "S1", "nodes": []}],
            "morphisms": [],
            "overall_assessment": {}
        }
        
        with pytest.raises(IsomorphismVisualizerError, match="Exactly 2 systems required"):
            IsomorphismExtractor.validate_json_structure(data)

    def test_validate_json_structure_confidence_out_of_range(self):
        """Test that morphisms with invalid confidence scores fail."""
        json_str = self.get_valid_isomorphism_json()
        data = json.loads(json_str)
        
        # Break a morphism confidence
        data["morphisms"][0]["confidence"] = 1.5  # Out of [0, 1] range
        
        with pytest.raises(IsomorphismVisualizerError, match="confidence must be a number between 0.0 and 1.0"):
            IsomorphismExtractor.validate_json_structure(data)

    def test_extract_from_llm_response_pure_json(self):
        """Test extraction when response is pure JSON."""
        json_str = self.get_valid_isomorphism_json()
        
        data = IsomorphismExtractor.extract_from_llm_response(json_str)
        
        assert "systems" in data
        assert len(data["systems"]) == 2
        assert len(data["morphisms"]) > 0

    def test_extract_from_llm_response_json_with_preamble(self):
        """Test extraction when JSON is embedded in prose."""
        json_str = self.get_valid_isomorphism_json()
        response_with_preamble = f"Here's the analysis:\n\n{json_str}\n\nEnd of analysis."
        
        data = IsomorphismExtractor.extract_from_llm_response(response_with_preamble)
        
        assert "systems" in data
        assert len(data["systems"]) == 2

    def test_extract_from_llm_response_invalid_json(self):
        """Test extraction when response contains no valid JSON."""
        response = "This is just prose with no JSON at all."
        
        with pytest.raises(IsomorphismVisualizerError, match="No JSON found"):
            IsomorphismExtractor.extract_from_llm_response(response)

    def test_extract_from_llm_response_malformed_json(self):
        """Test extraction when response contains malformed JSON."""
        response = "Here's the data: {invalid json that doesn't parse}"
        
        with pytest.raises(IsomorphismVisualizerError, match="Failed to parse JSON"):
            IsomorphismExtractor.extract_from_llm_response(response)


class TestIsomorphismAnalyzer:
    """Tests for analysis and report generation."""

    @staticmethod
    def get_sample_graph_data():
        """Returns sample valid graph data."""
        return json.loads(TestIsomorphismExtractor.get_valid_isomorphism_json())

    def test_generate_analysis_report_structure(self):
        """Test that report is well-formed and contains expected sections."""
        graph_data = self.get_sample_graph_data()
        
        report = IsomorphismAnalyzer.generate_analysis_report(graph_data)
        
        # Check for expected sections
        assert "ISOMORPHISM ANALYSIS REPORT" in report
        assert "SYSTEMS ANALYZED:" in report
        assert "COMPONENT MAPPING:" in report
        assert "MORPHISM ANALYSIS:" in report
        assert "OVERALL ASSESSMENT:" in report
        assert "Mechanical Spring System" in report
        assert "RLC Circuit" in report

    def test_generate_analysis_report_morphism_confidence_tiers(self):
        """Test that morphisms are correctly categorized by confidence."""
        graph_data = self.get_sample_graph_data()
        
        report = IsomorphismAnalyzer.generate_analysis_report(graph_data)
        
        # Morphisms in our sample have high confidence (0.9+)
        assert "High Confidence Morphisms" in report
        assert "✓" in report  # High confidence symbol

    def test_compute_morphism_statistics(self):
        """Test that statistics are correctly computed."""
        graph_data = self.get_sample_graph_data()
        
        stats = IsomorphismAnalyzer.compute_morphism_statistics(graph_data)
        
        assert stats["total_morphisms"] == 5
        assert 0.0 <= stats["average_confidence"] <= 1.0
        assert stats["average_confidence"] > 0.9  # Our sample has high confidence
        assert stats["morphism_types"]["1-to-1"] == 3
        assert stats["morphism_types"]["structural_isomorphism"] == 1
        assert stats["morphism_types"]["parameter_mapping"] == 1
        assert stats["confidence_distribution"]["high"] == 5

    def test_compute_morphism_statistics_empty(self):
        """Test statistics for graph with no morphisms."""
        graph_data = self.get_sample_graph_data()
        graph_data["morphisms"] = []
        
        stats = IsomorphismAnalyzer.compute_morphism_statistics(graph_data)
        
        assert stats["total_morphisms"] == 0
        assert stats["average_confidence"] == 0.0


class TestIsomorphismVisualizer:
    """Integration tests for the complete visualization pipeline."""

    def test_prompt_generation(self):
        """Test that isomorphism extraction prompt is well-formed."""
        system_1 = "Mechanical spring system with mass m, damping c, stiffness k"
        system_2 = "RLC circuit with inductance L, resistance R, capacitance C"
        
        prompt = get_isomorphism_extraction_prompt(system_1, system_2)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "STEP 1: COMPONENT IDENTIFICATION" in prompt
        assert "STEP 2: NODE POSITIONING" in prompt
        assert "STEP 3: MORPHISM DETECTION" in prompt
        assert "STEP 5: OUTPUT STRICTLY FORMATTED JSON" in prompt
        assert system_1 in prompt
        assert system_2 in prompt

    def test_visualizer_integration_with_mock_llm(self):
        """Test complete visualization pipeline with mocked LLM."""
        # Create mock LLM client
        mock_gemini = Mock()
        mock_gemini.query.return_value = TestIsomorphismExtractor.get_valid_isomorphism_json()
        
        visualizer = IsomorphismVisualizer(mock_gemini)
        
        system_1 = "Mechanical spring system"
        system_2 = "RLC circuit"
        
        result = visualizer.extract_isomorphism_structure(system_1, system_2)
        
        # Verify LLM was called
        assert mock_gemini.query.called
        call_args = mock_gemini.query.call_args
        assert "STEP 1: COMPONENT IDENTIFICATION" in call_args[0][0]  # First positional arg is prompt
        
        # Verify result structure
        assert "graph_data" in result
        assert "analysis_report" in result
        assert "statistics" in result
        
        # Verify graph data
        assert len(result["graph_data"]["systems"]) == 2
        assert len(result["graph_data"]["morphisms"]) > 0
        
        # Verify report is generated
        assert len(result["analysis_report"]) > 0
        assert "ISOMORPHISM ANALYSIS REPORT" in result["analysis_report"]
        
        # Verify statistics
        assert result["statistics"]["total_morphisms"] == 5

    def test_visualizer_get_visualization_data(self):
        """Test that get_visualization_data returns correct tuple."""
        mock_gemini = Mock()
        mock_gemini.query.return_value = TestIsomorphismExtractor.get_valid_isomorphism_json()
        
        visualizer = IsomorphismVisualizer(mock_gemini)
        
        graph_data, report = visualizer.get_visualization_data(
            "System 1 desc",
            "System 2 desc"
        )
        
        assert isinstance(graph_data, dict)
        assert isinstance(report, str)
        assert "systems" in graph_data
        assert "morphisms" in graph_data
        assert "ISOMORPHISM ANALYSIS REPORT" in report

    def test_visualizer_handles_llm_error(self):
        """Test that visualizer handles LLM errors gracefully."""
        mock_gemini = Mock()
        mock_gemini.query.side_effect = Exception("LLM connection failed")
        
        visualizer = IsomorphismVisualizer(mock_gemini)
        
        with pytest.raises(IsomorphismVisualizerError, match="Failed to extract isomorphism structure"):
            visualizer.extract_isomorphism_structure("System 1", "System 2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
