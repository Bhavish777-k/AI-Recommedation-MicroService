# services/roadmap_service.py
from typing import List, Dict
from bson import ObjectId
from config.database import db
from config.role_requirements import ROLE_REQUIREMENTS
from config.ai_client import ai_client

async def fetch_user(user_id: str):
    try:
        return await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

async def fetch_skills_by_ids(skill_ids: List[str]) -> List[Dict]:
    obj_ids = []
    for sid in skill_ids:
        try:
            obj_ids.append(ObjectId(sid))
        except Exception:
            continue
    if not obj_ids:
        return []
    skills = []
    cursor = db.skills.find({"_id": {"$in": obj_ids}})
    async for s in cursor:
        skills.append({
            "id": str(s["_id"]),
            "name": s.get("name", "").strip(),
            "category": s.get("category", "uncategorized"),
            "points": int(s.get("points", 0) or 0)
        })
    return skills

async def build_skill_name_map() -> Dict[str, Dict]:
    mapping = {}
    cursor = db.skills.find({})
    async for s in cursor:
        name = s.get("name", "").strip()
        if name:
            mapping[name] = {
                "id": str(s["_id"]),
                "name": name,
                "category": s.get("category", "uncategorized"),
                "points": int(s.get("points", 0) or 0)
            }
    return mapping

def filter_role_requirements(role: str, skill_name_map: Dict[str, Dict]) -> List[str]:
    required = ROLE_REQUIREMENTS.get(role, [])
    return [r for r in required if r in skill_name_map]

def enrich_missing(missing_names: List[str], skill_name_map: Dict[str, Dict]) -> List[Dict]:
    enriched = []
    for name in missing_names:
        doc = skill_name_map.get(name)
        if doc:
            enriched.append({
                "id": doc["id"],
                "name": doc["name"],
                "category": doc.get("category", "uncategorized"),
                "points": doc.get("points", 0)
            })
    return enriched

def group_and_sort(skills: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    for s in skills:
        cat = s.get("category", "uncategorized")
        grouped.setdefault(cat, []).append(s)
    for cat, items in grouped.items():
        items.sort(key=lambda x: x.get("points", 0), reverse=True)
    return grouped

def build_prompt(role: str, offered: List[Dict], missing_grouped: Dict[str, List[Dict]]) -> str:
    offered_lines = "\n".join([f"- {s['name']} (category: {s['category']}, points: {s['points']})" for s in offered]) or "None"
    missing_lines = []
    for cat, items in missing_grouped.items():
        missing_lines.append(f"Category: {cat}")
        for it in items:
            missing_lines.append(f"  - {it['name']} (points: {it['points']})")
    missing_text = "\n".join(missing_lines) or "None"

    prompt = f"""
You are an expert learning-path generator.

Target role: {role}

User current skills:
{offered_lines}

Missing skills grouped by category and ordered by weight:
{missing_text}

Task:
1) Produce a step-by-step learning roadmap for the user to acquire the missing skills.
2) For each missing skill, include recommended resources, estimated time, and priority based on points weight.
3) Provide a 12-week suggested schedule with milestones and checkpoints.

Return the roadmap in numbered sections and include short rationale for priorities.
"""
    return prompt

async def generate_roadmap_for_user(user_id: str, target_role: str, model: str = "gemini-flash-latest"):
    user = await fetch_user(user_id)
    if not user:
        return {"error": "User not found"}

    offered_ids = user.get("skillsOffered", []) or []
    if not offered_ids:
        return {"error": "User has no recorded skills", "currentSkills": []}

    offered_skill_docs = await fetch_skills_by_ids(offered_ids)
    skill_name_map = await build_skill_name_map()

    # Filter role requirements to only those present in DB
    filtered_required = filter_role_requirements(target_role, skill_name_map)
    if not filtered_required:
        return {"error": "Role not found or no matching skills in DB"}

    offered_names = {s["name"] for s in offered_skill_docs}
    missing_names = [r for r in filtered_required if r not in offered_names]

    missing_enriched = enrich_missing(missing_names, skill_name_map)
    missing_grouped = group_and_sort(missing_enriched)

    prompt = build_prompt(target_role, offered_skill_docs, missing_grouped)

    try:
        ai_resp = ai_client.generate(prompt=prompt, model=model)
        ai_text = ai_resp.get("text", "")
    except Exception as e:
        ai_text = f"AI generation failed: {str(e)}"

    return {
        "role": target_role,
        "currentSkills": offered_skill_docs,
        "missingSkills": missing_enriched,
        "missingByCategory": missing_grouped,
        "promptSent": prompt,
        "aiRawResponse": ai_text
    }
