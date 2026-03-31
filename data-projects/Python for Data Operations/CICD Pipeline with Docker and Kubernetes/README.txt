Script Breakdown:
1. Configuration:
	-Set variables for the Docker image name, tag, Kubernetes deployment name, namespace, Dockerfile path, and Kubernetes configuration file path.
2. Shell Command Execution:
	-'run_command' is a utility function to execute shell commands within the script. It handles errors and exits the script if a command fails.
3. Building Docker Image:
	-The script builds a Docker image using the provided Dockerfile.
4. Pushing Docker Image:
	-After building the image, it pushes the image to Docker Hub.
5. Deploying to Kubernetes:
	-The script updates the Kubernetes deployment with the new Docker image.
	-It applies the Kubernetes configuration file to ensure the deployment is updated.
	-Optionally, it checks the status of the deployment to ensure it's running as expected.
6. Cleaning Up Local Docker Images (Optional):
	-The script optionally removes the Docker image from the local environment to free up space.

Key Concepts Demonstrated:
	- CI/CD Automation: Automating the process of building, pushing, and deploying code.
	- Docker: Building and pushing Docker images.
	- Kubernetes: Managing deployments in a Kubernetes cluster.
	- Error Handling: Ensuring that errors are handled gracefully, with informative messages and clean exits.

How to Use:
1. Replace placeholders (your-dockerhub-username/your-image-name, etc.) with your actual Docker Hub username, image name, Kubernetes deployment name, and paths.
2. Ensure Docker, Kubernetes CLI (kubectl), and other required tools are installed and configured correctly on your system.
3. Run the script to automate the CI/CD process.