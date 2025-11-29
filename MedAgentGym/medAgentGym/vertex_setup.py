import os
import vertexai
from google.cloud import storage
from dotenv import load_dotenv
from google.cloud import aiplatform
import time
from google.cloud.aiplatform_v1.types import JobState
from vertexai.preview import model_garden
from vertexai.preview.tuning import sft, SourceModel
import pandas as pd

def monitor_sft_job(sft_tuning_job):
    """
    Monitors the SFT tuning job status.
    """
    print("Monitoring job... This will take several hours.")
    
    while not sft_tuning_job.state in [
        JobState.JOB_STATE_CANCELLED,
        JobState.JOB_STATE_FAILED,
        JobState.JOB_STATE_SUCCEEDED,
    ]:
        time.sleep(60)  # Check status every 1 minutes
        sft_tuning_job.refresh()
        print(f"Current job state: {str(sft_tuning_job.state.name)}")
    
    print(f"Job finished with state: {sft_tuning_job.state.name}")
    return sft_tuning_job.state.name



def deploy_tuned_model(model_name: str, machine_type: str = "g2-standard-12"):
    """
    Deploys the tuned model to an endpoint.
    """
    load_dotenv()
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is not set.")
        
    bucket_uri = f"gs://{bucket_name}"
    
    # Assume model_name is the full GCS URI to the model artifacts
    model_artifacts_uri = bucket_uri + "/" + model_name + "/postprocess/node-0/checkpoints/final" 
    
    print(f"Deploying model from: {model_artifacts_uri}")

    model = model_garden.CustomModel(
        gcs_uri=model_artifacts_uri,
    )

    # deploy the model to an endpoint using GPUs. Cost will incur for the deployment
    endpoint = model.deploy(
      machine_type=machine_type,
      accelerator_type="NVIDIA_L4",
      accelerator_count=1,
    )
    
    return endpoint.resource_name

def init_vertex_ai():
    """
    Initializes Vertex AI and creates a GCS bucket if it doesn't exist.
    """
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    bucket_name = os.getenv("BUCKET_NAME")

    if not project_id:
        # Fallback to GOOGLE_CLOUD_PROJECT if PROJECT_ID is not set
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not project_id:
        raise ValueError("PROJECT_ID environment variable is not set.")

    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is not set.")

    print(f"Setting up Vertex AI for project: {project_id}, location: {location}")

    # Initialize Storage Client
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    if not bucket.exists():
        print(f"Creating bucket: {bucket_name}")
        bucket.create(location=location)
    else:
        print(f"Bucket {bucket_name} already exists.")

    bucket_uri = f"gs://{bucket_name}"

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location, staging_bucket=bucket_uri)
    print("Vertex AI initialized successfully.")




def train_sft_job(model_id: str, dataset_path: str, epochs: int = 3, tuned_model_display_name: str = None):
    """
    Uploads dataset and submits an SFT training job.
    """
    load_dotenv()
    project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    bucket_name = os.getenv("BUCKET_NAME")
    
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is not set.")

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    bucket_uri = f"gs://{bucket_name}"

    # Upload dataset to GCS
    local_path = os.path.join("datasets", dataset_path)
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Dataset file not found: {local_path}")

    blob_name = dataset_path
    blob = bucket.blob(blob_name)
    
    print(f"Uploading {local_path} to {bucket_uri}/{blob_name}...")
    blob.upload_from_filename(local_path)
    print("Upload complete.")
    
    gcs_data_uri = f"{bucket_uri}/{blob_name}"
    
    # Use tuned_model_display_name for output path if provided, else default
    if tuned_model_display_name:
        gcs_output_uri = f"{bucket_uri}/{tuned_model_display_name}"
    else:
        gcs_output_uri = f"{bucket_uri}/output"

    print(f"Submitting SFT tuning job for model {model_id}...")
    try:
        sft_tuning_job = sft.preview_train(
            source_model=SourceModel(
                base_model=model_id
            ),
            tuning_mode="PEFT_ADAPTER", # FULL or PEFT_ADAPTER
            epochs=epochs,
            train_dataset=gcs_data_uri,
            output_uri=gcs_output_uri,
            tuned_model_display_name=tuned_model_display_name
        )
        print(f"SFT Job submitted: {sft_tuning_job.resource_name}")

        result =  monitor_sft_job(sft_tuning_job)

        return {"status": result, "job_name": sft_tuning_job.resource_name}
    except Exception as e:
        print(f"Failed to submit SFT job: {e}")
        raise e
