# MedAgentBench Integration Guide

## Integration with MedAgent Suite

MedAgentBench is designed to integrate seamlessly with other agents in the MedAgent Suite platform.

## 🔄 Integration Points

### 1. After Training (MedAgentGym → MedAgentBench)

Evaluate a model immediately after training:

```python
from agents.agent_3_benchmark.integration_example import MedAgentSuiteIntegration

integration = MedAgentSuiteIntegration()

# After MedAgentGym completes training
train_result = integration.evaluate_trained_model(
    model_endpoint_url="http://localhost:8000/predict",
    test_data_path="data/test/benchmark.jsonl",
    model_name="TrainedModel_v1",
    training_run_id="train_001"  # From MedAgentGym
)

if train_result['evaluation_status'] == 'PASS':
    print("✅ Model passed evaluation after training")
else:
    print("❌ Model needs improvement")
```

### 2. Pre-Deployment Check (MedAgentBench → Deployment Agent)

Run evaluation before deploying to production:

```python
# Before deployment
deploy_result = integration.pre_deployment_check(
    model_endpoint_url="http://localhost:8000/predict",
    test_data_path="data/test/benchmark.jsonl",
    model_name="ProductionModel_v1",
    min_score=0.80  # Minimum score required
)

if deploy_result['deployment_approved']:
    print("✅ Approved for deployment")
    # Proceed with deployment agent
else:
    print("❌ Not approved - check certificate for details")
```

### 3. After Simulation (MedAgentClinic → MedAgentBench)

Benchmark model performance after simulation runs:

```python
# After MedAgentClinic simulation
sim_result = integration.benchmark_after_simulation(
    model_endpoint_url="http://localhost:8000/predict",
    simulation_results_path="data/test/simulation_results.jsonl",
    model_name="SimulatedModel_v1",
    simulation_run_id="sim_001"  # From MedAgentClinic
)
```

### 4. Continuous Monitoring

Run periodic evaluations in production:

```python
# Daily evaluation
daily_result = integration.continuous_evaluation(
    model_endpoint_url="http://localhost:8000/predict",
    test_data_path="data/test/benchmark.jsonl",
    model_name="ProductionModel_v1",
    evaluation_schedule="daily"
)
```

## 🔗 Complete Workflow Example

```python
"""
Complete MedAgent Suite Workflow:
1. Data Prep (Agent 1)
2. Train (MedAgentGym - Agent 2)
3. Evaluate (MedAgentBench - Agent 3) ← YOU ARE HERE
4. Deploy (Deployment Agent - Agent 4)
"""

from agents.agent_3_benchmark import MedAgentBench, MedAgentBenchConfig

# Configure MedAgentBench
config = MedAgentBenchConfig(
    model_endpoint_url="http://localhost:8000/predict",
    test_data_path="data/test/benchmark.jsonl"
)

# Create agent
bench_agent = MedAgentBench(config=config)

# Step 1: Evaluate after training
print("Step 1: Evaluating trained model...")
eval_result = bench_agent.evaluate(
    test_data_path="data/test/benchmark.jsonl",
    model_name="MyMedicalModel_v1"
)

# Step 2: Check if ready for deployment
if eval_result['evaluation_status'] == 'PASS':
    overall_score = eval_result['pass_fail_result']['overall_score']
    
    print(f"✅ Model PASSED evaluation (score: {overall_score:.3f})")
    print(f"📄 Certificate: {eval_result['certificate_path']}")
    
    # Step 3: Ready for deployment
    if overall_score >= 0.80:
        print("✅ Ready for production deployment")
    else:
        print("⚠️  Passed but consider improvements before deployment")
else:
    print(f"❌ Model FAILED evaluation")
    print(f"📄 See certificate for details: {eval_result['certificate_path']}")
```

## 📋 Integration Checklist

When integrating MedAgentBench with other agents:

- [ ] **Test Data Ready**: Ensure test JSONL file is available
- [ ] **Model Endpoint**: Verify model endpoint is accessible
- [ ] **Configuration**: Set up MedAgentBenchConfig with correct paths
- [ ] **Thresholds**: Customize thresholds if needed
- [ ] **Output Paths**: Configure certificate and report output directories
- [ ] **Error Handling**: Handle evaluation failures appropriately
- [ ] **Result Storage**: Store evaluation results for downstream agents

## 🔄 Agent Communication Flow

```
┌─────────────────┐
│  MedAgentGym    │ (Training)
│  (Agent 2)      │
└────────┬────────┘
         │ Trained Model
         ▼
┌─────────────────┐
│  MedAgentBench  │ ← YOU ARE HERE
│  (Agent 3)      │ (Evaluation)
└────────┬────────┘
         │ Certificate
         ▼
┌─────────────────┐
│  Deployment     │
│  Agent          │ (Deployment)
│  (Agent 4)      │
└─────────────────┘
```

## 📝 Best Practices

1. **Always evaluate after training** before deployment
2. **Set appropriate thresholds** for your use case
3. **Store certificates** for audit trails
4. **Monitor continuously** in production
5. **Use evaluation IDs** to track model versions

## 🚀 Quick Integration

```python
# Minimal integration example
from agents.agent_3_benchmark import MedAgentBench

agent = MedAgentBench()
result = agent.evaluate(
    test_data_path="data/test/benchmark.jsonl",
    model_endpoint_url="http://localhost:8000/predict",
    model_name="MyModel"
)

print(f"Status: {result['evaluation_status']}")
```

For more details, see `integration_example.py` for complete integration patterns.

