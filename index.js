const express = require("express");
const path = require("path");
const { GoogleGenerativeAI } = require("@google/generative-ai");
require('dotenv').config(); // Load environment variables from .env file

const app = express();
const port = process.env.PORT || 3000;

// API Key from Environment Variables (SECURE)
const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
    console.error("GEMINI_API_KEY environment variable not set! Create a .env file and add it.");
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(apiKey);

const model = genAI.getGenerativeModel({
    model: "gemini-2.0-flash", // Or another suitable model
    systemInstruction: "Your name is Suraksha. You are a helpful chatbot that assists with general queries, predicts diseases, suggests Indian-style home remedies, and recommends hospitals for specific conditions. You speak less, work more, and make a strong impact.",
});

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;

    if (!userMessage) {
        return res.status(400).json({ error: "Message is required" });
    }

    try {
        const chatSession = model.startChat();
        const requestPayload = {
            contents: [{ text: userMessage }]  // Corrected: Array of objects!
        };

        const result = await chatSession.sendMessage(requestPayload);
        const botResponse = result.candidates[0]?.content?.parts[0]?.text || "No response received";

        res.json({ response: botResponse });

    } catch (error) {
        console.error("Error during AI response:", error);
        res.status(500).json({ error: "Failed to get response from AI: " + error.message });
    }
});

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});