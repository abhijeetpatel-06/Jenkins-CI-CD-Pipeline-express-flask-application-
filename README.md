# CI/CD Pipeline Using Jenkins

## 📌 Project Overview

This project is about creating a simple **CI/CD pipeline using Jenkins** to automatically deploy two applications:

* **Flask application** – Python
* **Express application** – Node.js

The main goal is to reduce manual deployment work. Whenever new code is pushed to GitHub, Jenkins automatically downloads the latest code, installs the required dependencies, and restarts the application.

## 🛠️ Technologies Used

* Jenkins
* Git & GitHub
* Python
* Flask
* Node.js
* Express.js
* PM2
* AWS EC2

## 🔄 CI/CD Workflow

The basic workflow is:

**Developer → GitHub → Jenkins → Install Dependencies → Restart Application**

### Flask Application

1. Developer pushes code to GitHub.
2. GitHub sends a webhook to Jenkins.
3. Jenkins pulls the latest Flask code.
4. Jenkins installs dependencies using:

   ```bash
   pip install -r requirements.txt
   ```
5. Jenkins restarts the Flask application.

### Express Application

1. Developer pushes code to GitHub.
2. GitHub sends a webhook to Jenkins.
3. Jenkins pulls the latest Express code.
4. Jenkins installs dependencies using:

   ```bash
   npm install
   ```
5. Jenkins restarts the Express application using PM2.

## 📁 Jenkinsfiles

Two separate Jenkins pipelines were created.

### Flask Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git 'FLASK_REPOSITORY_URL'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Deploy') {
            steps {
                sh 'pm2 restart flask-app'
            }
        }
    }
}
```

### Express Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git 'EXPRESS_REPOSITORY_URL'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Deploy') {
            steps {
                sh 'pm2 restart express-app'
            }
        }
    }
}
```

> Replace `FLASK_REPOSITORY_URL` and `EXPRESS_REPOSITORY_URL` with the actual GitHub repository URLs.

## 🔗 GitHub Webhook

A GitHub webhook was configured so that Jenkins is triggered whenever new code is pushed to the repository.

This means the deployment does not need to be started manually after every code change.

## 🔐 Environment Variables

Sensitive information such as API keys, database passwords, and other secrets can be stored in **Jenkins Credentials** instead of directly writing them inside the code or Jenkinsfile.

## 🧪 Optional Testing

Testing stages can also be added to the pipelines.

For Flask:

```bash
pytest
```

For Express:

```bash
npm test
```

If the tests fail, the deployment stage can be stopped.

## ✅ Final Result

After completing the setup:

* Jenkins automatically gets the latest code from GitHub.
* Dependencies are installed automatically.
* Applications are restarted using PM2.
* GitHub webhooks trigger the pipelines after every push.
* Flask and Express applications can be deployed without doing the complete process manually.

## 📸 Evidence

Screenshots can be added here to show:

1. Jenkins dashboard
2. Flask pipeline successful build
3. Express pipeline successful build
4. GitHub webhook configuration
5. Running Flask application
6. Running Express application

## 🎯 What I Learned

Through this project, I learned the basics of **CI/CD and Jenkins**. I understood how GitHub, Jenkins, and an AWS EC2 server can work together to automate application deployment.

I also learned how to use **Jenkins pipelines, webhooks, PM2, and environment variables** for a basic deployment workflow.

## 👨‍💻 Conclusion

This project helped me understand how developers can automate the deployment process instead of manually installing dependencies and restarting applications every time code is changed.

It is a basic CI/CD setup, but it gives me a good starting point for learning more about **DevOps, Jenkins, Docker, cloud deployment, and automation**.
