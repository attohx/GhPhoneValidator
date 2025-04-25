import re
import csv
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

# ---------- Validation Logic ----------
def is_valid_ghana_number(number):
    number = number.replace(" ", "").replace("-", "")
    if re.match(r'^\+233\d{9}$', number):
        raw_number = number[4:]
        prefix = raw_number[:3]
        formatted = "0" + raw_number
    elif re.match(r'^0\d{9}$', number):
        raw_number = number[1:]
        prefix = raw_number[:3]
        formatted = "+233" + raw_number
    else:
        return False, "Invalid format", number, None

    valid_prefixes = {
        "024": "MTN", "025": "MTN", "053": "MTN", "054": "MTN", "055": "MTN", "059": "MTN",
        "020": "Vodafone", "050": "Vodafone",
        "026": "AirtelTigo", "027": "AirtelTigo", "056": "AirtelTigo", "057": "AirtelTigo",
        "023": "Glo",
        "028": "Expresso"
    }

    if prefix in valid_prefixes:
        return True, f"Valid ({valid_prefixes[prefix]})", formatted, valid_prefixes[prefix]
    return False, "Invalid prefix", number, None

# ---------- GUI Setup ----------
app = ttk.Window(themename="flatly")
app.title("📞 Ghana Number Validator - Updated")
app.geometry("540x620")
app.resizable(False, False)

validated_numbers = []
summary_stats = {"total": 0, "valid": 0, "invalid": 0, "networks": {}}

# ---------- Functions ----------
def validate_number():
    number = entry.get()
    valid, message, formatted, network = is_valid_ghana_number(number)
    result_label.config(text=message, foreground="green" if valid else "red")
    cherri_msg.set("Cherri says: " + ("✅ That's a valid number!" if valid else "❌ Nope! Try again."))

    if valid:
        validated_numbers.append((formatted, network))
        summary_stats["total"] += 1
        summary_stats["valid"] += 1
        summary_stats["networks"][network] = summary_stats["networks"].get(network, 0) + 1
    else:
        summary_stats["total"] += 1
        summary_stats["invalid"] += 1

    update_stats()

def update_stats():
    stats_text = f"📊 Total: {summary_stats['total']} | ✅ Valid: {summary_stats['valid']} | ❌ Invalid: {summary_stats['invalid']}\n"
    for net, count in summary_stats["networks"].items():
        stats_text += f" - {net}: {count}\n"
    stats_label.config(text=stats_text)

def convert_format():
    number = entry.get().replace(" ", "").replace("-", "")
    if number.startswith("0") and len(number) == 10:
        converted = "+233" + number[1:]
    elif number.startswith("+233") and len(number) == 13:
        converted = "0" + number[4:]
    else:
        messagebox.showinfo("Convert", "Not a valid number to convert.")
        return
    entry.delete(0, END)
    entry.insert(0, converted)

def validate_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            number = row[0]
            valid, _, formatted, network = is_valid_ghana_number(number)
            if valid:
                validated_numbers.append((formatted, network))
                summary_stats["valid"] += 1
                summary_stats["networks"][network] = summary_stats["networks"].get(network, 0) + 1
            else:
                summary_stats["invalid"] += 1
            summary_stats["total"] += 1

    update_stats()
    messagebox.showinfo("Batch Validation", "File processed successfully.")

def export_validated():
    if not validated_numbers:
        messagebox.showinfo("Export", "No validated numbers to export.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv",
                                         filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Phone Number", "Network"])
            for number, network in validated_numbers:
                writer.writerow([number, network])
        messagebox.showinfo("Export", "Exported successfully!")

# ---------- Widgets ----------
ttk.Label(app, text="🇬🇭 Ghana Number Validator", font=("Segoe UI", 20, "bold")).pack(pady=20)

frame = ttk.Frame(app, padding=10)
frame.pack(pady=5)

entry = ttk.Entry(frame, font=("Segoe UI", 14), width=30, bootstyle="info")
entry.pack(pady=10)

ttk.Button(frame, text="Validate", bootstyle="success-outline", width=20, command=validate_number).pack(pady=5)
ttk.Button(frame, text="Convert Format", bootstyle="info-outline", width=20, command=convert_format).pack(pady=5)
ttk.Button(frame, text="Validate From File", bootstyle="warning-outline", width=20, command=validate_from_file).pack(pady=5)

result_label = ttk.Label(frame, text="", font=("Segoe UI", 14), wraplength=400)
result_label.pack(pady=10)

cherri_msg = ttk.StringVar()
ttk.Label(frame, textvariable=cherri_msg, font=("Segoe UI", 12, "italic"), foreground="purple", wraplength=400).pack(pady=5)

stats_label = ttk.Label(app, text="", font=("Segoe UI", 12), wraplength=480, justify="left")
stats_label.pack(pady=10)

ttk.Button(app, text="💾 Export Valid Numbers", bootstyle="primary", width=30, command=export_validated).pack(pady=15)

# ---------- Launch ----------
update_stats()
app.mainloop()
