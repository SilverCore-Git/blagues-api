/**
 * @author SilverCore
 * @author silverdium
 * @author MisterPapaye
 */

// Import des modules
const express = require("express");
const https = require("https");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const axios = require("axios");


const config = require("./config.json");

let bapi = [];

async function get_bapi() {
    try {
        const response = await axios.get(config.apib.url);
        return response.data;
    } catch (error) {
        console.error("Erreur lors de la récupération des blagues :", error.message);
        return [];
    }
}

async function load_bapi() {
    bapi = await get_bapi();
}

load_bapi(); // Chargement des blagues

// Initialisation d'Express
const app = express();

// Vérification des certificats SSL
const sslKeyPath = `/etc/letsencrypt/live/${config.host.name}/privkey.pem`;
const sslCertPath = `/etc/letsencrypt/live/${config.host.name}/fullchain.pem`;

if (!fs.existsSync(sslKeyPath) || !fs.existsSync(sslCertPath)) {
    console.error("Les fichiers SSL sont introuvables !");
    process.exit(1);
}

const options = {
    key: fs.readFileSync(sslKeyPath, "utf8"),
    cert: fs.readFileSync(sslCertPath, "utf8"),
};

// Configuration CORS
app.use(cors({
    origin: config.host.origin,
}));


// Fonction pour récupérer une blague par ID
function getJokeById(ID) {
    const id = parseInt(ID, 10);
    return bapi.find(d => d.id === id) || { message: "Blague non trouvée.", status: "error" };
}

// Fonction pour récupérer des blagues par type
function getJokesByType(type, random = false) {
    const jokes = bapi.filter(d => d.type === type);

    if (jokes.length === 0) {
        return { message: "Type de blague non trouvé.", status: "error" };
    }

    return random ? jokes[Math.floor(Math.random() * jokes.length)] : jokes;
}

// Fonction pour récupérer une blague aléatoire
function getRandomJoke() {
    return bapi.length > 0 ? bapi[Math.floor(Math.random() * bapi.length)] : { message: "Aucune blague disponible.", status: "error" };
}

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname, "public")));

// Route API principale
app.get("/api", async (req, res) => {
    try {
        const { type, id, arg, random } = req.query;

        if (id !== undefined) {
            return res.json(await getJokeById(id));
        }

        if (type !== undefined) {
            return res.json(await getJokesByType(type, random === "true"));
        }

        if (random === "true") {
            return res.json(await getRandomJoke());
        }

        return res.json(bapi);
    } catch (error) {
        console.error("Erreur API :", error.message);
        res.status(500).json({ status: "error", message: "Erreur interne du serveur." });
    }
});

// Démarrage du serveur HTTPS
const PORT = 3666;
https.createServer(options, app).listen(PORT, () => {
    console.log(`Serveur HTTPS lancé sur https://${config.host.name}:${PORT}`);
});
