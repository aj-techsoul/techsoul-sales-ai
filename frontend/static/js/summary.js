/* ==========================================
   TechSoul AI
   summary.js
   Updates Client Summary Panel
========================================== */

// ==========================================
// ELEMENTS
// ==========================================

const clientName = document.getElementById("client-name");

const clientCompany = document.getElementById("client-company");

const clientProject = document.getElementById("client-project");

const clientFeatures = document.getElementById("client-features");

const clientBudget = document.getElementById("client-budget");

const clientTimeline = document.getElementById("client-timeline");

const projectStatus = document.getElementById("project-status");

// ==========================================
// NAME
// ==========================================

function updateName(name) {

    clientName.textContent = name || "-";

}

// ==========================================
// COMPANY
// ==========================================

function updateCompany(company) {

    clientCompany.textContent = company || "-";

}

// ==========================================
// PROJECT
// ==========================================

function updateProject(project) {

    clientProject.textContent = project || "-";

}

// ==========================================
// FEATURES
// ==========================================

function updateFeatures(features) {

    if (!features || features.length === 0) {

        clientFeatures.textContent = "-";

        return;

    }

    clientFeatures.textContent = features.join(", ");

}

// ==========================================
// BUDGET
// ==========================================

function updateBudget(budget) {

    clientBudget.textContent = budget || "-";

}

// ==========================================
// TIMELINE
// ==========================================

function updateTimeline(timeline) {

    clientTimeline.textContent = timeline || "-";

}

// ==========================================
// STATUS
// ==========================================

function updateStatus(status) {

    projectStatus.textContent = status;

}

// ==========================================
// RESET SUMMARY
// ==========================================

function resetSummary() {

    updateName("-");

    updateCompany("-");

    updateProject("-");

    updateFeatures([]);

    updateBudget("-");

    updateTimeline("-");

    updateStatus("Waiting...");

}