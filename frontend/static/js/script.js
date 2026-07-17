/* ==========================================
   TechSoul AI
   script.js
   Main Frontend Controller
========================================== */

// ==========================================
// CLIENT STATE & MEMORY MAPPINGS
// ==========================================

const client = {
    name: "",
    company: "",
    project: "",
    features: [],
    budget: "",
    timeline: ""
};

// ==========================================
// INPUT ELEMENTS
// ==========================================

const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// ==========================================
// INITIAL EVENT BINDINGS
// ==========================================

if (sendBtn) {
    sendBtn.addEventListener("click", processInput);
}

if (input) {
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            processInput();
        }
    });
}

// ==========================================
// SYNC SUMMARY PANEL WITH BACKEND DATA
// ==========================================

function syncSummary(clientData) {
    if (!clientData) return;
    
    // Update local variables
    client.name = clientData.name;
    client.company = clientData.company;
    client.project = clientData.project;
    client.features = clientData.features || [];
    client.budget = clientData.budget;
    client.timeline = clientData.timeline;

    // Call summary panel update functions (defined in summary.js)
    if (typeof updateName === "function") updateName(client.name);
    if (typeof updateCompany === "function") updateCompany(client.company);
    if (typeof updateProject === "function") updateProject(client.project);
    if (typeof updateFeatures === "function") updateFeatures(client.features);
    if (typeof updateBudget === "function") updateBudget(client.budget);
    if (typeof updateTimeline === "function") updateTimeline(client.timeline);

    // Toggle Budget Simulator
    if (client.project) {
        const simContainer = document.getElementById("simulator-container");
        if (simContainer) {
            simContainer.style.display = "block";
            const slider = document.getElementById("sim-budget-slider");
            const inputField = document.getElementById("sim-budget-input");
            
            let cleanBudget = parseInt(String(client.budget).replace(/[^\d]/g, ""));
            if (isNaN(cleanBudget) || cleanBudget < 10000) cleanBudget = 50000;
            
            if (slider && parseInt(slider.value) !== cleanBudget) slider.value = cleanBudget;
            if (inputField && parseInt(inputField.value) !== cleanBudget) inputField.value = cleanBudget;
            
            recalculateSimulation(cleanBudget);
        }
    } else {
        const simContainer = document.getElementById("simulator-container");
        if (simContainer) simContainer.style.display = "none";
    }

    // Dynamic progress bar calculation
    let progress = 0;
    if (client.name) progress += 15;
    if (client.company) progress += 15;
    if (client.project) progress += 20;
    if (client.features && client.features.length > 0) progress += 15;
    if (client.budget) progress += 15;
    if (client.timeline) progress += 20;

    if (typeof updateProgress === "function") {
        updateProgress(progress);
    }
}

// ==========================================
// PROCESS INPUT SUBMISSION
// ==========================================

function processInput() {
    const message = input.value.trim();
    if (message === "") return;

    // Display user message in chat bubble
    if (typeof addUserMessage === "function") {
        addUserMessage(message);
    }

    clearInput();
    disableInput();

    // Call chatbot reply API
    showTyping();
    fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(payload => {
        hideTyping();
        enableInput();

        if (payload.success) {
            const data = payload.data;
            handleBackendResponse(data);
        } else {
            if (typeof addBotMessage === "function") {
                addBotMessage(`<p class="error">${payload.message}</p>`);
            }
        }
    })
    .catch(err => {
        hideTyping();
        enableInput();
        console.error("Chat API Error:", err);
    });
}

// ==========================================
// HANDLE BACKEND API RESPONSE
// ==========================================

function handleBackendResponse(data) {
    // Show bot reply
    if (typeof addBotMessage === "function") {
        // Convert line breaks to HTML paragraphs/breaks for better formatting
        let replyHtml = data.reply.replace(/\n/g, "<br>");
        
        // If completed, add PDF Proposal Download link
        if (data.completed && data.pdf_file) {
            replyHtml += `
                <div class="completion-box" style="margin-top: 15px; padding: 15px; background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; border-radius: 8px;">
                    <p style="margin-bottom: 10px;">📄 Your customized PDF Proposal is ready for download!</p>
                    <a href="/api/proposal/download/${data.pdf_file}" target="_blank" class="menu-btn active" style="display: inline-flex; text-decoration: none; width: auto; font-weight: 500;">
                        <i class="fa-solid fa-file-pdf"></i> Download PDF Proposal
                    </a>
                </div>
            `;
            if (typeof updateStatus === "function") {
                updateStatus("Completed");
            }
        }
        
        addBotMessage(replyHtml);
    }

    // Update Client Summary panel
    if (data.client) {
        syncSummary(data.client);
    }

    // Handle states for Project or Feature Selection Cards display
    const state = data.state;
    if (state === "ASK_PROJECT") {
        if (typeof showProjects === "function") {
            showProjects();
            // Keep input enabled for natural queries
        }
    } else {
        if (typeof hideProjects === "function") hideProjects();
    }

    if (state === "ASK_FEATURES") {
        if (typeof showFeatures === "function") {
            showFeatures();
            // Keep input enabled for natural queries
        }
    } else {
        if (typeof hideFeatures === "function") hideFeatures();
    }
}

// ==========================================
// CARD SELECTIONS LISTENERS
// ==========================================

// Project card click listener
document.addEventListener("projectSelected", function (e) {
    const selectedProj = e.detail;
    
    // Add user bubble
    if (typeof addUserMessage === "function") {
        addUserMessage(selectedProj);
    }

    if (typeof hideProjects === "function") hideProjects();
    enableInput();

    // Submit selection to backend
    showTyping();
    fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: selectedProj })
    })
    .then(response => response.json())
    .then(payload => {
        hideTyping();
        if (payload.success) {
            handleBackendResponse(payload.data);
        }
    })
    .catch(err => {
        hideTyping();
        console.error("Project selection API error:", err);
    });
});

// Features card click listener
document.addEventListener("featuresSelected", function (e) {
    const selectedFeats = e.detail;
    const featsStr = selectedFeats.join(", ");

    // Add user bubble
    if (typeof addUserMessage === "function") {
        addUserMessage(featsStr);
    }

    if (typeof hideFeatures === "function") hideFeatures();
    enableInput();

    // Submit selection to backend
    showTyping();
    fetch("/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: featsStr })
    })
    .then(response => response.json())
    .then(payload => {
        hideTyping();
        if (payload.success) {
            handleBackendResponse(payload.data);
        }
    })
    .catch(err => {
        hideTyping();
        console.error("Features selection API error:", err);
    });
});

// ==========================================
// RESET CONVERSATION & NEW CHAT
// ==========================================

const newChatBtn = document.getElementById("new-chat-btn");
if (newChatBtn) {
    newChatBtn.addEventListener("click", resetConversation);
}

function resetConversation() {
    // Call reset API
    fetch("/api/reset", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reset UI components
            if (typeof resetProjects === "function") resetProjects();
            if (typeof resetFeatures === "function") resetFeatures();
            if (typeof resetSummary === "function") resetSummary();
            if (typeof resetUI === "function") resetUI();

            // Fetch initial start chat details
            startConversation();
        }
    })
    .catch(err => console.error("Reset API Error:", err));
}

// ==========================================
// START CHAT API INITIAL KICKOFF
// ==========================================

function startConversation() {
    if (typeof clearChat === "function") {
        clearChat();
    }
    showTyping();

    fetch("/api/start")
    .then(response => response.json())
    .then(payload => {
        hideTyping();
        if (payload.success) {
            const data = payload.data;
            
            // Sync Summary
            if (data.client) {
                syncSummary(data.client);
            }

            // If it's a restored session, fetch and render all messages!
            if (payload.message === "Active chat restored.") {
                fetch(`/api/chats/${data.chat_id}/messages`)
                .then(res => res.json())
                .then(msgPayload => {
                    if (msgPayload.success) {
                        msgPayload.data.messages.forEach(m => {
                            if (m.role === "user") {
                                if (typeof addUserMessage === "function") addUserMessage(m.content);
                            } else {
                                if (typeof addBotMessage === "function") addBotMessage(m.content.replace(/\n/g, "<br>"));
                            }
                        });
                        // Update features and project display status
                        handleBackendResponse(data);
                    }
                });
            } else {
                // Output welcome message
                if (typeof addBotMessage === "function") {
                    addBotMessage(data.reply.replace(/\n/g, "<br>"));
                }
                // Handle initial state setup
                handleBackendResponse(data);
            }
            loadSidebarChats();
        }
    })
    .catch(err => {
        hideTyping();
        console.error("Start chat API error:", err);
    });
}

// ==========================================
// MULTI-CHAT SIDEBAR LOADING
// ==========================================

function loadSidebarChats() {
    const list = document.getElementById("sidebar-chats-list");
    if (!list) return;

    fetch("/api/chats")
    .then(res => res.json())
    .then(payload => {
        if (payload.success && payload.data.chats.length > 0) {
            list.innerHTML = "";
            payload.data.chats.forEach(c => {
                const btn = document.createElement("button");
                btn.className = "menu-btn";
                btn.style.padding = "10px 12px";
                btn.style.fontSize = "13px";
                btn.style.display = "flex";
                btn.style.justifyContent = "space-between";
                btn.style.alignItems = "center";
                btn.style.width = "100%";
                btn.style.border = "none";
                btn.style.background = "transparent";
                btn.style.color = "var(--text-muted)";
                btn.style.cursor = "pointer";
                btn.style.borderRadius = "8px";
                
                btn.innerHTML = `
                    <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 150px; text-align: left;"><i class="fa-solid fa-message" style="margin-right:8px; font-size:11px;"></i> ${c.title}</span>
                    <i class="fa-solid fa-trash" style="font-size:11px; opacity:0.6; cursor:pointer;" onclick="event.stopPropagation(); deleteSidebarChat(${c.id})"></i>
                `;
                btn.addEventListener("click", () => {
                    continueSidebarChat(c.id);
                });
                list.appendChild(btn);
            });
        } else {
            list.innerHTML = `<p style="font-size: 12px; color: var(--text-muted); padding: 5px 10px;">No chats yet.</p>`;
        }
    })
    .catch(err => console.error("Error loading sidebar chats:", err));
}

function continueSidebarChat(id) {
    fetch(`/api/chats/${id}/continue`, { method: "POST" })
    .then(res => res.json())
    .then(payload => {
        if (payload.success) {
            startConversation();
        }
    });
}

function deleteSidebarChat(id) {
    if (confirm("Delete this consultation?")) {
        fetch(`/api/chats/${id}/delete`, { method: "POST" })
        .then(res => res.json())
        .then(() => {
            loadSidebarChats();
            fetch("/api/status")
            .then(res => res.json())
            .then(payload => {
                if (!payload.data.chat_id) {
                    startConversation();
                }
            });
        });
    }
}

// ==========================================
// BUDGET SIMULATOR CONTROLLER
// ==========================================

let simulatedData = null;

function initBudgetSimulator() {
    const slider = document.getElementById("sim-budget-slider");
    const inputField = document.getElementById("sim-budget-input");

    if (!slider || !inputField) return;

    slider.addEventListener("input", function() {
        inputField.value = slider.value;
        recalculateSimulation(slider.value);
    });

    inputField.addEventListener("change", function() {
        let val = parseInt(inputField.value);
        if (isNaN(val) || val < 10000) val = 10000;
        if (val > 300000) val = 300000;
        inputField.value = val;
        slider.value = val;
        recalculateSimulation(val);
    });
}

function recalculateSimulation(budgetValue) {
    const project = client.project || "E-Commerce";
    
    fetch(`/api/simulator/recalculate?budget=${budgetValue}&project=${encodeURIComponent(project)}`)
    .then(res => res.json())
    .then(payload => {
        if (payload.success) {
            const data = payload.data;
            simulatedData = data;

            // Included features
            const incContainer = document.getElementById("sim-features-included");
            if (incContainer) {
                incContainer.innerHTML = data.features_included.length > 0 
                    ? data.features_included.map(f => `<span class="badge badge-success" style="padding:4px 8px; font-size:11px; background:rgba(16,185,129,0.15); color:#34d399; border-radius:12px; border:1px solid rgba(16,185,129,0.3); font-weight:500;">${f}</span>`).join("")
                    : `<span style="color:var(--text-muted); font-size:12px;">None</span>`;
            }

            // Excluded features
            const excContainer = document.getElementById("sim-features-excluded");
            if (excContainer) {
                excContainer.innerHTML = data.features_excluded.length > 0
                    ? data.features_excluded.map(f => `<span class="badge badge-danger" style="padding:4px 8px; font-size:11px; background:rgba(239,68,68,0.15); color:#f87171; border-radius:12px; border:1px solid rgba(239,68,68,0.3); text-decoration:line-through; font-weight:500;">${f}</span>`).join("")
                    : `<span style="color:var(--text-muted); font-size:12px;">None</span>`;
            }

            // Tech Stack
            const techEl = document.getElementById("sim-tech-stack");
            if (techEl) techEl.textContent = data.tech_stack;
            
            // Timeline
            const timelineEl = document.getElementById("sim-timeline");
            if (timelineEl) timelineEl.textContent = data.timeline;

            // ROI
            const roiEl = document.getElementById("sim-roi");
            if (roiEl) roiEl.textContent = `${data.roi.roi_statement} ${data.roi.ops_savings}`;

            // Est Cost
            const estCostEl = document.getElementById("sim-est-cost");
            if (estCostEl) estCostEl.textContent = `₹${data.estimated_project_cost.toLocaleString()}`;
            
            // Budget Gap
            const gapEl = document.getElementById("sim-gap");
            if (gapEl) {
                if (data.budget_gap > 0) {
                    gapEl.textContent = `+₹${data.budget_gap.toLocaleString()}`;
                    gapEl.style.color = "#f87171"; // red for gap
                } else {
                    gapEl.textContent = `Surplus: -₹${Math.abs(data.budget_gap).toLocaleString()}`;
                    gapEl.style.color = "#34d399"; // green for surplus
                }
            }
            
            // Recommended Package
            const recPkgEl = document.getElementById("sim-recommended-package");
            if (recPkgEl) {
                let recPkgName = "Starter";
                if (data.budget >= 150000) recPkgName = "Enterprise";
                else if (data.budget >= 60000) recPkgName = "Professional";
                recPkgEl.textContent = `${recPkgName} Package`;
            }
        }
    })
    .catch(err => console.error("Recalculate simulator error:", err));
}

function openComparisonModal() {
    const modal = document.getElementById("comparison-modal");
    if (!modal) return;

    modal.style.display = "flex";

    if (!simulatedData) return;

    // 1. Stats Bar
    const statsBar = document.getElementById("sim-stats-bar");
    if (statsBar) {
        const gapText = simulatedData.budget_gap > 0 
            ? `<span style="color:#f87171; font-weight:700;">+₹${simulatedData.budget_gap.toLocaleString()} Gap</span>`
            : `<span style="color:#34d399; font-weight:700;">-₹${Math.abs(simulatedData.budget_gap).toLocaleString()} Surplus</span>`;
            
        statsBar.innerHTML = `
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:15px; display:flex; flex-direction:column; gap:4px;">
                <span style="font-size:11px; text-transform:uppercase; color:#94a3b8;">Current Budget</span>
                <span style="font-size:18px; font-weight:700; color:#fff;">₹${simulatedData.budget.toLocaleString()}</span>
            </div>
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:15px; display:flex; flex-direction:column; gap:4px;">
                <span style="font-size:11px; text-transform:uppercase; color:#94a3b8;">Est. Solution Cost</span>
                <span style="font-size:18px; font-weight:700; color:#38bdf8;">₹${simulatedData.estimated_project_cost.toLocaleString()}</span>
            </div>
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:15px; display:flex; flex-direction:column; gap:4px;">
                <span style="font-size:11px; text-transform:uppercase; color:#94a3b8;">Budget Balance</span>
                <span style="font-size:18px; font-weight:700;">${gapText}</span>
            </div>
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:15px; display:flex; flex-direction:column; gap:4px;">
                <span style="font-size:11px; text-transform:uppercase; color:#94a3b8;">Complexity Classification</span>
                <span style="font-size:16px; font-weight:700; color:#fbbf24; text-transform:capitalize;">${simulatedData.complexity || "Medium"}</span>
            </div>
        `;
    }

    // 2. Packages Grid
    if (simulatedData.packages) {
        const grid = document.getElementById("sim-packages-grid");
        if (grid) {
            const currentBudget = simulatedData.budget;
            grid.innerHTML = "";
            Object.entries(simulatedData.packages).forEach(([pkgName, pkg]) => {
                const isPromo = pkgName === "Professional";
                const isStarter = pkgName === "Starter";
                const isEnterprise = pkgName === "Enterprise";

                // Budget Difference (estimated cost - current budget)
                const diff = pkg.price - currentBudget;
                let diffText = "";
                let diffColor = "";
                if (diff > 0) {
                    diffText = `Gap: +₹${diff.toLocaleString()}`;
                    diffColor = "#f87171"; // Red
                } else {
                    diffText = `Surplus: -₹${Math.abs(diff).toLocaleString()}`;
                    diffColor = "#34d399"; // Green
                }

                // Badges
                let badgeHTML = "";
                if (isPromo) {
                    badgeHTML = `
                        <span style="background:#3b82f6; color:#fff; font-size:9px; font-weight:700; text-transform:uppercase; padding:2px 6px; border-radius:10px; margin-right:4px;">⭐ Recommended</span>
                        <span style="background:#10b981; color:#fff; font-size:9px; font-weight:700; text-transform:uppercase; padding:2px 6px; border-radius:10px;">✔ Best Value</span>
                    `;
                } else if (isStarter) {
                    badgeHTML = `<span style="background:#6b7280; color:#fff; font-size:9px; font-weight:700; text-transform:uppercase; padding:2px 6px; border-radius:10px;">💸 Budget Friendly</span>`;
                } else if (isEnterprise) {
                    badgeHTML = `<span style="background:#8b5cf6; color:#fff; font-size:9px; font-weight:700; text-transform:uppercase; padding:2px 6px; border-radius:10px;">🚀 Enterprise Ready</span>`;
                }

                // Features lists
                const incFeatures = pkg.features;
                const allProjectFeatures = simulatedData.categories.essential.concat(simulatedData.categories.recommended).concat(simulatedData.categories.future);
                const excFeatures = allProjectFeatures.filter(f => !incFeatures.includes(f));

                // Features unlocked
                let unlockedHTML = "";
                if (isPromo && simulatedData.packages.Starter) {
                    const starterFeats = simulatedData.packages.Starter.features;
                    const unlocked = incFeatures.filter(f => !starterFeats.includes(f));
                    if (unlocked.length > 0) {
                        unlockedHTML = `
                            <div>
                                <strong style="display:block; margin-bottom:4px; font-size:11px; text-transform:uppercase; color:#60a5fa; font-weight:600;">🔓 Features Unlocked</strong>
                                <div style="display:flex; flex-wrap:wrap; gap:4px;">
                                    ${unlocked.map(f => `<span style="background:rgba(96,165,250,0.1); color:#60a5fa; padding:2px 6px; border-radius:6px; font-size:10px; border:1px solid rgba(96,165,250,0.2);">${f}</span>`).join("")}
                                </div>
                            </div>
                        `;
                    }
                } else if (isEnterprise && simulatedData.packages.Professional) {
                    const promoFeats = simulatedData.packages.Professional.features;
                    const unlocked = incFeatures.filter(f => !promoFeats.includes(f));
                    if (unlocked.length > 0) {
                        unlockedHTML = `
                            <div>
                                <strong style="display:block; margin-bottom:4px; font-size:11px; text-transform:uppercase; color:#c084fc; font-weight:600;">🔓 Features Unlocked</strong>
                                <div style="display:flex; flex-wrap:wrap; gap:4px;">
                                    ${unlocked.map(f => `<span style="background:rgba(192,132,252,0.1); color:#c084fc; padding:2px 6px; border-radius:6px; font-size:10px; border:1px solid rgba(192,132,252,0.2);">${f}</span>`).join("")}
                                </div>
                            </div>
                        `;
                    }
                }

                // ROI & Business Benefits
                let roiText = "";
                if (isStarter) {
                    roiText = "Phase 1 validates your market demand, providing core user authentication and front-end interface trust at low cost.";
                } else if (isPromo) {
                    roiText = simulatedData.roi.roi_statement + " " + simulatedData.roi.ops_savings;
                } else if (isEnterprise) {
                    roiText = "Fully customized AI automation, automated alerts pipelines, and full CRM integrations for maximum scale and data intelligence.";
                }

                // Tech Stack Selection
                const techStack = isStarter ? "WordPress / PHP / SQLite" : (isPromo ? "React / Node.js / PostgreSQL" : "Next.js / Django / AWS Cloud");
                
                // Upgrade advice
                let upgradeRec = "";
                if (isStarter) {
                    upgradeRec = "Start with Phase 1 MVP to go-to-market quickly. Scale to Professional later.";
                } else if (isPromo) {
                    upgradeRec = "Ideal choice: includes databases, payment APIs, and admin dashboard panels.";
                } else if (isEnterprise) {
                    upgradeRec = "Best for large scale organizations requiring custom AI chatbot and advanced analytics integrations.";
                }

                const card = document.createElement("div");
                card.style.background = isPromo ? "linear-gradient(135deg, #1e293b 0%, #1e3a8a 100%)" : "rgba(255,255,255,0.02)";
                card.style.border = isPromo ? "2px solid #3b82f6" : "1px solid rgba(255,255,255,0.08)";
                card.style.borderRadius = "16px";
                card.style.padding = "25px";
                card.style.display = "flex";
                card.style.flexDirection = "column";
                card.style.gap = "15px";
                card.style.position = "relative";
                card.style.boxShadow = isPromo ? "0 10px 25px rgba(59, 130, 246, 0.2)" : "none";

                card.innerHTML = `
                    <div style="display:flex; flex-direction:column; gap:5px;">
                        <h3 style="font-size:18px; font-weight:600; color:#fff; margin:0;">${pkgName} Package</h3>
                        <div style="display:flex; flex-wrap:wrap; gap:5px; margin-top:5px;">${badgeHTML}</div>
                    </div>
                    
                    <p style="font-size:12px; color:#94a3b8; line-height:1.4; margin:0; height:35px; overflow:hidden;">${pkg.best_for}</p>
                    
                    <div style="border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:15px; display:flex; flex-direction:column; gap:5px;">
                        <div style="font-size:24px; font-weight:700; color:#38bdf8;">₹${pkg.price.toLocaleString()}</div>
                        <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
                            <span>Current Budget: ₹${currentBudget.toLocaleString()}</span>
                            <span style="color:${diffColor}; font-weight:600;">${diffText}</span>
                        </div>
                    </div>
                    
                    <div style="display:flex; flex-direction:column; gap:12px; font-size:12px; color:#e2e8f0; line-height:1.4; flex-grow:1;">
                        <div>
                            <strong style="color:#fff; display:block; margin-bottom:4px; font-size:11px; text-transform:uppercase; color:#34d399;">✔ Included Features</strong>
                            <div style="display:flex; flex-wrap:wrap; gap:4px;">
                                ${incFeatures.map(f => `<span style="background:rgba(16,185,129,0.1); color:#34d399; padding:2px 6px; border-radius:6px; font-size:10px; border:1px solid rgba(16,185,129,0.2);">${f}</span>`).join("")}
                            </div>
                        </div>
                        
                        ${excFeatures.length > 0 ? `
                        <div>
                            <strong style="color:#fff; display:block; margin-bottom:4px; font-size:11px; text-transform:uppercase; color:#f87171;">✖ Excluded Features</strong>
                            <div style="display:flex; flex-wrap:wrap; gap:4px; opacity:0.8;">
                                ${excFeatures.map(f => `<span style="background:rgba(239,68,68,0.1); color:#f87171; padding:2px 6px; border-radius:6px; font-size:10px; border:1px solid rgba(239,68,68,0.2); text-decoration:line-through;">${f}</span>`).join("")}
                            </div>
                        </div>
                        ` : ''}

                        ${unlockedHTML}
                        
                        <div style="border-top:1px solid rgba(255,255,255,0.04); padding-top:8px;">
                            <strong>Timeline:</strong> <span style="color:#fbbf24;">${pkg.timeline}</span>
                        </div>
                        <div>
                            <strong>Technology Stack:</strong> <span style="color:#38bdf8;">${techStack}</span>
                        </div>
                        <div>
                            <strong>Support Tier:</strong> <span>${pkg.support}</span>
                        </div>
                        <div>
                            <strong>Maintenance:</strong> <span>${pkg.maintenance}</span>
                        </div>
                        <div>
                            <strong>Business ROI:</strong> <span style="font-size:11px; color:#94a3b8; display:block; margin-top:2px;">${roiText}</span>
                        </div>
                        
                        <div style="border-top:1px solid rgba(255,255,255,0.04); padding-top:8px; font-size:11px; color:#94a3b8; font-style:italic;">
                            <strong>Upgrade Advice:</strong> ${upgradeRec}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    }

    // 3. AI Scores Panel
    const scoresPanel = document.getElementById("sim-scores-panel");
    if (scoresPanel && simulatedData.scores) {
        scoresPanel.innerHTML = "";
        Object.entries(simulatedData.scores).forEach(([scoreKey, scoreVal]) => {
            const label = scoreKey.replace("_", " ").toUpperCase();
            scoresPanel.innerHTML += `
                <div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px; color:#e2e8f0;">
                        <span>${label}</span>
                        <span style="font-weight:700; color:#34d399;">${scoreVal}%</span>
                    </div>
                    <div style="width:100%; height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                        <div style="width:${scoreVal}%; height:100%; background:linear-gradient(90deg, #10b981 0%, #34d399 100%); border-radius:3px;"></div>
                    </div>
                </div>
            `;
        });
    }

    // 4. Project Health Panel
    const healthPanel = document.getElementById("sim-health-panel");
    if (healthPanel && simulatedData.health) {
        const h = simulatedData.health;
        healthPanel.innerHTML = `
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:12px; color:#e2e8f0;">
                <div><strong>Risk Level:</strong> <span style="padding:2px 8px; border-radius:8px; background:rgba(239,68,68,0.15); color:#f87171; font-weight:700; font-size:10px;">${h.risk_level}</span></div>
                <div><strong>Budget Status:</strong> <span style="color:#34d399; font-weight:700;">${h.budget_health}</span></div>
                <div><strong>Timeline Track:</strong> <span style="color:#fbbf24; font-weight:700;">${h.timeline_health}</span></div>
                <div><strong>Tech Complexity:</strong> <span>${h.technology_health}</span></div>
                <div><strong>Feasibility:</strong> <span style="color:#38bdf8; font-weight:700;">${h.business_feasibility}</span></div>
                <div><strong>Success Probability:</strong> <span style="color:#34d399; font-weight:700;">${h.success_probability}%</span></div>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.04); padding-top:8px; font-size:11px; color:#94a3b8; line-height:1.4;">
                <strong>AI Advisor Risk Assessment:</strong> ${h.risk_reasoning}
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.04); padding-top:8px; font-size:11px; color:#fbbf24; line-height:1.4;">
                <strong>Hosting Recommendation:</strong> ${simulatedData.hosting_recommendation || "-"}
            </div>
        `;
    }

    // 5. Phased Roadmap
    const roadmapTimeline = document.getElementById("sim-roadmap-timeline");
    if (roadmapTimeline && simulatedData.roadmap) {
        roadmapTimeline.innerHTML = "";
        simulatedData.roadmap.forEach((phase, index) => {
            const phaseFeatures = phase.features.length > 0
                ? phase.features.map(f => `<span style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); font-size:10px; color:#cbd5e1; padding:2px 6px; border-radius:6px;">${f}</span>`).join("")
                : `<span style="font-size:11px; color:#64748b;">No extra scope added.</span>`;
                
            roadmapTimeline.innerHTML += `
                <div style="display:flex; gap:20px; align-items:flex-start; position:relative; padding-bottom:10px;">
                    <!-- Line dot connection -->
                    <div style="display:flex; flex-direction:column; align-items:center; min-height:80px;">
                        <span style="width:28px; height:28px; border-radius:50%; background:#1e293b; border:2px solid #a78bfa; color:#a78bfa; display:flex; justify-content:center; align-items:center; font-weight:700; font-size:12px;">${index+1}</span>
                        ${index < 3 ? '<div style="width:2px; flex-grow:1; background:rgba(167,139,250,0.2); margin-top:4px;"></div>' : ''}
                    </div>
                    <!-- Details Card -->
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:12px; flex-grow:1; display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:5px;">
                            <strong style="color:#fff; font-size:14px;">${phase.phase}</strong>
                            <span style="font-size:13px; font-weight:700; color:#a78bfa;">₹${phase.cost.toLocaleString()}</span>
                        </div>
                        <p style="font-size:12px; color:#94a3b8; margin:0; line-height:1.4;">${phase.details}</p>
                        <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:4px;">
                            ${phaseFeatures}
                        </div>
                    </div>
                </div>
            `;
        });
    }

    // 6. Technology comparison
    const techComparePanel = document.getElementById("sim-tech-compare-panel");
    if (techComparePanel && simulatedData.tech_comparison) {
        techComparePanel.innerHTML = "";
        Object.entries(simulatedData.tech_comparison).forEach(([layer, item]) => {
            techComparePanel.innerHTML += `
                <div style="border-bottom:1px solid rgba(255,255,255,0.04); padding-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#fff; margin-bottom:2px;">
                        <span style="text-transform:capitalize; color:#38bdf8;">${layer} Layer</span>
                        <span style="color:#fbbf24;">${item.choice}</span>
                    </div>
                    <p style="font-size:11px; color:#cbd5e1; margin:0 0 3px 0; line-height:1.3;"><strong>Rec:</strong> ${item.recommendation}</p>
                    <p style="font-size:10px; color:#94a3b8; margin:0; line-height:1.3;"><strong>Trade-off:</strong> + ${item.advantages} / - ${item.disadvantages}</p>
                </div>
            `;
        });
    }

    // 7. Team Structure
    const teamPanel = document.getElementById("sim-team-panel");
    if (teamPanel && simulatedData.team) {
        teamPanel.innerHTML = "";
        Object.entries(simulatedData.team).forEach(([role, info]) => {
            const roleLabel = role.replace("_", " ").toUpperCase();
            if (info.count > 0) {
                teamPanel.innerHTML += `
                    <div style="display:flex; gap:10px; font-size:12px; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:6px;">
                        <div style="background:rgba(245,158,11,0.1); color:#f59e0b; width:22px; height:22px; border-radius:6px; display:flex; justify-content:center; align-items:center; font-weight:700; font-size:10px;">${info.count}</div>
                        <div style="flex-grow:1;">
                            <strong style="color:#fff; display:block; font-size:11px;">${roleLabel}</strong>
                            <span style="font-size:10px; color:#94a3b8; display:block; line-height:1.3;">${info.reason}</span>
                        </div>
                    </div>
                `;
            }
        });
    }

    // 8. Milestone Cost Breakdown Table
    const costBreakdownContainer = document.getElementById("sim-cost-breakdown-container");
    if (costBreakdownContainer && simulatedData.cost_breakdown) {
        const b = simulatedData.cost_breakdown;
        costBreakdownContainer.innerHTML = `
            <table style="width:100%; border-collapse:collapse; font-size:12px; color:#cbd5e1; text-align:left;">
                <thead>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.08); color:#fff; font-weight:600;">
                        <th style="padding:10px;">Milestone Phase</th>
                        <th style="padding:10px; text-align:right;">Cost (INR)</th>
                        <th style="padding:10px; text-align:right;">Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Planning & Consultation</td>
                        <td style="padding:10px; text-align:right;">₹${b.planning.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">5%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Requirement Analysis & Architecture</td>
                        <td style="padding:10px; text-align:right;">₹${b.requirement_analysis.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">5%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">UI/UX Design</td>
                        <td style="padding:10px; text-align:right;">₹${b.ui_design.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">10%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Frontend Implementation</td>
                        <td style="padding:10px; text-align:right;">₹${b.frontend.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">20%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Backend Engineering & API Setup</td>
                        <td style="padding:10px; text-align:right;">₹${b.backend.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">25%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Database Design & Security Integration</td>
                        <td style="padding:10px; text-align:right;">₹${b.database.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">10%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Integration Testing & QA</td>
                        <td style="padding:10px; text-align:right;">₹${b.testing.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">10%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Deployment & Cloud Server Setup</td>
                        <td style="padding:10px; text-align:right;">₹${b.deployment.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">5%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:10px;">Annual Maintenance (Pre-funded)</td>
                        <td style="padding:10px; text-align:right;">₹${b.maintenance.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">10%</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.06); color:#a78bfa;">
                        <td style="padding:10px;">Applicable Taxes & GST (18%)</td>
                        <td style="padding:10px; text-align:right;">₹${b.taxes.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">18%</td>
                    </tr>
                    <tr style="font-weight:700; color:#fff; font-size:13px;">
                        <td style="padding:10px;">GRAND TOTAL ESTIMATE</td>
                        <td style="padding:10px; text-align:right; color:#38bdf8;">₹${b.total.toLocaleString()}</td>
                        <td style="padding:10px; text-align:right;">100%</td>
                    </tr>
                </tbody>
            </table>
        `;
    }
}

function closeComparisonModal() {
    const modal = document.getElementById("comparison-modal");
    if (modal) modal.style.display = "none";
}

// ==========================================
// WINDOW LOAD ENTRY
// ==========================================

window.addEventListener("load", function () {
    startConversation();
    loadSidebarChats();
    initBudgetSimulator();
});