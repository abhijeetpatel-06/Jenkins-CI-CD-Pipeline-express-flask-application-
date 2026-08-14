pipeline {
    agent any

    environment {
        APP_DIR = "/opt/myapp"

        DEPLOY_USER = "jenkins"
        DEPLOY_HOST = "15.252.88.81"

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
                    echo "Checking Python..."

                    if command -v python3 >/dev/null 2>&1; then
                        echo "Python already installed"
                        python3 --version
                    else
                        echo "Python not installed"
                        exit 1
                    fi

                    echo "Checking Node.js..."

                    if command -v node >/dev/null 2>&1; then
                        echo "Node.js already installed"
                        node --version
                    else
                        echo "Node.js not installed"
                        exit 1
                    fi

                    echo "Checking npm..."

                    if command -v npm >/dev/null 2>&1; then
                        echo "npm already installed"
                        npm --version
                    else
                        echo "npm not installed"
                        exit 1
                    fi
                '''
            }
        }

        stage('Backend Build') {
            steps {
                sh '''
                    cd backend

                    python3 -m venv venv

                    . venv/bin/activate

                    pip install --upgrade pip

                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                '''
            }
        }

        stage('Backend Test') {
            steps {
                sh '''
                    cd backend

                    . venv/bin/activate

                    if [ -f test_app.py ]; then
                        python -m pytest
                    else
                        echo "No backend test file found"
                    fi
                '''
            }
        }

        stage('Frontend Build') {
            steps {
                sh '''
                    cd frontend

                    if [ -f package-lock.json ]; then
                        npm ci
                    else
                        npm install
                    fi

                    npm run build --if-present
                '''
            }
        }

        stage('Frontend Test') {
            steps {
                sh '''
                    cd frontend

                    npm test -- --watchAll=false || true
                '''
            }
        }

        stage('Prepare Deployment Server') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no \
                    ${DEPLOY_USER}@${DEPLOY_HOST} << 'EOF'

                    echo "Checking Python..."

                    if command -v python3 >/dev/null 2>&1; then
                        echo "Python already installed"
                    else
                        echo "Installing Python..."
                        sudo apt update
                        sudo apt install -y python3 python3-pip python3-venv
                    fi

                    echo "Checking Node.js..."

                    if command -v node >/dev/null 2>&1; then
                        echo "Node.js already installed"
                    else
                        echo "Installing Node.js..."
                        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                        sudo apt install -y nodejs
                    fi

                    echo "Checking npm..."

                    if command -v npm >/dev/null 2>&1; then
                        echo "npm already installed"
                    else
                        sudo apt install -y npm
                    fi

                    sudo mkdir -p ${APP_DIR}
                    sudo chown -R ${DEPLOY_USER}:${DEPLOY_USER} ${APP_DIR}

                    EOF
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no \
                    ${DEPLOY_USER}@${DEPLOY_HOST} \
                    "rm -rf ${APP_DIR}/*"

                    scp -o StrictHostKeyChecking=no -r \
                    backend frontend \
                    ${DEPLOY_USER}@${DEPLOY_HOST}:${APP_DIR}/
                '''
            }
        }

        stage('Install Application Dependencies') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no \
                    ${DEPLOY_USER}@${DEPLOY_HOST} << 'EOF'

                    cd ${APP_DIR}

                    echo "Installing backend dependencies..."

                    cd backend

                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi

                    . venv/bin/activate

                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi

                    deactivate

                    echo "Installing frontend dependencies..."

                    cd ../frontend

                    if [ -f package-lock.json ]; then
                        npm ci
                    else
                        npm install
                    fi

                    EOF
                '''
            }
        }

        stage('Setup Services') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no \
                    ${DEPLOY_USER}@${DEPLOY_HOST} << 'EOF'

                    echo "Creating backend service..."

                    sudo tee /etc/systemd/system/flask-app.service > /dev/null << SERVICE
[Unit]
Description=Flask Application
After=network.target

[Service]
User=${DEPLOY_USER}
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${APP_DIR}/backend/venv/bin"
ExecStart=${APP_DIR}/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

                    echo "Creating frontend service..."

                    sudo tee /etc/systemd/system/express-app.service > /dev/null << SERVICE
[Unit]
Description=Express Application
After=network.target

[Service]
User=${DEPLOY_USER}
WorkingDirectory=${APP_DIR}/frontend
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production
Environment=PORT=${FRONTEND_PORT}

[Install]
WantedBy=multi-user.target
SERVICE

                    sudo systemctl daemon-reload

                    sudo systemctl enable flask-app
                    sudo systemctl enable express-app

                    sudo systemctl restart flask-app
                    sudo systemctl restart express-app

                    EOF
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    ssh -o StrictHostKeyChecking=no \
                    ${DEPLOY_USER}@${DEPLOY_HOST} << 'EOF'

                    sleep 5

                    echo "Flask status:"
                    sudo systemctl is-active flask-app

                    echo "Express status:"
                    sudo systemctl is-active express-app

                    echo "Checking ports:"

                    sudo ss -tulnp | grep :${BACKEND_PORT} || true
                    sudo ss -tulnp | grep :${FRONTEND_PORT} || true

                    EOF
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment completed successfully."
        }

        failure {
            echo "Deployment failed."
        }
    }
}
