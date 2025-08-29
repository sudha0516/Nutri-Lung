from flask import Flask, render_template, request, session
import mysql.connector
import pandas as pd
import joblib
import numpy as np
import random

app = Flask(__name__)
app.secret_key = 'admin'

# ✅ Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='lung_db'
)
mycursor = mydb.cursor()

# ✅ Database helpers
def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values):
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

# ==========================
# Routes
# ==========================

@app.route('/')
def index():
    return render_template('index.html')

# ✅ Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name', '')  # optional
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']

        if password == c_password:
            query = "SELECT email FROM users"
            email_data = retrivequery2(query)
            email_data_list = [i[0].lower() for i in email_data]

            if email.lower() not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)
                return render_template('login.html', message="✅ Successfully Registered!")
            return render_template('register.html', message="⚠️ This email already exists!")
        return render_template('register.html', message="⚠️ Confirm password does not match!")
    return render_template('register.html')

# ✅ Login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        query = "SELECT password FROM users WHERE email = %s"
        values = (email,)
        password_data = retrivequery1(query, values)

        if password_data and password == password_data[0][0]:
            session['name'] = email
            return render_template('home.html', message=f"Welcome {email}")
        return render_template('login.html', message="⚠️ Invalid email or password!")
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ✅ File Upload
@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        df = pd.read_csv(file)
        df_html = df.to_html()
        return render_template('upload.html', df=df_html)
    return render_template('upload.html')

# ✅ Model Accuracy Page
@app.route('/model', methods=["GET", "POST"])
def model_page():
    if request.method == "POST":
        algorithams = request.form["algo"]

        if algorithams == "1":
            accuracy = 98.17
            msg = f'Accuracy for Random Forest is {accuracy}%'
        elif algorithams == "2":
            accuracy = 100
            msg = f'Accuracy for XGBoost is {accuracy}%'
        elif algorithams == "3":
            accuracy = 100
            msg = f'Accuracy for Voting Classifier is {accuracy}%'
        elif algorithams == "4":
            accuracy = 99
            msg = f'Accuracy for SVM is {accuracy}%'
        elif algorithams == "5":
            accuracy = 98.63
            msg = f'Accuracy for Decision Tree is {accuracy}%'
        else:
            accuracy = 0
            msg = "⚠️ Unknown algorithm selected"

        return render_template('model.html', msg=msg, accuracy=accuracy)
    return render_template('model.html')

# ✅ Prediction
@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    result = None
    recommendations = None

    if request.method == "POST":
        air_pollution = int(request.form['Air Pollution'])
        alcohol_use = int(request.form['Alcohol use'])
        genetic_risk = int(request.form['Genetic Risk'])
        balanced_diet = int(request.form['Balanced Diet'])
        obesity = int(request.form['Obesity'])
        smoking = int(request.form['Smoking'])
        passive_smoker = int(request.form['Passive Smoker'])
        chest_pain = int(request.form['Chest Pain'])
        coughing_of_blood = int(request.form['Coughing of Blood'])
        fatigue = int(request.form['Fatigue'])

        # Load saved SVM model
        model = joblib.load('svm_model.joblib')

        def prediction_function(inputs):
            classes = {0: "High", 1: "Medium", 2: "Low"}
            prediction = model.predict(inputs)
            return classes[prediction[0]]

        inputs = np.array([[air_pollution, alcohol_use, genetic_risk, balanced_diet,
                            obesity, smoking, passive_smoker, chest_pain,
                            coughing_of_blood, fatigue]])
        result = prediction_function(inputs)

        # Recommendations
        high_risk_recommendations = [
            "Consult a pulmonologist immediately for evaluation.",
            "Stop smoking and avoid secondhand smoke completely.",
            "Limit alcohol consumption to reduce risks.",
            "Exercise regularly to strengthen lung capacity.",
            "Maintain a diet rich in antioxidants and vegetables.",
            "Report persistent cough, chest pain, or fatigue to your doctor."
        ]

        medium_risk_recommendations = [
            "Consult your physician to discuss lifestyle changes.",
            "Reduce smoking gradually and plan to quit completely.",
            "Choose healthier beverages instead of alcohol.",
            "Eat a balanced diet with at least five servings of vegetables daily.",
            "Do brisk walking or light jogging daily.",
            "Check air quality reports and avoid polluted environments."
        ]

        low_risk_recommendations = [
            "Maintain annual health check-ups.",
            "Continue avoiding smoking and secondhand smoke.",
            "Keep alcohol consumption within safe limits.",
            "Eat a healthy diet rich in fruits and whole grains.",
            "Exercise like cycling, swimming, or jogging 3–4 times a week.",
            "Stay updated with research in lung health prevention."
        ]

        if result == "High":
            recommendations = random.sample(high_risk_recommendations, 3)
        elif result == "Medium":
            recommendations = random.sample(medium_risk_recommendations, 3)
        elif result == "Low":
            recommendations = random.sample(low_risk_recommendations, 3)

    return render_template('prediction.html', prediction=result, recommendations=recommendations)

# ==========================
# Run Flask App
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
