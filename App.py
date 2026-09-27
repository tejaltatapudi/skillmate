
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "skill_matching_demo_secret"


# -----------------------------
# WORKER PROFILES
# -----------------------------

workers = {
    1: {
        "name": "Sita Devi",
        "skills": [
            "hand block printing",
            "textile printing",
            "traditional crafts"
        ],
        "location": "Jaipur, India"
    },

    2: {
        "name": "Meena Kumari",
        "skills": [
            "tailoring",
            "garment stitching",
            "embroidery"
        ],
        "location": "Jaipur, India"
    },

    3: {
        "name": "Anjali Sharma",
        "skills": [
            "graphic design",
            "digital illustration",
            "social media design"
        ],
        "location": "Jaipur, India"
    }
}


# -----------------------------
# TASK LIST
# -----------------------------

tasks = [
    {
        "id": 1,
        "title": "Create hand block printed tote bags",
        "description": "Print traditional patterns on cotton tote bags.",
        "skill": "hand block printing",
        "category": "textile",
        "pay": 800,
        "location": "Jaipur, India"
    },

    {
        "id": 2,
        "title": "Print traditional floral fabric",
        "description": "Create floral designs on fabric using traditional printing techniques.",
        "skill": "textile printing",
        "category": "textile",
        "pay": 1000,
        "location": "Jaipur, India"
    },

    {
        "id": 3,
        "title": "Design digital social media posters",
        "description": "Create promotional posters for a local handicraft business.",
        "skill": "graphic design",
        "category": "design",
        "pay": 500,
        "location": "Jaipur, India"
    },

    {
        "id": 4,
        "title": "Stitch traditional garments",
        "description": "Stitch garments for a local clothing business.",
        "skill": "garment stitching",
        "category": "tailoring",
        "pay": 900,
        "location": "Jaipur, India"
    },

    {
        "id": 5,
        "title": "Create embroidered cushion covers",
        "description": "Add traditional embroidery to decorative cushion covers.",
        "skill": "embroidery",
        "category": "textile",
        "pay": 700,
        "location": "Jaipur, India"
    }
]


# -----------------------------
# APPLICATION STORAGE
# -----------------------------

applications = []


# -----------------------------
# SKILL MATCHING FUNCTION
# -----------------------------

def find_matching_tasks(worker):
    matching_tasks = []

    worker_skills = [
        skill.strip().lower()
        for skill in worker["skills"]
    ]

    for task in tasks:
        task_copy = task.copy()

        required_skill = task["skill"].strip().lower()

        task_copy["matched"] = (
            required_skill in worker_skills
        )

        matching_tasks.append(task_copy)

    return matching_tasks


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def home():
    worker_id = request.args.get("worker_id", default=1, type=int)

    # Check if worker exists
    if worker_id not in workers:
        worker_id = 1

    worker = workers[worker_id]

    all_tasks = find_matching_tasks(worker)

    matching_tasks = [
        task for task in all_tasks
        if task["matched"]
    ]

    unmatched_tasks = [
        task for task in all_tasks
        if not task["matched"]
    ]

    return render_template(
        "index.html.txt",
        worker=worker,
        workers=workers,
        worker_id=worker_id,
        tasks=all_tasks,
        matching_tasks=matching_tasks,
        unmatched_tasks=unmatched_tasks,
        match_count=len(matching_tasks),
        total_tasks=len(tasks),
        applications=applications
    )


# -----------------------------
# APPLY FOR A TASK
# -----------------------------

@app.route("/apply/<int:task_id>", methods=["POST"])
def apply(task_id):
    worker_id = request.form.get(
        "worker_id", default=1, type=int
    )

    # Validate worker
    if worker_id not in workers:
        flash("Invalid worker profile.")
        return redirect(url_for("home"))

    worker = workers[worker_id]

    # Find task
    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if task is None:
        flash("Task not found.")
        return redirect(
            url_for("home", worker_id=worker_id)
        )

    # Recheck skills on the server
    matching_tasks = find_matching_tasks(worker)

    matched_task = next(
        (
            item for item in matching_tasks
            if item["id"] == task_id
        ),
        None
    )

    if not matched_task or not matched_task["matched"]:
        flash(
            "Application rejected. Your skills do not match this task."
        )

        return redirect(
            url_for("home", worker_id=worker_id)
        )

    # Prevent duplicate applications
    already_applied = any(
        application["worker_id"] == worker_id
        and application["task_id"] == task_id
        for application in applications
    )

    if already_applied:
        flash("You have already applied for this task.")

        return redirect(
            url_for("home", worker_id=worker_id)
        )

    # Save application
    applications.append({
        "worker_id": worker_id,
        "worker_name": worker["name"],
        "task_id": task_id,
        "task_title": task["title"]
    })

    flash(
        f"Successfully applied for: {task['title']}"
    )

    return redirect(
        url_for("home", worker_id=worker_id)
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )