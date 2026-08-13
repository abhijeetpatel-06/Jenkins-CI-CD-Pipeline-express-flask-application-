const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

// This is the URL the BROWSER will call directly (client-side fetch),
// so it must be an address reachable from the user's machine, not the
// internal docker-network service name. Default matches the port
// docker-compose publishes for the backend on localhost.
const BACKEND_PUBLIC_URL = process.env.BACKEND_PUBLIC_URL || "http://localhost:5000";

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", (req, res) => {
  res.render("index", { backendUrl: BACKEND_PUBLIC_URL });
});

app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
  console.log(`Form will submit to backend at ${BACKEND_PUBLIC_URL}/submit`);
});
