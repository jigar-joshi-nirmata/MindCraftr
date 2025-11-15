"""Opus API Integration - Official Documentation"""

import time
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OpusAPIError(Exception):
    pass


class OpusClient:
    """Opus API Client following official documentation"""
    
    BASE_URL = "https://operator.opus.com"
    API_KEY = "_b1befdcaff9e627c2f4f2c7c6a802f69a133d246d5d676707ec9dd4b3e6776acc499f965f326c6ec6d687a7679747931"
    WORKFLOW_ID = "vWMUyrVTjwJlfOau"
    GRADING_WORKFLOW_ID = "oBBPtfoqIT9oww5X"
    
    def __init__(self):
        self.headers = {
            'x-service-key': self.API_KEY,
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            logger.info(f"{method} {url}")
            if data:
                logger.debug(f"Request body: {data}")
            response = requests.request(method, url, headers=self.headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json() if response.content else {}
            logger.debug(f"Response: {result}")
            return result
        except Exception as e:
            logger.error(f"API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    logger.error(f"Error response: {e.response.text}")
                except:
                    pass
            raise OpusAPIError(str(e))
    
    def get_workflow_details(self) -> Dict:
        """GET /workflow/{workflowId} - Get workflow details and schema"""
        logger.info(f"Getting workflow details: {self.WORKFLOW_ID}")
        return self._request('GET', f'/workflow/{self.WORKFLOW_ID}')
    
    def initiate_job(self, title: str = None, description: str = None) -> str:
        """POST /job/initiate - Create job and get jobExecutionId"""
        logger.info("Initiating job...")
        
        # Default titles based on workflow
        if title is None:
            if self.WORKFLOW_ID == self.GRADING_WORKFLOW_ID:
                title = "AI Test Grader"
            else:
                title = "AI Test Generator"
        
        if description is None:
            if self.WORKFLOW_ID == self.GRADING_WORKFLOW_ID:
                description = "Grade student test submission with AI-powered analysis"
            else:
                description = "Generate exam questions using AI"
        
        body = {
            "workflowId": self.WORKFLOW_ID,
            "title": title,
            "description": description
        }
        response = self._request('POST', '/job/initiate', data=body)
        job_id = response.get('jobExecutionId')
        logger.info(f"Job initiated: {job_id} - {title}")
        return job_id
    
    def get_workflow_schema_mapping(self) -> Dict[str, str]:
        """Get mapping of display_name to variable_name from workflow schema"""
        try:
            details = self.get_workflow_details()
            schema = details.get('jobPayloadSchema', {})
            
            # Map display_name -> variable_name
            mapping = {}
            for var_name, info in schema.items():
                display_name = info.get('display_name', '')
                if display_name:
                    mapping[display_name] = var_name
            
            logger.info(f"Schema mapping: {mapping}")
            return mapping
        except:
            logger.warning("Could not get schema, using direct mapping")
            return {}
    
    def execute_job(self, job_id: str, inputs: Dict[str, Any]) -> Dict:
        """POST /job/execute - Execute job with inputs"""
        logger.info(f"Executing job: {job_id}")
        logger.info(f"Input keys: {list(inputs.keys())}")
        
        # Get schema mapping to find correct variable names
        schema_mapping = self.get_workflow_schema_mapping()
        
        # Convert inputs to jobPayloadSchemaInstance format
        payload_schema = {}
        
        for key, value in inputs.items():
            # Use schema mapping if available, otherwise use key as-is
            variable_name = schema_mapping.get(key, key)
            
            if isinstance(value, bool):
                payload_schema[variable_name] = {"value": value, "type": "bool"}
            elif isinstance(value, int):
                payload_schema[variable_name] = {"value": value, "type": "int"}
            elif isinstance(value, float):
                payload_schema[variable_name] = {"value": value, "type": "float"}
            elif isinstance(value, list):
                payload_schema[variable_name] = {"value": value, "type": "array"}
            elif isinstance(value, dict):
                payload_schema[variable_name] = {"value": value, "type": "object"}
            else:
                payload_schema[variable_name] = {"value": str(value), "type": "str"}
        
        body = {
            "jobExecutionId": job_id,
            "jobPayloadSchemaInstance": payload_schema
        }
        
        logger.info(f"Execute payload: {body}")
        return self._request('POST', '/job/execute', data=body)
    
    def get_status(self, job_id: str) -> str:
        """GET /job/{jobExecutionId}/status - Get job status"""
        response = self._request('GET', f'/job/{job_id}/status')
        status = response.get('status', 'UNKNOWN')
        logger.info(f"Job {job_id} status: {status}")
        return status
    
    def get_results(self, job_id: str) -> Dict:
        """GET /job/{jobExecutionId}/results - Get job results"""
        logger.info(f"Getting results for job: {job_id}")
        return self._request('GET', f'/job/{job_id}/results')
    
    def run_workflow(self, inputs: Dict[str, Any], max_wait: int = 300, workflow_id: str = None) -> Dict:
        """
        Complete workflow execution:
        1. Initiate job
        2. Execute with inputs
        3. Poll status until COMPLETED
        4. Get results
        """
        # Use custom workflow_id if provided, otherwise use default
        original_workflow = self.WORKFLOW_ID
        if workflow_id:
            self.WORKFLOW_ID = workflow_id
        
        try:
            # Step 1: Initiate
            job_id = self.initiate_job()
            
            # Step 2: Execute
            self.execute_job(job_id, inputs)
            
            # Step 3: Poll status
            start = time.time()
            poll_interval = 5
            
            while time.time() - start < max_wait:
                try:
                    status = self.get_status(job_id)
                    
                    if status == 'COMPLETED':
                        # Step 4: Get results
                        return self.get_results(job_id)
                    
                    if status in ['FAILED', 'ERROR', 'CANCELLED']:
                        raise OpusAPIError(f"Job failed with status: {status}")
                    
                    # Still in progress
                    time.sleep(poll_interval)
                    
                except OpusAPIError:
                    raise
                except Exception as e:
                    logger.warning(f"Status check error: {e}, retrying...")
                    time.sleep(poll_interval)
            
            raise OpusAPIError(f"Job timeout after {max_wait}s")
        finally:
            # Restore original workflow ID
            self.WORKFLOW_ID = original_workflow
    
    def grade_test(self, answer_sheet: Dict[str, Any], syllabus_text: str = "", max_wait: int = 300) -> Dict:
        """
        Grade test using Opus grading workflow
        
        Args:
            answer_sheet: Full test submission with answers and questions
            syllabus_text: Optional syllabus content
            max_wait: Maximum wait time in seconds
        
        Returns:
            Grading results with score, strengths, weaknesses, etc.
        """
        import json
        
        logger.info("Grading test with Opus...")
        
        # Grading workflow expects JSON string for answer sheet (type: "str" in schema)
        # Convert answer_sheet dict to JSON string
        answer_sheet_str = json.dumps(answer_sheet)
        
        # Use exact display names from schema
        inputs = {
            "Answer sheet and grading reference": answer_sheet_str,
            "Syllabus Texts": syllabus_text or "General knowledge assessment"
        }
        
        logger.info(f"Grading inputs prepared (answer_sheet as JSON string)")
        
        # Run grading workflow
        result = self.run_workflow(inputs, max_wait=max_wait, workflow_id=self.GRADING_WORKFLOW_ID)
        
        logger.info("Grading completed")
        return result
