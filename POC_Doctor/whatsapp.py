import subprocess

from fpdf import FPDF # type: ignore

def send_message(number,path):
    # Construct the command
    command = f"npx mudslide@latest send-file {number} {path}"
    
    # Run the command
    result = subprocess.run(command, shell=True, text=True, capture_output=True, encoding="utf-8")    
    # Check for errors and print the output
    if result.returncode == 0:
        print(f"Message sent successfully: {result.stdout}")
    else:
        print(f"Error: {result.stderr}")
def create_pdf(number,text, filename="output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)
    send_message(number[1:],"output.pdf")




