
import sys
from pathlib import Path

# Add backend root so Python can find the app package.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import select

from app.core.security import hash_password
from app.database.connections import SessionLocal
from app.models.organisations import Organization
from app.models.personnel import Personnel


def set_password():
    organization_code = organization_entry.get().strip()
    personnel_code = personnel_entry.get().strip()
    password = password_entry.get()
    confirmation = confirm_entry.get()

    if not organization_code or not personnel_code:
        messagebox.showerror("Error", "Enter organization and personnel codes.")
        return

    if len(password) < 12:
        messagebox.showerror("Error", "Password must contain at least 12 characters.")
        return

    if password != confirmation:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    try:
        password_hash = hash_password(password)

        with SessionLocal() as db:
            organization = db.scalar(
                select(Organization).where(
                    Organization.organization_code == organization_code
                )
            )

            if organization is None:
                messagebox.showerror("Error", "Organization not found.")
                return

            personnel = db.scalar(
                select(Personnel).where(
                    Personnel.organization_id == organization.id,
                    Personnel.personnel_code == personnel_code,
                )
            )

            if personnel is None:
                messagebox.showerror("Error", "Personnel not found.")
                return

            if not personnel.is_active:
                messagebox.showerror("Error", "Personnel account is inactive.")
                return

            personnel.password_hash = password_hash
            db.commit()

        messagebox.showinfo(
            "Success",
            "Personnel password successfully configured."
        )

        password_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)

    except Exception as error:
        messagebox.showerror(
            "Error",
            f"Password setup failed:\n{error}"
        )


root = tk.Tk()
root.title("Digi-CoC Personnel Password Setup")
root.geometry("420x350")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

ttk.Label(
    main_frame,
    text="Digi-CoC Password Setup",
    font=("Arial", 15, "bold")
).pack(pady=10)

ttk.Label(main_frame, text="Organization Code").pack(anchor="w")
organization_entry = ttk.Entry(main_frame, width=40)
organization_entry.pack(fill="x", pady=5)

ttk.Label(main_frame, text="Personnel Code").pack(anchor="w")
personnel_entry = ttk.Entry(main_frame, width=40)
personnel_entry.pack(fill="x", pady=5)

ttk.Label(main_frame, text="New Password (minimum 12 characters)").pack(anchor="w")
password_entry = ttk.Entry(main_frame, width=40, show="*")
password_entry.pack(fill="x", pady=5)

ttk.Label(main_frame, text="Confirm Password").pack(anchor="w")
confirm_entry = ttk.Entry(main_frame, width=40, show="*")
confirm_entry.pack(fill="x", pady=5)

ttk.Button(
    main_frame,
    text="Set Personnel Password",
    command=set_password
).pack(pady=15)

root.mainloop()
