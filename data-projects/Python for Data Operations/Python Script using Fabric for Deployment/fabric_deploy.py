from fabric import Connection, task

# Configuration
REMOTE_HOST = 'your-server-ip'
REMOTE_USER = 'your-ssh-username'
REMOTE_PATH = '/path/to/deploy/directory'
LOCAL_PROJECT_PATH = './project'
GIT_REPO_URL = 'https://github.com/your-repo/project.git'
VENV_DIR = 'venv'

@task
def deploy(c):
    # Connect to the remote server
    conn = Connection(host=REMOTE_HOST, user=REMOTE_USER)

    # Ensure the remote path exists
    print("Ensuring deployment directory exists on the remote server.")
    conn.run(f"mkdir -p {REMOTE_PATH}")

    # Clone the repository if it doesn't exist, otherwise pull the latest changes
    print("Cloning or pulling the latest code from the repository.")
    with conn.cd(REMOTE_PATH):
        if conn.run(f"test -d {REMOTE_PATH}/.git", warn=True).ok:
            conn.run("git pull")
        else:
            conn.run(f"git clone {GIT_REPO_URL} {REMOTE_PATH}")

    # Setup virtual environment and install dependencies
    print("Setting up virtual environment and installing dependencies.")
    with conn.cd(REMOTE_PATH):
        conn.run(f"python3 -m venv {VENV_DIR}")
        conn.run(f"{VENV_DIR}/bin/pip install -r requirements.txt")

    # Restart the web server (e.g., Gunicorn)
    print("Restarting the web server.")
    conn.run("sudo systemctl restart my_web_app")

    print("Deployment completed successfully!")

@task
def setup(c):
    # Connect to the remote server
    conn = Connection(host=REMOTE_HOST, user=REMOTE_USER)

    # Ensure the necessary packages are installed
    print("Installing necessary packages on the remote server.")
    conn.run("sudo apt-get update")
    conn.run("sudo apt-get install -y python3-pip python3-venv git")

    # Set up the deployment environment
    print("Setting up deployment environment.")
    conn.run(f"mkdir -p {REMOTE_PATH}")

    # Optionally clone the repository
    print("Cloning the repository.")
    conn.run(f"git clone {GIT_REPO_URL} {REMOTE_PATH}")

    print("Setup completed successfully!")

if __name__ == "__main__":
    deploy()
    setup()
