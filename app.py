from flask import Flask, render_template, request, send_file
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd
import numpy as np
import csv
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Initialize Flask app
app = Flask(__name__)

# Function to calculate pressure data
def calculate_pressure_data():
    log_file_path = r"C:\Users\js838\Desktop\Graph\data\20241022-133343_SL1_Ibrar.log.txt"
    csv_file_path = r"C:\Users\js838\Desktop\Graph\data\output4.csv"

    try:
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()

        lines_to_remove = {0, 1, 2, 4}
        filtered_lines = [line for index, line in enumerate(lines) if index not in lines_to_remove]

        csv_data = []
        for line in filtered_lines:
            columns = line.split()[1:]
            csv_data.append(columns)

        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(csv_data)

        df = pd.read_csv(csv_file_path)
        data = list(df.iloc[0])

        temp_max = []
        diff_val = []

        for i in range(1, 6):
            temp = "Ch01Gr0" + str(i)
            maxim = max(df[temp])
            temp_max.append(maxim)

        for i in range(1, 6):
            temp = "Ch02Gr0" + str(i)
            maxim = max(df[temp])
            temp_max.append(maxim)

        for i, j in zip(temp_max, data):
            diff_val.append(j - i)

        left_foot = diff_val[5:]
        right_foot = diff_val[:5]

        l_mean = np.mean(left_foot)
        r_mean = np.mean(right_foot)

        return l_mean, r_mean
    except Exception as e:
        print(f"An error occurred while calculating pressure data: {e}")
        return None, None

# Function to generate the graph
def generate_graph():
    try:
        df = pd.read_csv(r"C:\Users\js838\Desktop\Graph\data\output4.csv")
        Wavelength_No_Load = [1559.9401, 1554.3851, 1549.3752, 1545.2885, 1542.5413, 
                              1559.7816, 1553.9641, 1549.3252, 1546.7133, 1542.9034]

        temp_max = []
        diff_val = []
        for i in range(1, 6):
            temp = "Ch01Gr0" + str(i)
            maxim = max(df[temp])
            temp_max.append(maxim)
        for i in range(1, 6):
            temp = "Ch02Gr0" + str(i)
            maxim = max(df[temp])
            temp_max.append(maxim)
        for i, j in zip(temp_max, Wavelength_No_Load):
            diff_val.append(j - i)

        lfw = [6.4474 * i * 98.0665 for i in diff_val[5:]]
        rfw = [6.4474 * i * 98.0665 for i in diff_val[:5]]
        lmean = np.mean(lfw)
        rmean = np.mean(rfw)

        fig, ax = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle("PLANTAR PRESSURE MEASURING DEVICE", fontsize="14", fontweight="bold", color="darkblue")
        na1 = ["Mid-Heel", "Midfoot-Center", "Metatarsal Head-5", "Metatarsal Head-1", "Greater Toe"]
        na2 = ["Mid-Heel", "Midfoot-Center", "Metatarsal Head-1", "Metatarsal Head-5", "Greater Toe"]

        ax[0].plot(na2, lfw, marker="*", mec="r", mfc="r")
        ax[0].grid()
        ax[0].set_title("Left Foot Pressure", fontweight="bold")
        ax[0].set_ylabel("Pressure(KPa)", fontweight="bold")
        ax[0].set_xlabel("Sensor Index", fontweight="bold")
        ax[0].axhline(lmean, ls="--", color="r", label=f'Average: {lmean:.4f} KPa')
        ax[0].legend(loc="lower left")

        ax[1].plot(na1, rfw, marker="*", mec="r", mfc="r")
        ax[1].grid()
        ax[1].set_title("Right Foot Pressure", fontweight="bold")
        ax[1].set_ylabel("Pressure(KPa)", fontweight="bold")
        ax[1].set_xlabel("Sensor Index", fontweight="bold")
        ax[1].axhline(rmean, ls="--", color="r", label=f'Average: {rmean:.4f} KPa')
        ax[1].legend(loc="lower left")

        plt.tight_layout(pad=5)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)
        return buffer
    except Exception as e:
        print(f"An error occurred while generating the graph: {e}")
        return None

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    left_pressure, right_pressure = calculate_pressure_data()
    
    if left_pressure is None or right_pressure is None:
        return "Error calculating pressure data. Please check the log file and CSV file paths."

    try:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.drawString(100, 800, f"Name: {name}")
        pdf.drawString(100, 780, f"Age: {age}")
        pdf.drawString(100, 760, f"Gender: {gender}")
        pdf.drawString(100, 740, f"Left Foot Pressure: {left_pressure:.2f} KPa")
        pdf.drawString(100, 720, f"Right Foot Pressure: {right_pressure:.2f} KPa")
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="Report.pdf", mimetype='application/pdf')
    except Exception as e:
        print(f"An error occurred while generating the PDF: {e}")
        return "Error generating PDF."

@app.route('/generate_graph')
def graph():
    buffer = generate_graph()
    if buffer is None:
        return "Error generating graph."
    return send_file(buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
