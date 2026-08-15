// PM2 process manager config for both apps.
//
// *** THE ONLY LINE YOU NEED TO EDIT WHEN SWITCHING BETWEEN LOCAL AND EC2 ***
// is API_BASE_URL below, inside the "express-frontend" app's env block.
//
//   Local machine:   API_BASE_URL: "http://localhost:5000"
//   EC2 deployment:  API_BASE_URL: "http://<YOUR_EC2_PUBLIC_IP>:5000"
//
// Everything else can stay exactly as-is.

module.exports = {
  apps: [
    {
      name: "flask-backend",
      script: "app.py",
      interpreter: "python3",
      cwd: "./backend",
      env: {
        PORT: 5000,
      },
    },
    {
      name: "express-frontend",
      script: "server.js",
      cwd: "./frontend",
      env: {
        PORT: 3000,
        // <-- CHANGE THIS ONE LINE FOR EC2 vs LOCAL (see note above) -->
        API_BASE_URL: "http://localhost:5000",
      },
    },
  ],
};
