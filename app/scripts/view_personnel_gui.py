
import sys
from pathlib import Path

# Add the backend directory to Python's import path.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

import tkinter as tk
from tkinter import ttk, messagebox

from sqlalchemy import select

from app.database.connections import SessionLocal
from app.models.organisations import Organization
from app.models.personnel import Personnel


def load_records():
    try:
        with SessionLocal() as db:
            organizations = db.scalars(
                select(Organization)
            ).all()

            personnel_records = db.scalars(
                select(Personnel)
            ).all()

            organization_names = {
                str(org.id): org.organization_code
                for org in organizations
            }

            for org in organizations:
                organization_tree.insert(
                    "",
                    "end",
                    values=(
                        org.organization_code,
                        str(org.id),
                    ),
                )

            for person in personnel_records:
                personnel_tree.insert(
                    "",
                    "end",
                    values=(
                        person.personnel_code,
                        person.full_name,
                        person.role,
                        organization_names.get(
                            str(person.organization_id),
                            "Unknown",
                        ),
                        "Active" if person.is_active else "Inactive",
                    ),
                )

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            f"Could not load records:\n{error}",
        )


root = tk.Tk()
root.title("Digi-CoC Existing Database Records")
root.geometry("900x550")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

organization_frame = ttk.Frame(notebook)
personnel_frame = ttk.Frame(notebook)

notebook.add(
    organization_frame,
    text="Organizations",
)

notebook.add(
    personnel_frame,
    text="Personnel",
)

organization_tree = ttk.Treeview(
    organization_frame,
    columns=("code", "id"),
    show="headings",
)

organization_tree.heading(
    "code",
    text="Organization Code",
)

organization_tree.heading(
    "id",
    text="Organization ID",
)

organization_tree.column("code", width=200)
organization_tree.column("id", width=550)

organization_tree.pack(
    fill="both",
    expand=True,
)

personnel_tree = ttk.Treeview(
    personnel_frame,
    columns=(
        "code",
        "name",
        "role",
        "organization",
        "status",
    ),
    show="headings",
)

personnel_tree.heading("code", text="Personnel Code")
personnel_tree.heading("name", text="Full Name")
personnel_tree.heading("role", text="Role")
personnel_tree.heading("organization", text="Organization")
personnel_tree.heading("status", text="Status")

personnel_tree.column("code", width=120)
personnel_tree.column("name", width=200)
personnel_tree.column("role", width=130)
personnel_tree.column("organization", width=150)
personnel_tree.column("status", width=100)

personnel_tree.pack(
    fill="both",
    expand=True,
)

load_records()

root.mainloop()
