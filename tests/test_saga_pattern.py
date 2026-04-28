"""Tests for Saga Pattern implementation."""

import pytest
import uuid
from unittest.mock import Mock, MagicMock, call
from app.services.saga_orchestrator import (
    SagaOrchestrator,
    SagaStep,
    SagaStepStatus,
    SagaTransaction,
    SagaTransactionStatus,
    SagaFactory,
)


class TestSagaStep:
    """Test SagaStep data class."""
    
    def test_saga_step_creation(self):
        """Test creating a saga step."""
        action = Mock(return_value="result")
        compensation = Mock()
        
        step = SagaStep(
            name="test_step",
            action=action,
            compensation=compensation,
            priority=1,
        )
        
        assert step.name == "test_step"
        assert step.priority == 1
        assert step.status == SagaStepStatus.PENDING
        assert step.result is None
        assert step.error is None
    
    def test_saga_step_latency(self):
        """Test latency calculation for a saga step."""
        step = SagaStep(
            name="test",
            action=Mock(),
            compensation=Mock(),
        )
        
        assert step.latency == 0.0
        
        # Simulate execution
        step.start_time = 1000.0
        step.end_time = 1100.0
        
        assert step.latency == 100000.0  # milliseconds


class TestSagaTransaction:
    """Test SagaTransaction data class."""
    
    def test_saga_transaction_creation(self):
        """Test creating a saga transaction."""
        steps = [
            SagaStep("step1", Mock(), Mock(), priority=2),
            SagaStep("step2", Mock(), Mock(), priority=1),
        ]
        
        transaction = SagaTransaction(transaction_id="tx_123", steps=steps)
        
        assert transaction.transaction_id == "tx_123"
        assert transaction.status == SagaTransactionStatus.PENDING
        # Steps should be sorted by priority
        assert transaction.steps[0].name == "step2"
        assert transaction.steps[1].name == "step1"
    
    def test_saga_transaction_successful_steps(self):
        """Test filtering successful steps."""
        steps = [
            SagaStep("s1", Mock(), Mock()),
            SagaStep("s2", Mock(), Mock()),
        ]
        
        transaction = SagaTransaction(transaction_id="tx_123", steps=steps)
        transaction.steps[0].status = SagaStepStatus.SUCCESS
        transaction.steps[1].status = SagaStepStatus.FAILED
        
        assert len(transaction.successful_steps) == 1
        assert transaction.successful_steps[0].name == "s1"
    
    def test_saga_transaction_to_dict(self):
        """Test converting transaction to dictionary."""
        steps = [
            SagaStep("s1", Mock(), Mock()),
        ]
        
        transaction = SagaTransaction(transaction_id="tx_123", steps=steps)
        transaction.status = SagaTransactionStatus.SUCCESS
        transaction.start_time = 1000.0
        transaction.end_time = 1100.0
        
        data = transaction.to_dict()
        
        assert data["transaction_id"] == "tx_123"
        assert data["status"] == "success"
        assert data["latency_ms"] == 100000.0
        assert len(data["steps"]) == 1


class TestSagaOrchestrator:
    """Test SagaOrchestrator execution logic."""
    
    def test_happy_path_all_steps_succeed(self):
        """Test saga succeeds when all steps succeed."""
        action1 = Mock(return_value="result1")
        action2 = Mock(return_value="result2")
        comp1 = Mock()
        comp2 = Mock()
        
        steps = [
            SagaStep("step1", action1, comp1, priority=1),
            SagaStep("step2", action2, comp2, priority=2),
        ]
        
        orchestrator = SagaOrchestrator("tx_123", steps)
        transaction = orchestrator.execute()
        
        assert transaction.status == SagaTransactionStatus.SUCCESS
        assert len(transaction.successful_steps) == 2
        assert len(transaction.failed_steps) == 0
        action1.assert_called_once()
        action2.assert_called_once()
        comp1.assert_not_called()
        comp2.assert_not_called()
    
    def test_failure_at_first_step(self):
        """Test saga fails when first step fails."""
        action1 = Mock(side_effect=ValueError("fail1"))
        action2 = Mock(return_value="result2")
        comp1 = Mock()
        comp2 = Mock()
        
        steps = [
            SagaStep("step1", action1, comp1, priority=1),
            SagaStep("step2", action2, comp2, priority=2),
        ]
        
        orchestrator = SagaOrchestrator("tx_123", steps)
        transaction = orchestrator.execute()
        
        assert transaction.status == SagaTransactionStatus.FAILED
        assert len(transaction.successful_steps) == 0
        assert len(transaction.failed_steps) == 1
        action2.assert_not_called()  # Should not reach second step
    
    def test_failure_at_second_step_triggers_compensation(self):
        """Test saga compensates when second step fails."""
        action1 = Mock(return_value="result1")
        action2 = Mock(side_effect=ValueError("fail2"))
        comp1 = Mock()
        comp2 = Mock()
        
        steps = [
            SagaStep("step1", action1, comp1, priority=1),
            SagaStep("step2", action2, comp2, priority=2),
        ]
        
        orchestrator = SagaOrchestrator("tx_123", steps)
        transaction = orchestrator.execute()
        
        assert transaction.status == SagaTransactionStatus.FAILED
        # After compensation, step1 is COMPENSATED not SUCCESS
        assert steps[0].status == SagaStepStatus.COMPENSATED
        assert steps[1].status == SagaStepStatus.FAILED
        # Compensation should be called for step1 only (LIFO)
        comp1.assert_called_once_with("result1")
        comp2.assert_not_called()
    
    def test_compensation_lifo_order(self):
        """Test compensation runs in LIFO (reverse) order."""
        call_order = []
        
        action1 = Mock(side_effect=lambda: (call_order.append("action1"), "result1")[1])
        action2 = Mock(side_effect=lambda: (call_order.append("action2"), "result2")[1])
        action3 = Mock(side_effect=ValueError("fail3"))
        
        comp1 = Mock(side_effect=lambda r: call_order.append("comp1"))
        comp2 = Mock(side_effect=lambda r: call_order.append("comp2"))
        comp3 = Mock()
        
        steps = [
            SagaStep("step1", action1, comp1, priority=1),
            SagaStep("step2", action2, comp2, priority=2),
            SagaStep("step3", action3, comp3, priority=3),
        ]
        
        orchestrator = SagaOrchestrator("tx_123", steps)
        transaction = orchestrator.execute()
        
        # Order should be: action1, action2, action3 fails, comp2, comp1 (LIFO)
        assert call_order == ["action1", "action2", "comp2", "comp1"]
    
    def test_step_status_tracking(self):
        """Test that step statuses are properly tracked."""
        action1 = Mock(return_value="result1")
        comp1 = Mock()
        
        step = SagaStep("step1", action1, comp1)
        orchestrator = SagaOrchestrator("tx_123", [step])
        
        assert step.status == SagaStepStatus.PENDING
        
        transaction = orchestrator.execute()
        
        assert step.status == SagaStepStatus.SUCCESS
        assert step.result == "result1"
        assert step.error is None
        assert step.start_time is not None
        assert step.end_time is not None
    
    def test_step_error_tracking(self):
        """Test that step errors are tracked."""
        error = ValueError("test error")
        action1 = Mock(side_effect=error)
        comp1 = Mock()
        
        step = SagaStep("step1", action1, comp1)
        orchestrator = SagaOrchestrator("tx_123", [step])
        transaction = orchestrator.execute()
        
        assert step.status == SagaStepStatus.FAILED
        assert step.error == error
        assert step.result is None


class TestSagaFactory:
    """Test SagaFactory for saga management."""
    
    def setup_method(self):
        """Reset factory metrics before each test."""
        SagaFactory.reset_metrics()
    
    def test_factory_execute_saga_success(self):
        """Test factory successfully executes a saga."""
        action = Mock(return_value="result")
        comp = Mock()
        
        steps = [SagaStep("step1", action, comp)]
        
        SagaFactory.register_saga_type("test_saga", object)
        transaction = SagaFactory.execute_saga("test_saga", "tx_123", steps)
        
        assert transaction.status == SagaTransactionStatus.SUCCESS
    
    def test_factory_unknown_saga_type(self):
        """Test factory raises error for unknown saga type."""
        steps = [SagaStep("step1", Mock(), Mock())]
        
        with pytest.raises(ValueError, match="Unknown saga type"):
            SagaFactory.execute_saga("unknown_saga", "tx_123", steps)
    
    def test_factory_metrics_tracking_success(self):
        """Test factory tracks metrics for successful sagas."""
        action = Mock(return_value="result")
        steps = [SagaStep("step1", action, Mock())]
        
        SagaFactory.register_saga_type("test_saga", object)
        
        for i in range(3):
            SagaFactory.execute_saga("test_saga", f"tx_{i}", steps)
        
        metrics = SagaFactory.get_metrics("test_saga")
        
        assert metrics["total_executed"] == 3
        assert metrics["total_successful"] == 3
        assert metrics["total_failed"] == 0
        assert metrics["success_rate"] == 100.0
    
    def test_factory_metrics_tracking_mixed(self):
        """Test factory tracks mixed success/failure metrics."""
        action_success = Mock(return_value="result")
        action_fail = Mock(side_effect=ValueError("fail"))
        comp = Mock()
        
        SagaFactory.register_saga_type("test_saga", object)
        
        # Execute 2 successful sagas
        for i in range(2):
            steps = [SagaStep(f"step_{i}", action_success, comp)]
            SagaFactory.execute_saga("test_saga", f"tx_success_{i}", steps)
        
        # Execute 1 failed saga
        steps = [SagaStep("step_fail", action_fail, comp)]
        SagaFactory.execute_saga("test_saga", "tx_fail", steps)
        
        metrics = SagaFactory.get_metrics("test_saga")
        
        assert metrics["total_executed"] == 3
        assert metrics["total_successful"] == 2
        assert metrics["total_failed"] == 1
        assert metrics["success_rate"] == pytest.approx(66.67, 0.01)
    
    def test_factory_reset_metrics(self):
        """Test factory can reset metrics."""
        action = Mock(return_value="result")
        steps = [SagaStep("step1", action, Mock())]
        
        SagaFactory.register_saga_type("test_saga", object)
        SagaFactory.execute_saga("test_saga", "tx_1", steps)
        
        metrics_before = SagaFactory.get_metrics("test_saga")
        assert metrics_before["total_executed"] == 1
        
        SagaFactory.reset_metrics("test_saga")
        metrics_after = SagaFactory.get_metrics("test_saga")
        
        assert metrics_after["total_executed"] == 0
        assert metrics_after["total_successful"] == 0
        assert metrics_after["total_failed"] == 0
    
    def test_factory_multiple_saga_types(self):
        """Test factory handles multiple saga types independently."""
        action1 = Mock(return_value="result")
        action2 = Mock(return_value="result")
        comp = Mock()
        
        SagaFactory.register_saga_type("saga_type_1", object)
        SagaFactory.register_saga_type("saga_type_2", object)
        
        steps1 = [SagaStep("step1", action1, comp)]
        steps2 = [SagaStep("step2", action2, comp)]
        
        SagaFactory.execute_saga("saga_type_1", "tx_1", steps1)
        SagaFactory.execute_saga("saga_type_2", "tx_2", steps2)
        SagaFactory.execute_saga("saga_type_1", "tx_3", steps1)
        
        metrics_all = SagaFactory.get_metrics()
        
        assert metrics_all["saga_type_1"]["total_executed"] == 2
        assert metrics_all["saga_type_2"]["total_executed"] == 1


class TestDocumentProcessingSaga:
    """Test saga for document upload → extract → summary workflow."""
    
    def test_document_processing_saga_happy_path(self):
        """Test complete document processing saga with all steps succeeding."""
        # Setup mocks
        upload_action = Mock(return_value={"id": 1, "filename": "doc.pdf"})
        upload_comp = Mock()
        
        extract_action = Mock(return_value={"text": "extracted text"})
        extract_comp = Mock()
        
        summary_action = Mock(return_value={"summary": "summary text"})
        summary_comp = Mock()
        
        # Create saga steps
        steps = [
            SagaStep("upload", upload_action, upload_comp, priority=1),
            SagaStep("extract", extract_action, extract_comp, priority=2),
            SagaStep("summarize", summary_action, summary_comp, priority=3),
        ]
        
        # Execute saga
        orchestrator = SagaOrchestrator("doc_saga_123", steps)
        transaction = orchestrator.execute()
        
        # Verify success
        assert transaction.status == SagaTransactionStatus.SUCCESS
        assert len(transaction.successful_steps) == 3
        assert transaction.steps[0].result == {"id": 1, "filename": "doc.pdf"}
        assert transaction.steps[1].result == {"text": "extracted text"}
        assert transaction.steps[2].result == {"summary": "summary text"}
    
    def test_document_processing_saga_extract_fails_triggers_rollback(self):
        """Test saga rolls back upload if extract fails."""
        # Setup mocks
        doc_id = 1
        upload_action = Mock(return_value={"id": doc_id, "filename": "doc.pdf"})
        upload_comp = Mock()
        
        extract_action = Mock(side_effect=RuntimeError("PDF extraction failed"))
        extract_comp = Mock()
        
        summary_action = Mock(return_value={"summary": "summary"})
        summary_comp = Mock()
        
        # Create saga steps
        steps = [
            SagaStep("upload", upload_action, upload_comp, priority=1),
            SagaStep("extract", extract_action, extract_comp, priority=2),
            SagaStep("summarize", summary_action, summary_comp, priority=3),
        ]
        
        # Execute saga
        orchestrator = SagaOrchestrator("doc_saga_fail", steps)
        transaction = orchestrator.execute()
        
        # Verify failure and compensation
        assert transaction.status == SagaTransactionStatus.FAILED
        assert steps[0].status == SagaStepStatus.COMPENSATED  # Upload was compensated
        assert steps[1].status == SagaStepStatus.FAILED  # Extract failed
        assert steps[2].status == SagaStepStatus.PENDING  # Summarize never ran
        upload_comp.assert_called_once_with({"id": doc_id, "filename": "doc.pdf"})
        extract_comp.assert_not_called()
        summary_action.assert_not_called()
    
    def test_document_processing_saga_summary_fails_triggers_full_rollback(self):
        """Test saga rolls back everything if summary generation fails."""
        # Setup mocks
        doc_id = 1
        extracted_text = "extracted text"
        
        upload_action = Mock(return_value={"id": doc_id, "filename": "doc.pdf"})
        upload_comp = Mock()
        
        extract_action = Mock(return_value={"text": extracted_text})
        extract_comp = Mock()
        
        summary_action = Mock(side_effect=RuntimeError("AI API error"))
        summary_comp = Mock()
        
        # Create saga steps
        steps = [
            SagaStep("upload", upload_action, upload_comp, priority=1),
            SagaStep("extract", extract_action, extract_comp, priority=2),
            SagaStep("summarize", summary_action, summary_comp, priority=3),
        ]
        
        # Execute saga
        orchestrator = SagaOrchestrator("doc_saga_summary_fail", steps)
        transaction = orchestrator.execute()
        
        # Verify compensation runs in reverse order (LIFO)
        assert transaction.status == SagaTransactionStatus.FAILED
        upload_comp.assert_called_once()
        extract_comp.assert_called_once()
        summary_comp.assert_not_called()
