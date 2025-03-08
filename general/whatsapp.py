import subprocess
from reportlab.pdfgen import canvas


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
    # Create a PDF file
    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, text)  
    c.save()
    print(f"PDF created successfully: {filename}")
    send_message(number[1:],"output.pdf")




