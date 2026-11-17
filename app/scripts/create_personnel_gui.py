

import sys
from pathlib import Path

# Add the backend root to Python's import path.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

import tkinter as tk
from tkinter import ttk, messagebox

from sqlalchemy import select

from app.database.connections import SessionLocal
from app.models.organisations import Organization
from app.models.personnel import Personnel


class PersonnelRegistrationApp:

    def __init__(self, root):
        self.root = root

        self.root.title("Digi-CoC Personnel Registration")
        self.root.geometry("520x520")
        self.root.resizable(False, False)

        self.organizations = []

        self.build_interface()
        self.load_organizations()

    def build_interface(self):

        main_frame = ttk.Frame(self.root, padding=25)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(
            main_frame,
            text="Personnel Registration",
            font=("Arial", 17, "bold"),
        ).pack(pady=(0, 5))

        ttk.Label(
            main_frame,
            text="Register personnel for an existing organization",
        ).pack(pady=(0, 20))

        # Organization selection
        ttk.Label(main_frame, text="Organization").pack(anchor="w")

        self.organization_var = tk.StringVar()

        self.organization_combo = ttk.Combobox(
            main_frame,
            textvariable=self.organization_var,
            state="readonly",
            width=45,
        )

        self.organization_combo.pack(fill="x", pady=(5, 15))

        # Personnel code
        ttk.Label(main_frame, text="Personnel Code").pack(anchor="w")

        self.personnel_code_entry = ttk.Entry(main_frame)
        self.personnel_code_entry.pack(fill="x", pady=(5, 15))

        # Full name
        ttk.Label(main_frame, text="Full Name").pack(anchor="w")

        self.full_name_entry = ttk.Entry(main_frame)
        self.full_name_entry.pack(fill="x", pady=(5, 15))

        # Role selection
        ttk.Label(main_frame, text="Role").pack(anchor="w")

        self.role_var = tk.StringVar(value="officer")

        self.role_combo = ttk.Combobox(
            main_frame,
            textvariable=self.role_var,
            values=[
                "admin",
                "reviewer",
                "officer",
                "investigator",
                "supervisor",
            ],
            state="readonly",
        )

        self.role_combo.pack(fill="x", pady=(5, 15))

        # Active status
        self.active_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            main_frame,
            text="Account Active",
            variable=self.active_var,
        ).pack(anchor="w", pady=(0, 15))

        # Register button
        ttk.Button(
            main_frame,
            text="Register Personnel",
            command=self.register_personnel,
        ).pack(fill="x", pady=5)

        # Clear button
        ttk.Button(
            main_frame,
            text="Clear Form",
            command=self.clear_form,
        ).pack(fill="x", pady=5)

        # Refresh organizations button
        ttk.Button(
            main_frame,
            text="Refresh Organizations",
            command=self.load_organizations,
        ).pack(fill="x", pady=5)

    def load_organizations(self):

        try:

            with SessionLocal() as db:

                organizations = db.scalars(
                    select(Organization).order_by(
                        Organization.organization_code
                    )
                ).all()

                self.organizations = [
                    {
                        "id": organization.id,
                        "code": organization.organization_code,
                    }
                    for organization in organizations
                ]

            organization_options = [
                organization["code"]
                for organization in self.organizations
            ]

            self.organization_combo["values"] = organization_options

            if organization_options:
                self.organization_combo.current(0)
            else:
                self.organization_var.set("")

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not load organizations:\n{error}",
            )

    def register_personnel(self):

        organization_code = self.organization_var.get().strip()

        personnel_code = (
            self.personnel_code_entry.get().strip()
        )

        full_name = self.full_name_entry.get().strip()

        role = self.role_var.get().strip()

        is_active = self.active_var.get()

        # Validate required fields.
        if not organization_code:
            messagebox.showerror(
                "Missing Organization",
                "Please select an organization.",
            )
            return

        if not personnel_code:
            messagebox.showerror(
                "Missing Personnel Code",
                "Please enter a personnel code.",
            )
            return

        if not full_name:
            messagebox.showerror(
                "Missing Name",
                "Please enter the person's full name.",
            )
            return

        if not role:
            messagebox.showerror(
                "Missing Role",
                "Please select a role.",
            )
            return

        try:

            with SessionLocal() as db:

                # Find the selected organization.
                organization = db.scalar(
                    select(Organization).where(
                        Organization.organization_code
                        == organization_code
                    )
                )

                if organization is None:

                    messagebox.showerror(
                        "Organization Not Found",
                        "The selected organization no longer exists.",
                    )

                    return

                # Check duplicate personnel code within organization.
                existing_personnel = db.scalar(
                    select(Personnel).where(
                        Personnel.organization_id == organization.id,
                        Personnel.personnel_code == personnel_code,
                    )
                )

                if existing_personnel is not None:

                    messagebox.showerror(
                        "Duplicate Personnel Code",
                        "This personnel code already exists "
                        "in the selected organization.",
                    )

                    return

                # Create the personnel record.
                personnel = Personnel(
                    organization_id=organization.id,
                    personnel_code=personnel_code,
                    full_name=full_name,
                    role=role,
                    is_active=is_active,
                )

                db.add(personnel)

                db.commit()

            messagebox.showinfo(
                "Registration Successful",
                f"Personnel registered successfully!\n\n"
                f"Name: {full_name}\n"
                f"Personnel Code: {personnel_code}\n"
                f"Organization: {organization_code}\n"
                f"Role: {role}",
            )

            # Clear fields so another person can be registered.
            self.clear_form()

        except Exception as error:

            messagebox.showerror(
                "Registration Failed",
                f"Could not register personnel:\n{error}",
            )

    def clear_form(self):

        self.personnel_code_entry.delete(0, tk.END)

        self.full_name_entry.delete(0, tk.END)

        self.role_combo.current(2)

        self.active_var.set(True)


if __name__ == "__main__":

    root = tk.Tk()

    app = PersonnelRegistrationApp(root)

    root.mainloop()
