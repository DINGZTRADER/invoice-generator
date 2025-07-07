import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dateutil.parser import parse
from fpdf import FPDF
import pandas as pd
import os

# Room Rates from ROOM RATES.pdf
ROOM_RATES = {
    "Crested Crane": [98, 120, 142, 164],
    "Wild Geese": [135, 157, 179],
    "Kingfisher": [110, 132, 154, 176, 198],
    "Ross Turaco": [110, 132, 154],
    "Tower": [55, 77],
    "Wax Bill": [95, 117, 139, 161],
    "Starling": [85, 107],
    "Ibis": [75, 98, 120],
    "Caven": [100, 122],
    "Tree House The Crown": [100, 122],
    "Sunbird": [98, 120, 142],
}

EXTRA_GUEST_RATE = 22
BREAKFAST_RATE = 10
CONFERENCE_ROOM_RATE = 120
PA_SYSTEM_RATE = 40


class InvoiceGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yellow Haven Lodge - Invoice Generator")
        self.root.geometry("800x700")
        self.rooms = []

        # Header
        header = tk.Label(root, text="YELLOW HAVEN LODGE", font=("Arial", 16, "bold"))
        header.pack(pady=10)
        subheader = tk.Label(root, text="Invoice Generator", font=("Arial", 12))
        subheader.pack()

        # Guest Info
        self.create_guest_info_frame()

        # Room Selection
        self.create_room_selection_frame()

        # Extras
        self.create_extras_frame()

        # Breakfast
        self.create_breakfast_frame()

        # Discount
        self.create_discount_frame()

        # Preview
        self.create_preview_frame()

        # Generate Button
        tk.Button(root, text="Generate Invoice", command=self.generate_invoice, bg="#28a745", fg="white", width=20,
                  font=("Arial", 12)).pack(pady=20)

    def create_guest_info_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Guest Name").grid(row=0, column=0, sticky='w')
        self.guest_name = tk.Entry(frame, width=40)
        self.guest_name.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Check-in Date (e.g., 18 June 2025)").grid(row=1, column=0, sticky='w')
        self.checkin = tk.Entry(frame, width=40)
        self.checkin.grid(row=1, column=1, padx=5)

        tk.Label(frame, text="Check-out Date (e.g., 21 June 2025)").grid(row=2, column=0, sticky='w')
        self.checkout = tk.Entry(frame, width=40)
        self.checkout.grid(row=2, column=1, padx=5)

    def create_room_selection_frame(self):
        tk.Label(self.root, text="Room Selection", font=("Arial", 12, "underline")).pack(anchor='w', padx=20, pady=(10, 5))

        self.room_frame = tk.Frame(self.root)
        self.room_frame.pack(padx=20)

        self.add_room_row()

        tk.Button(self.root, text="Add Another Room", command=self.add_room_row).pack(pady=5)

    def add_room_row(self):
        frame = tk.Frame(self.room_frame)
        frame.pack(pady=5, fill='x')

        tk.Label(frame, text="Room Type:").pack(side='left')
        room_type = ttk.Combobox(frame, values=list(ROOM_RATES.keys()), width=20)
        room_type.pack(side='left', padx=5)

        tk.Label(frame, text="Pax:").pack(side='left')
        pax = tk.Spinbox(frame, from_=1, to=5, width=3)
        pax.pack(side='left', padx=5)

        self.rooms.append((frame, room_type, pax))

    def create_extras_frame(self):
        tk.Label(self.root, text="Extras", font=("Arial", 12, "underline")).pack(anchor='w', padx=20, pady=(10, 5))

        frame = tk.Frame(self.root)
        frame.pack(padx=20, fill='x')

        self.conference_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Conference Room ($120/day)", variable=self.conference_var).grid(row=0, column=0,
                                                                                               sticky='w')
        tk.Label(frame, text="Days:").grid(row=0, column=1)
        self.conference_days = tk.Entry(frame, width=5)
        self.conference_days.grid(row=0, column=2)

        self.pa_system_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="PA System ($40/day)", variable=self.pa_system_var).grid(row=1, column=0, sticky='w')
        tk.Label(frame, text="Days:").grid(row=1, column=1)
        self.pa_system_days = tk.Entry(frame, width=5)
        self.pa_system_days.grid(row=1, column=2)

    def create_breakfast_frame(self):
        tk.Label(self.root, text="Breakfast ($10/person/day)", font=("Arial", 12, "underline")).pack(anchor='w', padx=20,
                                                                                                pady=(10, 5))

        frame = tk.Frame(self.root)
        frame.pack(padx=20, fill='x')

        self.breakfast_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Include Breakfast", variable=self.breakfast_var).pack(anchor='w')

        tk.Label(frame, text="Number of Guests:").pack(side='left')
        self.breakfast_guests = tk.Entry(frame, width=5)
        self.breakfast_guests.pack(side='left', padx=5)

        tk.Label(frame, text="Days:").pack(side='left')
        self.breakfast_days = tk.Entry(frame, width=5)
        self.breakfast_days.pack(side='left', padx=5)

    def create_discount_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=20, fill='x')

        tk.Label(frame, text="Discount on Rooms:").pack(side='left')
        self.discount_var = ttk.Combobox(frame, values=["0%", "10%", "15%", "20%"], width=5)
        self.discount_var.set("0%")
        self.discount_var.pack(side='left', padx=5)

    def create_preview_frame(self):
        tk.Label(self.root, text="Invoice Summary", font=("Arial", 12, "underline")).pack(anchor='w', padx=20,
                                                                                      pady=(10, 5))
        self.preview_label = tk.Label(self.root, text="", justify="left", font=("Courier", 10), anchor='e')
        self.preview_label.pack(padx=20, anchor='e')

    def calculate_nights(self):
        try:
            checkin_date = parse(self.checkin.get())
            checkout_date = parse(self.checkout.get())
            return (checkout_date - checkin_date).days
        except Exception as e:
            messagebox.showerror("Date Error", "Please enter valid dates.")
            return None

    def update_preview(self):
        nights = self.calculate_nights()
        if not nights:
            return

        room_details = []
        room_subtotal = 0
        for _, room_type, pax in self.rooms:
            room = room_type.get()
            pax_count = int(pax.get())
            if room == "":
                continue
            base_rates = ROOM_RATES[room]
            if pax_count > len(base_rates):
                rate = base_rates[-1] + (pax_count - len(base_rates)) * EXTRA_GUEST_RATE
            else:
                rate = base_rates[pax_count - 1]
            total = rate * nights
            room_details.append((room, pax_count, rate, nights, total))
            room_subtotal += total

        discount_percent = float(self.discount_var.get().strip('%')) / 100
        discount_amount = room_subtotal * discount_percent

        breakfast_total = 0
        if self.breakfast_var.get():
            try:
                guests = int(self.breakfast_guests.get())
                days = int(self.breakfast_days.get())
                breakfast_total = guests * BREAKFAST_RATE * days
            except ValueError:
                pass

        conference_total = 0
        if self.conference_var.get():
            try:
                conf_days = float(self.conference_days.get())
                conference_total = conf_days * CONFERENCE_ROOM_RATE
            except ValueError:
                pass

        pa_total = 0
        if self.pa_system_var.get():
            try:
                pa_days = float(self.pa_system_days.get())
                pa_total = pa_days * PA_SYSTEM_RATE
            except ValueError:
                pass

        subtotal = room_subtotal + breakfast_total + conference_total + pa_total
        grand_total = subtotal - discount_amount

        preview_text = (
            f"Subtotal (Rooms): ${room_subtotal:.2f}\n"
            f"Discount ({discount_percent * 100:.0f}%): -${discount_amount:.2f}\n"
            f"Breakfast: ${breakfast_total:.2f}\n"
            f"Conference Room: ${conference_total:.2f}\n"
            f"PA System: ${pa_total:.2f}\n"
            f"Grand Total: ${grand_total:.2f}"
        )
        self.preview_label.config(text=preview_text)

    def generate_invoice(self):
        self.update_preview()  # Make sure all values are up-to-date

        nights = self.calculate_nights()
        if not nights:
            return

        guest = self.guest_name.get().strip()
        if not guest:
            messagebox.showwarning("Input Error", "Please enter guest name.")
            return

        # Build invoice data
        room_details = []
        room_subtotal = 0
        for _, room_type, pax in self.rooms:
            room = room_type.get()
            pax_count = int(pax.get())
            if room == "":
                continue
            base_rates = ROOM_RATES[room]
            if pax_count > len(base_rates):
                rate = base_rates[-1] + (pax_count - len(base_rates)) * EXTRA_GUEST_RATE
            else:
                rate = base_rates[pax_count - 1]
            total = rate * nights
            room_details.append((room, pax_count, rate, nights, total))
            room_subtotal += total

        discount_percent = float(self.discount_var.get().strip('%')) / 100
        discount_amount = room_subtotal * discount_percent

        breakfast_total = 0
        if self.breakfast_var.get():
            try:
                guests = int(self.breakfast_guests.get())
                days = int(self.breakfast_days.get())
                breakfast_total = guests * BREAKFAST_RATE * days
            except ValueError:
                pass

        conference_total = 0
        if self.conference_var.get():
            try:
                conf_days = float(self.conference_days.get())
                conference_total = conf_days * CONFERENCE_ROOM_RATE
            except ValueError:
                pass

        pa_total = 0
        if self.pa_system_var.get():
            try:
                pa_days = float(self.pa_system_days.get())
                pa_total = pa_days * PA_SYSTEM_RATE
            except ValueError:
                pass

        subtotal = room_subtotal + breakfast_total + conference_total + pa_total
        grand_total = subtotal - discount_amount

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, txt="YELLOW HAVEN LODGE", ln=True, align='C')
        pdf.cell(0, 5, txt="Plot 2A, Kanyanya Road | Kampala, Uganda", ln=True, align='C')
        pdf.cell(0, 5, txt="+256 772 200 300 | info@yellowhavenlodge.com", ln=True, align='C')
        pdf.ln(10)

        pdf.cell(0, 10, txt=f"Guest: {guest}", ln=True)
        pdf.cell(0, 10, txt=f"Dates: {self.checkin.get()} – {self.checkout.get()}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Room Charges", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(70, 7, txt="Room", border=1)
        pdf.cell(20, 7, txt="Pax", border=1, align='C')
        pdf.cell(25, 7, txt="Rate/Night", border=1, align='R')
        pdf.cell(20, 7, txt="Nights", border=1, align='C')
        pdf.cell(25, 7, txt="Total", border=1, align='R')
        pdf.ln()

        for room, pax, rate, nts, total in room_details:
            pdf.cell(70, 7, txt=room, border=1)
            pdf.cell(20, 7, txt=str(pax), border=1, align='C')
            pdf.cell(25, 7, txt=f"${rate:.2f}", border=1, align='R')
            pdf.cell(20, 7, txt=str(nts), border=1, align='C')
            pdf.cell(25, 7, txt=f"${total:.2f}", border=1, align='R')
            pdf.ln()

        pdf.ln(2)
        pdf.cell(160, 7, txt=f"Subtotal (Rooms): ${room_subtotal:.2f}", ln=True, align='R')

        if discount_amount > 0:
            pdf.cell(160, 7, txt=f"Discount ({discount_percent*100:.0f}%): -${discount_amount:.2f}", ln=True, align='R')

        if breakfast_total > 0:
            pdf.ln(5)
            pdf.cell(0, 10, txt="Breakfast Charges", ln=True)
            pdf.cell(160, 7, txt=f"Breakfast: ${breakfast_total:.2f}", ln=True, align='R')

        if conference_total > 0:
            pdf.cell(160, 7, txt=f"Conference Room: ${conference_total:.2f}", ln=True, align='R')

        if pa_total > 0:
            pdf.cell(160, 7, txt=f"PA System: ${pa_total:.2f}", ln=True, align='R')

        pdf.ln(2)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(160, 7, txt=f"Grand Total: ${grand_total:.2f}", ln=True, align='R')

        filename_base = f"Invoice_{guest.replace(' ', '_')}"
        pdf_filename = f"{filename_base}.pdf"
        xlsx_filename = f"{filename_base}.xlsx"

        # Save PDF
        pdf.output(pdf_filename)

        # Save Excel
        df = pd.DataFrame(room_details, columns=["Room", "Pax", "Rate/Night", "Nights", "Total"])
        df.to_excel(xlsx_filename, index=False)

        messagebox.showinfo("Success", f"Invoice saved as:\n{pdf_filename}\n{xlsx_filename}")

        try:
            os.startfile(pdf_filename)
            os.startfile(xlsx_filename)
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceGeneratorApp(root)
    root.mainloop()