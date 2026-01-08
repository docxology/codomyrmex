from __future__ import annotations
from typing import Optional
import logging

from codomyrmex.coding.debugging.error_analyzer import ErrorAnalyzer, ErrorDiagnosis
from codomyrmex.coding.debugging.patch_generator import PatchGenerator, Patch
from codomyrmex.coding.debugging.verify_fix import FixVerifier, VerificationResult































logger = logging.getLogger(__name__)

class Debugger:
    """
    Main orchestrator for the autonomous debugging loop.
    """
    
    def __init__(self, llm_client=None):
        self.analyzer = ErrorAnalyzer()
        self.patcher = PatchGenerator(llm_client)
        self.verifier = FixVerifier()
        
    def debug(self, source_code: str, stdout: str, stderr: str, exit_code: int) -> Optional[str]:
        """
        Attempt to fix a failing execution.
        
        Args:
            source_code: The code that failed
            stdout: Output from failed run
            stderr: Error output from failed run
            exit_code: Exit code from failed run
            
        Returns:
            Fixed source code if successful, None otherwise.
        """
        logger.info("Starting debug session...")
        
        # 1. Analyze Error
        diagnosis = self.analyzer.analyze(stdout, stderr, exit_code)
        if not diagnosis:
            logger.info("No error diagnosed or clean exit.")
            return None
            
        logger.info(f"Diagnosed error: {diagnosis.error_type} at line {diagnosis.line_number}")
        
        # 2. Generate Patches
        patches = self.patcher.generate(source_code, diagnosis)
        if not patches:
            logger.warning("No patches generated.")
            return None
            
        # 3. Verify Patches
        for patch in patches:
            verification = self.verifier.verify(source_code, patch)
            if verification.success:
                logger.info(f"Patch verified successfully: {patch.description}")
                # In a real impl, we'd return the patched source code
                return self.verifier._apply_patch(source_code, patch)
                
        logger.info("No patch verified successfully.")
        return None
