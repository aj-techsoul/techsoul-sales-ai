/* ==========================================
   TechSoul AI
   cards.js
   Handles Project & Feature Cards
========================================== */

// ==========================================
// SELECTED DATA
// ==========================================

let selectedProject = "";

let selectedFeatures = [];

// ==========================================
// PROJECT CARDS
// ==========================================

const projectCards = document.querySelectorAll(".project-card");

projectCards.forEach(card => {

    card.addEventListener("click", () => {

        // Remove previous selection
        projectCards.forEach(c => {
            c.classList.remove("selected");
        });

        // Select current card
        card.classList.add("selected");

        selectedProject = card.dataset.project;

        // Update Summary
        if (typeof updateProject === "function") {
            updateProject(selectedProject);
        }

        // Hide Project Cards
        setTimeout(() => {

            hideProjects();

        }, 300);

        // Notify script.js
        document.dispatchEvent(
            new CustomEvent("projectSelected", {
                detail: selectedProject
            })
        );

    });

});

// ==========================================
// FEATURE CARDS
// ==========================================

const featureCards = document.querySelectorAll(".feature-card");

featureCards.forEach(card => {

    card.addEventListener("click", () => {

        const feature = card.dataset.feature;

        if (selectedFeatures.includes(feature)) {

            selectedFeatures =
                selectedFeatures.filter(item => item !== feature);

            card.classList.remove("selected");

        }

        else {

            selectedFeatures.push(feature);

            card.classList.add("selected");

        }

        // Update Summary
        if (typeof updateFeatures === "function") {

            updateFeatures(selectedFeatures);

        }

    });

});

// ==========================================
// CONTINUE BUTTON
// ==========================================

const continueButton =
document.getElementById("continue-features");

continueButton.addEventListener("click", () => {

    if (selectedFeatures.length === 0) {

        alert("Please select at least one feature.");

        return;

    }

    hideFeatures();

    document.dispatchEvent(

        new CustomEvent("featuresSelected", {

            detail: selectedFeatures

        })

    );

});

// ==========================================
// RESET PROJECTS
// ==========================================

function resetProjects() {

    selectedProject = "";

    projectCards.forEach(card => {

        card.classList.remove("selected");

    });

}

// ==========================================
// RESET FEATURES
// ==========================================

function resetFeatures() {

    selectedFeatures = [];

    featureCards.forEach(card => {

        card.classList.remove("selected");

    });

}

// ==========================================
// GETTERS
// ==========================================

function getSelectedProject() {

    return selectedProject;

}

function getSelectedFeatures() {

    return selectedFeatures;

}