import os
import subprocess
import sys

# Configuration
DOCKER_IMAGE_NAME = "your-dockerhub-username/your-image-name"
DOCKER_TAG = "latest"
KUBE_DEPLOYMENT_NAME = "your-k8s-deployment"
KUBE_NAMESPACE = "default"
DOCKERFILE_PATH = "./Dockerfile"
KUBERNETES_CONFIG_PATH = "./k8s-deployment.yaml"

# Function to execute shell commands
def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

# Step 1: Build Docker Image
def build_docker_image():
    print(f"Building Docker image: {DOCKER_IMAGE_NAME}:{DOCKER_TAG}")
    run_command(f"docker build -t {DOCKER_IMAGE_NAME}:{DOCKER_TAG} -f {DOCKERFILE_PATH} .")

# Step 2: Push Docker Image to Docker Hub
def push_docker_image():
    print(f"Pushing Docker image to Docker Hub: {DOCKER_IMAGE_NAME}:{DOCKER_TAG}")
    run_command(f"docker push {DOCKER_IMAGE_NAME}:{DOCKER_TAG}")

# Step 3: Deploy to Kubernetes
def deploy_to_kubernetes():
    print(f"Deploying to Kubernetes: {KUBE_DEPLOYMENT_NAME} in namespace {KUBE_NAMESPACE}")
    
    # Update the Kubernetes deployment with the new image
    run_command(f"kubectl set image deployment/{KUBE_DEPLOYMENT_NAME} {KUBE_DEPLOYMENT_NAME}={DOCKER_IMAGE_NAME}:{DOCKER_TAG} -n {KUBE_NAMESPACE}")

    # Apply the Kubernetes configuration file
    run_command(f"kubectl apply -f {KUBERNETES_CONFIG_PATH} -n {KUBE_NAMESPACE}")

    # Optional: Check the status of the deployment
    run_command(f"kubectl rollout status deployment/{KUBE_DEPLOYMENT_NAME} -n {KUBE_NAMESPACE}")

# Step 4: Clean up local Docker images (optional)
def cleanup_local_images():
    print(f"Cleaning up local Docker images: {DOCKER_IMAGE_NAME}:{DOCKER_TAG}")
    run_command(f"docker rmi {DOCKER_IMAGE_NAME}:{DOCKER_TAG}")

# Main function
if __name__ == "__main__":
    # Build Docker Image
    build_docker_image()
    
    # Push Docker Image to Docker Hub
    push_docker_image()
    
    # Deploy to Kubernetes
    deploy_to_kubernetes()
    
    # Optional: Clean up local Docker images
    cleanup_local_images()

    print("CI/CD pipeline executed successfully!")
