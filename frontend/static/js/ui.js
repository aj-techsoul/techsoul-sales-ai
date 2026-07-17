/* ==========================================
   TechSoul AI
   ui.js
   Handles UI Components Only
========================================== */

// ==========================================
// ELEMENTS
// ==========================================

const projectSection = document.getElementById("project-section");

const featureSection = document.getElementById("feature-section");

const userInput = document.getElementById("user-input");

const sendButton = document.getElementById("send-btn");

const progressFill = document.getElementById("progress-fill");

// ==========================================
// PROJECT SECTION
// ==========================================

function showProjects() {

    projectSection.style.display = "block";

    scrollChat();

}

function hideProjects() {

    projectSection.style.display = "none";

}

// ==========================================
// FEATURE SECTION
// ==========================================

function showFeatures() {

    featureSection.style.display = "block";

    scrollChat();

}

function hideFeatures() {

    featureSection.style.display = "none";

}

// ==========================================
// INPUT CONTROL
// ==========================================

function enableInput() {

    userInput.disabled = false;

    sendButton.disabled = false;

    userInput.focus();

}

function disableInput() {

    userInput.disabled = true;

    sendButton.disabled = true;

}

// ==========================================
// INPUT CLEAR
// ==========================================

function clearInput() {

    userInput.value = "";

}

// ==========================================
// PROGRESS BAR
// ==========================================

function updateProgress(percent) {

    progressFill.style.width = percent + "%";

}

// ==========================================
// RESET UI
// ==========================================

function resetUI() {

    hideProjects();

    hideFeatures();

    enableInput();

    clearInput();

    updateProgress(0);

}

// ==========================================
// INITIALIZE
// ==========================================

window.addEventListener("load", () => {

    resetUI();

});