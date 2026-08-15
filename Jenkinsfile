pipeline {
    agent {
        label 'linux-agent'
    }

    environment {
        APP_DIR = "/opt/myapp"
        BACKEND_PORT = "5000"
        FRONTEND_PORT = "3000"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/abhijeetpatel-06/Jenkins-CI-CD-Pipeline-express-flask-application-.git'
            }
        }

        stage('Check Dependencies') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Checking Dependencies"
                    echo "===================================="

                    echo "Python:"
                    command -v python3
                    python3 --version

                    echo "Node.js:"
                    command -v node
                    node --version

                    echo "npm:"
                    command -v npm
                    npm --version

                    echo "Git:"
                    command -v git
                    git --version
                '''
            }
        }

        stage('Backend Build') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Backend Build"
                    echo "===================================="

                    cd backend

                    echo "Creating Python virtual environment..."

                    python3 -m venv venv

                    . venv/bin/activate

                    echo "Upgrading pip..."

                    pip install --upgrade pip

                    if [ -f requirements.txt ]; then
                        echo "Installing backend dependencies..."
                        pip install -r requirements.txt
                    else
                        echo "requirements.txt not found"
                    fi

                    deactivate

                    echo "Backend build completed."
                '''
            }
        }

        stage('Backend Test') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Backend Test"
                    echo "===================================="

                    cd backend

                    . venv/bin/activate

                    if [ -f test_app.py ]; then
                        echo "Running backend tests..."
                        python -m pytest
                    else
                        echo "No test_app.py found."
                        echo "Skipping backend tests."
                    fi

                    deactivate
                '''
            }
        }

        stage('Frontend Build') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Frontend Build"
                    echo "===================================="

                    cd frontend

                    if [ -f package-lock.json ]; then
                        echo "Running npm ci..."
                        npm ci
                    else
                        echo "package-lock.json not found."
                        echo "Running npm install..."
                        npm install
                    fi

                    echo "Running frontend build..."

                    npm run build --if-present

                    echo "Frontend build completed."
                '''
            }
        }

        stage('Frontend Test') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Frontend Test"
                    echo "===================================="

                    cd frontend

                    if npm run 2>/dev/null | grep -q "test"; then
                        echo "Test script found."
                        npm test -- --watchAll=false
                    else
                        echo "No frontend test script found."
                        echo "Skipping frontend tests."
                    fi
                '''
            }
        }

        stage('Prepare Application Directory') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Preparing Application Directory"
                    echo "===================================="

                    sudo mkdir -p ${APP_DIR}

                    sudo chown -R jenkins:jenkins ${APP_DIR}

                    echo "Application directory:"
                    ls -ld ${APP_DIR}
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Deploying Application"
                    echo "===================================="

                    echo "Cleaning old deployment..."

                    rm -rf ${APP_DIR}/backend
                    rm -rf ${APP_DIR}/frontend

                    echo "Copying backend..."

                    cp -r backend ${APP_DIR}/

                    echo "Copying frontend..."

                    cp -r frontend ${APP_DIR}/

                    echo "Deployment files copied."

                    ls -la ${APP_DIR}
                '''
            }
        }

        stage('Install Production Dependencies') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Installing Production Dependencies"
                    echo "===================================="

                    cd ${APP_DIR}/backend

                    echo "Creating backend virtual environment..."

                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi

                    . venv/bin/activate

                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi

                    deactivate

                    echo "Installing frontend dependencies..."

                    cd ${APP_DIR}/frontend

                    if [ -f package-lock.json ]; then
                        npm ci
                    else
                        npm install
                    fi

                    echo "Production dependencies installed."
                '''
            }
        }

        stage('Setup Flask Service') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Setting up Flask Service"
                    echo "===================================="

                    sudo tee /etc/systemd/system/flask-app.service > /dev/null <<EOF
[Unit]
Description=Flask Application
After=network.target

[Service]
Type=simple
User=jenkins
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${APP_DIR}/backend/venv/bin"
ExecStart=${APP_DIR}/backend/venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

                    echo "Flask service created."
                '''
            }
        }

        stage('Setup Frontend Service') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Setting up Frontend Service"
                    echo "===================================="

                    sudo tee /etc/systemd/system/express-app.service > /dev/null <<EOF
[Unit]
Description=Express Frontend Application
After=network.target

[Service]
Type=simple
User=jenkins
WorkingDirectory=${APP_DIR}/frontend
Environment=NODE_ENV=production
Environment=PORT=${FRONTEND_PORT}
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

                    echo "Express service created."
                '''
            }
        }

        stage('Start Services') {
            steps {
                sh '''
                    set -e

                    echo "===================================="
                    echo "Starting Services"
                    echo "===================================="

                    sudo systemctl daemon-reload

                    sudo systemctl enable flask-app
                    sudo systemctl enable express-app

                    sudo systemctl restart flask-app
                    sudo systemctl restart express-app

                    sleep 5

                    echo "Flask status:"
                    sudo systemctl --no-pager status flask-app || true

                    echo "Express status:"
                    sudo systemctl --no-pager status express-app || true
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "===================================="
                    echo "Health Check"
                    echo "===================================="

                    echo ""
                    echo "Flask Service:"
                    sudo systemctl is-active flask-app

                    echo ""
                    echo "Express Service:"
                    sudo systemctl is-active express-app

                    echo ""
                    echo "Listening Ports:"
                    sudo ss -tulnp | grep ":${BACKEND_PORT}" || true
                    sudo ss -tulnp | grep ":${FRONTEND_PORT}" || true

                    echo ""
                    echo "Application Directory:"
                    ls -la ${APP_DIR}

                    echo ""
                    echo "Health check completed."
                '''
            }
        }
    }

    post {
        success {
            echo "===================================="
            echo "DEPLOYMENT SUCCESSFUL"
            echo "===================================="
            echo "Application deployed on linux-agent."
            echo "Backend Port: 5000"
            echo "Frontend Port: 3000"
        }

        failure {
            echo "===================================="
            echo "DEPLOYMENT FAILED"
            echo "===================================="
            echo "Check the stage above for the error."
        }

        always {
            echo "Pipeline execution completed."
        }
    }
}