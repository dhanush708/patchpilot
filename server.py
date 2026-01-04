from flask import Flask, render_template, request
import uuid
import os
import shutil
from fix_engine import run_fix_engine

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

BASE_DIR = os.getcwd()
WORKDIR = os.path.join(BASE_DIR, "workdir")
UPLOADS = os.path.join(BASE_DIR, "uploads")

os.makedirs(WORKDIR, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_patchpilot():
    file = request.files.get("repo")

    if not file or not file.filename.endswith(".zip"):
        return render_template("result.html", result={
            "status": "ERROR",
            "summary": "Invalid or missing .zip file",
            "stdout": "",
            "output_path": None
        })

    run_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOADS, f"{run_id}.zip")
    extract_path = os.path.join(WORKDIR, run_id)

    file.save(upload_path)
    shutil.unpack_archive(upload_path, extract_path)

    result = run_fix_engine(extract_path)

    return render_template("result.html", result={
        "status": result.status,
        "summary": result.summary,
        "stdout": result.stdout,
        "output_path": result.output_path
    })


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
