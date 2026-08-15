const express = require("express");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

// *** THIS IS THE ONLY THING YOU NEED TO CHANGE FOR EC2 vs LOCAL ***
// Local machine:  http://localhost:5000
// EC2 deployment: http://<YOUR_EC2_PUBLIC_IP>:5000
// Set it in ecosystem.config.js (see README) or as an environment variable
// before starting the app.
const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:5000";

app.get("/health", (req, res) => res.json({ status: "ok" }));

app.get("/", (req, res) => {
  const filePath = path.join(__dirname, "public", "index.html");
  fs.readFile(filePath, "utf8", (err, html) => {
    if (err) return res.status(500).send("Error loading page");
    const rendered = html.replace("__API_BASE_URL__", API_BASE_URL);
    res.send(rendered);
  });
});

app.use(express.static(path.join(__dirname, "public")));

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Frontend listening on port ${PORT}`);
  console.log(`API_BASE_URL = "${API_BASE_URL}"`);
});
