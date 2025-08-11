import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from num2words import num2words

def amount_to_words(amount):
    rupees = int(amount)
    paisa = int(round((amount - rupees) * 100))
    words = num2words(rupees, to='cardinal').replace('-', ' ')
    if rupees == 0:
        words = "Zero"
    return f"{words.capitalize()} rupees and {paisa:02d} paisa"

def generate_check(data, filename):
    PAGE_WIDTH, PAGE_HEIGHT = letter
    c = canvas.Canvas(filename, pagesize=letter)

    # check size and position (adjust if needed)
    check_w = 6 * inch
    check_h = 2.75 * inch
    x = 0.75 * inch
    y = PAGE_HEIGHT - 1.0 * inch - check_h  # reportlab origin is bottom-left

    # optional outline so you can see where the check is
    c.rect(x, y, check_w, check_h)

    # header: date
    c.setFont("Helvetica", 10)
    c.drawRightString(x + check_w - 0.3 * inch, y + check_h - 0.3 * inch, f"Date: {data['date']}")

    # payee line
    c.setFont("Helvetica", 10)
    c.drawString(x + 0.3 * inch, y + check_h - 0.7 * inch, f"Pay to the order of: {data['payee']}")

    # numeric amount on the right
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(x + check_w - 0.3 * inch, y + check_h - 0.7 * inch, f"Rupees: {data['amount']:.2f}")

    # amount in words
    c.setFont("Helvetica", 10)
    words = amount_to_words(data['amount'])
    c.drawString(x + 0.3 * inch, y + check_h - 1.15 * inch, words)

    # memo and signature area
    c.drawString(x + 0.3 * inch, y + 0.6 * inch, f"Memo: {data.get('memo','')}")
    c.drawString(x + check_w - 2.3 * inch, y + 0.6 * inch, "Signature:")
    if data.get('signature'):
        try:
            c.drawImage(data['signature'], x + check_w - 1.8 * inch, y + 0.25 * inch, width=1.6 * inch, height=0.6 * inch, preserveAspectRatio=True)
        except Exception:
            # if image fails, just draw a line
            c.line(x + check_w - 2.3 * inch, y + 0.4 * inch, x + check_w - 0.3 * inch, y + 0.4 * inch)
    else:
        c.line(x + check_w - 2.3 * inch, y + 0.4 * inch, x + check_w - 0.3 * inch, y + 0.4 * inch)

    # bank name and a simple MICR-like line (this is NOT real MICR)
    c.drawString(x + 0.3 * inch, y + 0.25 * inch, data.get('bank', 'Your Bank Name'))
    c.setFont("Courier", 12)
    micr_text = f"{data.get('routing','')}  {data.get('account','')}  {data.get('check_num','')}"
    c.drawCentredString(x + check_w / 2, y + 0.05 * inch, micr_text)

    c.showPage()
    c.save()

# GUI
root = tk.Tk()
root.title("Jaly Check Printer")

labels = ["Date", "Payee", "Amount (e.g. 123.45)", "Memo", "Bank", "Routing #", "Account #", "Check #", "Signature (optional)"]
vars = {}
for i, lab in enumerate(labels):
    tk.Label(root, text=lab).grid(row=i, column=0, sticky="w", padx=5, pady=3)
    e = tk.Entry(root, width=40)
    e.grid(row=i, column=1, padx=5, pady=3)
    vars[lab] = e

def browse_sig():
    p = filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.bmp"),("All files","*.*")])
    if p:
        vars["Signature (optional)"].delete(0, tk.END)
        vars["Signature (optional)"].insert(0, p)

tk.Button(root, text="Browse Signature", command=browse_sig).grid(row=len(labels), column=0, padx=5, pady=6)

def on_generate():
    try:
        amount = float(vars["Amount (e.g. 123.45)"].get())
    except Exception:
        messagebox.showerror("Error", "Please enter a valid amount like 123.45")
        return
    data = {
        "date": vars["Date"].get(),
        "payee": vars["Payee"].get(),
        "amount": amount,
        "memo": vars["Memo"].get(),
        "bank": vars["Bank"].get(),
        "routing": vars["Routing #"].get(),
        "account": vars["Account #"].get(),
        "check_num": vars["Check #"].get(),
        "signature": vars["Signature (optional)"].get() or None
    }
    savepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
    if not savepath:
        return
    generate_check(data, savepath)
    messagebox.showinfo("Done", f"Saved check to {savepath}")

tk.Button(root, text="Generate PDF Check", command=on_generate, bg="#4CAF50", fg="white").grid(row=len(labels)+1, column=0, columnspan=2, pady=8)

root.mainloop()