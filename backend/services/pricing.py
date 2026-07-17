"""
==================================================
TechSoul AI
Pricing Service
==================================================

Calculates project quotations including base price,
feature price, timeline multiplier, taxes, and maintenance.
"""

import json
import os
from backend.config import PRICING_DATABASE


class PricingService:
    """
    Handles all pricing calculations for projects and features.
    """

    def __init__(self):
        """
        Initialize PricingService and load pricing configuration.
        """
        self.data = self.load_pricing_data()

    # ==========================================
    # LOAD JSON
    # ==========================================

    def load_pricing_data(self):
        """
        Load pricing.json database.

        Returns
        -------
        dict
            Dictionary containing project and feature pricing config.
        """
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(
            current_dir,
            "..",
            "..",
            "data",
            "pricing.json"
        )
        json_path = os.path.abspath(json_path)

        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    # ==========================================
    # PROJECT PRICE
    # ==========================================

    def get_project_price(self, project):
        """
        Return project base price.

        Parameters
        ----------
        project : str
            Name of the project.

        Returns
        -------
        int
            Base price of the project.
        """
        project_data = self.data["projects"].get(project)
        if project_data:
            return project_data["price"]
        return 0

    # ==========================================
    # FEATURE PRICE
    # ==========================================

    def get_feature_price(self, feature):
        """
        Return single feature price.

        Parameters
        ----------
        feature : str
            Name of the feature.

        Returns
        -------
        int
            Price of the feature.
        """
        feature_data = self.data["features"].get(feature)
        if feature_data:
            return feature_data["price"]
        return 0

    # ==========================================
    # TIMELINE MULTIPLIER
    # ==========================================

    def get_timeline_multiplier(self, timeline):
        """
        Return timeline multiplier.

        Parameters
        ----------
        timeline : str
            timeline option (Normal, Fast, Urgent).

        Returns
        -------
        float
            Price multiplier for the timeline.
        """
        timeline_data = self.data["timeline"].get(timeline)
        if timeline_data:
            return timeline_data["multiplier"]
        return 1.0

    # ==========================================
    # TOTAL FEATURE PRICE
    # ==========================================

    def calculate_feature_total(self, features):
        """
        Calculate total feature cost.

        Parameters
        ----------
        features : list
            List of feature names.

        Returns
        -------
        int
            Total price of all features.
        """
        total = 0
        for feature in features:
            total += self.get_feature_price(feature)
        return total

    # ==========================================
    # CALCULATE QUOTATION
    # ==========================================

    def calculate(
        self,
        project,
        features,
        timeline
    ):
        """
        Calculate full quotation detail including taxes, maintenance and discount.

        Parameters
        ----------
        project : str
            Name of the project.
        features : list
            List of features.
        timeline : str
            Project timeline.

        Returns
        -------
        dict
            Structured pricing breakdown.
        """
        project_price = self.get_project_price(project)
        feature_price = self.calculate_feature_total(features)
        subtotal = project_price + feature_price
        multiplier = self.get_timeline_multiplier(timeline)
        
        # Subtotal adjusted by timeline
        timeline_price = round(subtotal * multiplier)

        # Standard GST is 18%
        taxes = round(timeline_price * 0.18)

        # Annual maintenance is 10%
        maintenance = round(timeline_price * 0.10)

        # Discount is 0 by default (budget optimization handles scoping)
        discount = 0

        # Final price includes base, features, timeline multiplier, taxes, maintenance
        total = timeline_price - discount + taxes + maintenance

        res = {
            "project": project,
            "project_price": project_price,
            "features": features,
            "feature_price": feature_price,
            "subtotal": subtotal,
            "timeline": timeline,
            "multiplier": multiplier,
            "discount": discount,
            "taxes": taxes,
            "maintenance": maintenance,
            "total": total
        }
        res["cost_breakdown"] = self.get_cost_breakdown(res)
        return res

    # ==========================================
    # GET COST BREAKDOWN
    # ==========================================

    def get_cost_breakdown(self, quotation):
        """
        Generate detailed cost breakdown for the quotation.
        """
        project_price = quotation.get("project_price", 0)
        multiplier = quotation.get("multiplier", 1.0)
        
        # Divide project base price into core execution layers (adjusted by timeline multiplier)
        ui_design = round(project_price * 0.20 * multiplier)
        backend = round(project_price * 0.40 * multiplier)
        database = round(project_price * 0.15 * multiplier)
        testing = round(project_price * 0.15 * multiplier)
        deployment = round(project_price * 0.10 * multiplier)
        
        breakdown = [
            {"item": "UI/UX Design & Wireframing", "amount": ui_design},
            {"item": "Backend Architecture & API Development", "amount": backend},
            {"item": "Database Design & Security Configuration", "amount": database},
        ]
        
        # Features breakdown
        features = quotation.get("features", [])
        for f in features:
            f_price = self.get_feature_price(f)
            # Adjust feature price by timeline multiplier too
            f_amt = round(f_price * multiplier)
            breakdown.append({"item": f"{f} Feature Development", "amount": f_amt})
            
        breakdown.extend([
            {"item": "Quality Assurance & Automated Testing", "amount": testing},
            {"item": "Production Server Setup & Cloud Deployment", "amount": deployment},
            {"item": "Annual Server Support & Maintenance (10%)", "amount": quotation.get("maintenance", 0)},
            {"item": "Government Taxes & GST (18%)", "amount": quotation.get("taxes", 0)}
        ])
        
        return breakdown

    # ==========================================
    # PARSE BUDGET
    # ==========================================

    def parse_budget(self, budget):
        """
        Convert budget string/number to integer.

        Parameters
        ----------
        budget : str or int
            Estimated budget input.

        Returns
        -------
        int
            Cleaned integer budget.
        """
        if isinstance(budget, (int, float)):
            return int(budget)

        budget_str = str(budget).lower().replace(",", "").replace("₹", "").replace("$", "").strip()

        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(k|lakh|lacs|lac|thousand|m|million)?', budget_str)
        if match:
            val = float(match.group(1))
            suffix = match.group(2)
            if suffix in ['k', 'thousand']:
                val *= 1000
            elif suffix in ['lakh', 'lacs', 'lac']:
                val *= 100000
            elif suffix in ['m', 'million']:
                val *= 1000000
            return int(val)

        if budget_str.isdigit():
            return int(budget_str)
        return 0

    # ==========================================
    # FEATURE PRIORITY
    # ==========================================

    def get_feature_priority(self, feature):
        """
        Return feature priority.

        Parameters
        ----------
        feature : str
            Name of the feature.

        Returns
        -------
        int
            Priority score.
        """
        feature_data = self.data["features"].get(feature)
        if feature_data:
            return feature_data["priority"]
        return 0

    # ==========================================
    # OPTIMIZE FEATURES
    # ==========================================

    def optimize_features(
        self,
        project,
        features,
        budget,
        timeline
    ):
        """
        Optimize selected features according to budget.

        Parameters
        ----------
        project : str
            Name of the project.
        features : list
            List of features.
        budget : str or int
            Estimated budget.
        timeline : str
            Project timeline.

        Returns
        -------
        dict
            Optimized quotation.
        """
        budget_val = self.parse_budget(budget)
        
        # If budget is 0 or unassigned, return base calculation
        if budget_val == 0:
            quotation = self.calculate(project, features, timeline)
            quotation["status"] = "within_budget"
            quotation["removed_features"] = []
            return quotation

        quotation = self.calculate(project, features, timeline)

        if quotation["total"] <= budget_val:
            quotation["status"] = "within_budget"
            quotation["removed_features"] = []
            quotation["budget"] = budget_val
            quotation["remaining_budget"] = budget_val - quotation["total"]
            return quotation

        # If too expensive, start dropping low priority features
        optimized = features.copy()
        removed = []

        # Sort features ascending by priority (lowest priority first)
        optimized.sort(key=self.get_feature_priority)

        while optimized:
            quotation = self.calculate(project, optimized, timeline)
            if quotation["total"] <= budget_val:
                break

            removed_feature = optimized.pop(0)
            removed.append(removed_feature)

        # Recalculate with final set of optimized features
        quotation = self.calculate(project, optimized, timeline)
        quotation["status"] = "optimized"
        quotation["removed_features"] = removed
        quotation["budget"] = budget_val
        quotation["remaining_budget"] = budget_val - quotation["total"]

        return quotation

    # ==========================================
    # RECOMMEND UPGRADES
    # ==========================================

    def recommend_upgrades(
        self,
        project,
        selected_features,
        remaining_budget
    ):
        """
        Recommend extra features within remaining budget.

        Parameters
        ----------
        project : str
            Name of the project.
        selected_features : list
            Currently selected features.
        remaining_budget : int
            Leftover budget.

        Returns
        -------
        list
            Recommended upsell items.
        """
        recommendations = []
        upsell_list = self.data["upsell"].get(project, [])

        for feature in upsell_list:
            if feature in selected_features:
                continue

            feature_price = self.get_feature_price(feature)
            # Factor taxes and maintenance (approx 28% overhead) into the budget limit
            estimated_cost_with_overhead = feature_price * 1.28

            if estimated_cost_with_overhead <= remaining_budget:
                recommendations.append({
                    "feature": feature,
                    "price": feature_price
                })
                remaining_budget -= estimated_cost_with_overhead

        return recommendations

    # ==========================================
    # FINAL QUOTATION
    # ==========================================

    def generate_final_quote(
        self,
        project,
        features,
        budget,
        timeline
    ):
        """
        Generate complete quotation.

        Parameters
        ----------
        project : str
            Name of the project.
        features : list
            Selected features.
        budget : str or int
            Budget constraint.
        timeline : str
            Timeline speed.

        Returns
        -------
        dict
            Final detailed quotation structure.
        """
        quotation = self.optimize_features(
            project,
            features,
            budget,
            timeline
        )

        quotation["recommended_upgrades"] = self.recommend_upgrades(
            project,
            quotation["features"],
            quotation.get("remaining_budget", 0)
        )

        return quotation

    # ==========================================
    # BUDGET SIMULATION ENGINE
    # ==========================================

    def simulate_budget(self, project, budget, timeline="Normal", chat_context=None):
        """
        Simulate recommendations based on a dynamic budget value and chat context.
        """
        parsed_budget = self.parse_budget(budget)
        if parsed_budget <= 0:
            parsed_budget = 50000

        project_price = self.get_project_price(project)
        if not project_price:
            project_price = 40000

        # Fetch all available features and sort by priority desc, price asc
        all_features = []
        for name, details in self.data["features"].items():
            all_features.append({
                "name": name,
                "price": details.get("price", 10000),
                "priority": details.get("priority", 5)
            })
        all_features.sort(key=lambda x: (-x["priority"], x["price"]))

        # Determine MVP vs standard base price
        minimum_standard_cost = round((project_price) * self.get_timeline_multiplier(timeline) * 1.28)
        is_mvp = parsed_budget < minimum_standard_cost
        
        active_base = round(project_price * 0.6) if is_mvp else project_price
        
        # Helper to calculate final quote total
        def get_total_for_features(feats, base_override=None):
            feat_sum = sum(self.get_feature_price(f) for f in feats)
            sub = (base_override if base_override is not None else project_price) + feat_sum
            tim_total = round(sub * self.get_timeline_multiplier(timeline))
            taxes = round(tim_total * 0.18)
            maint = round(tim_total * 0.10)
            return tim_total + taxes + maint

        # Find which features fit the budget
        included_features = []
        excluded_features = []
        
        for f in all_features:
            test_feats = included_features + [f["name"]]
            test_total = get_total_for_features(test_feats, active_base)
            if test_total <= parsed_budget:
                included_features.append(f["name"])
            else:
                excluded_features.append(f["name"])

        # Timeline calculation
        days_base = 5 if is_mvp else 15
        days_features = len(included_features) * 2
        total_days = days_base + days_features

        # Tech stack selection
        if parsed_budget < 60000:
            tech_stack = "WordPress / PHP / SQLite / TailWind CSS"
            best_for = "Startups / Landing Pages"
        elif parsed_budget <= 150000:
            tech_stack = "React / Node.js / PostgreSQL / Express"
            best_for = "Growing Businesses / Standard SaaS"
        else:
            tech_stack = "Next.js / Python Django / PostgreSQL / AWS Cloud / Docker"
            best_for = "Enterprises / Scale & High Security"

        # Categorize features
        essential_list = []
        recommended_list = []
        future_list = []
        for f in all_features:
            if f["priority"] >= 9:
                essential_list.append(f["name"])
            elif f["priority"] >= 5:
                recommended_list.append(f["name"])
            else:
                future_list.append(f["name"])

        # Phase Roadmap
        p1_feats = [f for f in included_features if f in essential_list]
        p1_cost = get_total_for_features(p1_feats, active_base)

        p2_feats = list(set(p1_feats + [f for f in included_features if f in recommended_list]))
        p2_cost = get_total_for_features(p2_feats, project_price)

        p3_feats = included_features
        p3_cost = get_total_for_features(p3_feats, project_price)

        p4_feats = list(set(included_features + future_list[:3]))
        p4_cost = get_total_for_features(p4_feats, project_price)

        # ROI & Business Benefits
        if parsed_budget < 60000:
            roi_statement = f"Phase 1 establishes your online visibility, securing customer trust and generating inbound leads at minimal cost."
            ops_savings = "Reduces manual customer inquiries by 30% via automated contact forms."
        elif parsed_budget <= 150000:
            roi_statement = f"Phase 2 integrates payments and user dashboards, automating manual operations and increasing cart conversion by 20%."
            ops_savings = "Saves 10+ hours per week of manual booking/payment reconciliation."
        else:
            roi_statement = f"Phase 3 unlocks data-driven marketing, multi-language support, and analytics, driving customer acquisition up to 35%."
            ops_savings = "Replaces 2 manual admin headcount using AI chatbot and automated billing."

        # Package Comparison
        packages = {
            "Starter": {
                "price": get_total_for_features(essential_list[:2], active_base),
                "features": essential_list[:2],
                "timeline": f"{days_base} Days",
                "support": "Email Support",
                "maintenance": "Basic Updates",
                "best_for": "Testing market validation (MVP)"
            },
            "Professional": {
                "price": get_total_for_features([f for f in essential_list + recommended_list if f in included_features or len(included_features) < 3], project_price),
                "features": [f for f in essential_list + recommended_list if f in included_features][:4],
                "timeline": f"{max(total_days, 15)} Days",
                "support": "Priority Chat Support",
                "maintenance": "Monthly Health & Backups",
                "best_for": "Fully functional SaaS / E-Commerce"
            },
            "Enterprise": {
                "price": get_total_for_features([f["name"] for f in all_features[:10]], project_price),
                "features": [f["name"] for f in all_features[:8]],
                "timeline": "45 Days",
                "support": "24/7 Phone & Dedicated Manager",
                "maintenance": "Weekly Audits & SLA Guarantee",
                "best_for": "Scaling platforms with custom requirements"
            }
        }

        # Recommendations for Options 1, 2, and 3
        opt1_feats = included_features
        opt1_price = get_total_for_features(opt1_feats, active_base)

        opt2_feats = list(set(included_features + [f["name"] for f in all_features if f["name"] not in included_features][:2]))
        opt2_price = get_total_for_features(opt2_feats, project_price)

        opt3_feats = [f["name"] for f in all_features]
        opt3_price = get_total_for_features(opt3_feats, project_price)

        # Cost Breakdown calculations based on opt2_price (Recommended option)
        estimated_project_cost = opt2_price
        budget_gap = estimated_project_cost - parsed_budget

        planning = round(estimated_project_cost * 0.05)
        analysis_cost = round(estimated_project_cost * 0.05)
        ui_design = round(estimated_project_cost * 0.10)
        frontend = round(estimated_project_cost * 0.20)
        backend = round(estimated_project_cost * 0.25)
        database = round(estimated_project_cost * 0.10)
        qa = round(estimated_project_cost * 0.10)
        deployment = round(estimated_project_cost * 0.05)

        core_cost = planning + analysis_cost + ui_design + frontend + backend + database + qa + deployment
        taxes_cost = round(core_cost * 0.18)
        maintenance_cost = round(core_cost * 0.10)
        grand_total = core_cost + taxes_cost + maintenance_cost

        # Call Gemini AI simulation advisor
        ai_analysis = None
        try:
            from backend.services.gemini_service import GeminiService
            gemini_svc = GeminiService()
            ai_analysis = gemini_svc.generate_simulation_analysis(chat_context, parsed_budget, project)
        except Exception as e:
            print(f"Gemini simulator analysis exception: {e}")

        res = {
            "budget": parsed_budget,
            "project": project,
            "timeline": f"{total_days} Days",
            "tech_stack": tech_stack,
            "best_for": best_for,
            "features_included": included_features,
            "features_excluded": excluded_features,
            "categories": {
                "essential": essential_list,
                "recommended": recommended_list,
                "future": future_list
            },
            "options": {
                "option1": {
                    "title": "Solution Within Budget (MVP)",
                    "price": opt1_price,
                    "features": opt1_feats,
                    "timeline": f"{total_days} Days",
                    "explanation": "Prioritizes high-value features to launch fast within your specific budget limit."
                },
                "option2": {
                    "title": "Recommended Solution",
                    "price": opt2_price,
                    "features": opt2_feats,
                    "timeline": f"{total_days + 6} Days",
                    "explanation": "Includes essential database and integration upgrades to unlock standard business automation."
                },
                "option3": {
                    "title": "Ideal Solution",
                    "price": opt3_price,
                    "features": opt3_feats,
                    "timeline": "45 Days",
                    "explanation": "The ultimate scalable product covering all possible features with enterprise-grade cloud hosting."
                }
            },
            "roadmap": [
                {"phase": "Phase 1: Launch Core", "cost": p1_cost, "features": p1_feats, "details": "Minimal Viable Product focusing on registration and core screens."},
                {"phase": "Phase 2: Add Automation", "cost": p2_cost, "features": p2_feats, "details": "Brings CMS dashboards, emails, and payment collections."},
                {"phase": "Phase 3: Deep Insights", "cost": p3_cost, "features": p3_feats, "details": "Full product sync with report logs, notifications, and analytics."},
                {"phase": "Phase 4: Scale & AI", "cost": p4_cost, "features": p4_feats, "details": "Optimizes conversions via AI chatbot and customized cloud integrations."}
            ],
            "roi": {
                "roi_statement": roi_statement,
                "ops_savings": ops_savings,
                "scalability": "Built using standardized modular architecture for simple future upgrades."
            },
            "packages": packages,
            
            # Augmented calculations
            "estimated_project_cost": grand_total,
            "budget_gap": budget_gap,
            "maintenance_cost": maintenance_cost,
            "cost_breakdown": {
                "planning": planning,
                "requirement_analysis": analysis_cost,
                "ui_design": ui_design,
                "frontend": frontend,
                "backend": backend,
                "database": database,
                "testing": qa,
                "deployment": deployment,
                "maintenance": maintenance_cost,
                "taxes": taxes_cost,
                "total": grand_total
            }
        }

        # Merge AI analysis parameters
        if ai_analysis:
            res.update({
                "complexity": ai_analysis.get("complexity", "Medium"),
                "complexity_reasoning": ai_analysis.get("complexity_reasoning", ""),
                "scores": ai_analysis.get("scores", {}),
                "health": ai_analysis.get("health", {}),
                "team": ai_analysis.get("team", {}),
                "tech_comparison": ai_analysis.get("tech_comparison", {}),
                "roi_analysis": ai_analysis.get("roi_analysis", {}),
                "hosting_recommendation": ai_analysis.get("hosting_recommendation", ""),
                "negotiation_advice": ai_analysis.get("negotiation_advice", [])
            })
        else:
            # Fallback layout details
            res.update({
                "complexity": "Medium",
                "complexity_reasoning": f"Calculated as Medium for {project} based on typical features.",
                "scores": {
                    "business_match": 80,
                    "budget_match": 85,
                    "security": 75,
                    "scalability": 70,
                    "maintainability": 80,
                    "future_growth": 75,
                    "roi": 85,
                    "overall_score": 79
                },
                "health": {
                    "risk_level": "Medium",
                    "risk_reasoning": "Standard launch constraints.",
                    "budget_health": "Healthy",
                    "timeline_health": "On Track",
                    "technology_health": "Standard",
                    "business_feasibility": "High",
                    "success_probability": 80
                },
                "team": {
                    "project_manager": { "count": 1, "reason": "Manages core sprint plans." },
                    "ui_designer": { "count": 1, "reason": "Designs visual wireframes." },
                    "frontend_developer": { "count": 1, "reason": "Builds layouts." },
                    "backend_developer": { "count": 1, "reason": "Builds database APIs." },
                    "qa_engineer": { "count": 1, "reason": "Verifies correct behavior." },
                    "ai_engineer": { "count": 0, "reason": "Not strictly required for Phase 1." },
                    "devops_engineer": { "count": 0, "reason": "Handled within developer scope." }
                },
                "tech_comparison": {
                    "frontend": { "choice": "React vs Angular", "advantages": "React is simple.", "disadvantages": "Angular is complex.", "recommendation": "React recommended." },
                    "backend": { "choice": "Flask vs FastAPI", "advantages": "FastAPI is faster.", "disadvantages": "Flask is simpler.", "recommendation": "Flask recommended." },
                    "database": { "choice": "MongoDB vs PostgreSQL", "advantages": "PostgreSQL is ACID compliant.", "disadvantages": "MongoDB is NoSQL.", "recommendation": "PostgreSQL recommended." },
                    "cloud": { "choice": "AWS vs Azure", "advantages": "AWS is popular.", "disadvantages": "Azure is complex.", "recommendation": "AWS recommended." }
                },
                "roi_analysis": {
                    "revenue_increase": "15% Est. Increase",
                    "time_saved": "10 Hours/Week",
                    "automation_benefits": "Reduced support load.",
                    "customer_growth": "10% Growth",
                    "estimated_roi": "120%",
                    "payback_period": "6 Months"
                },
                "hosting_recommendation": "Heroku or DigitalOcean VPS.",
                "negotiation_advice": [
                    "What fits: Basic SaaS layout and admin dashboards.",
                    "What can wait: Auto-backups and multi-tenant scaling.",
                    "Next investment recommendation: Optimize basic user signup rate."
                ]
            })

        return res