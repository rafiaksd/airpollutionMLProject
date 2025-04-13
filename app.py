from flask import Flask,render_template,request,jsonify
import joblib
import pandas as pd
import numpy as np
import threading, time, asyncio

import os

app=Flask(__name__)
app.secret_key = 'your_secret_key_here'

#handle image uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

#car ml model
car_ml_model = joblib.load('car_price_model.pkl')

car=pd.read_csv('Cleaned_Car_data.csv')
companies=sorted(car['company'].unique())
car_models=sorted(car['name'].unique())
fuel_types=car['fuel_type'].unique()

#car predict homepage
@app.route('/',methods=['GET','POST'])
def index():
    prediction = None;
    return render_template('index.html',prediction=prediction, companies=companies, car_models=car_models,fuel_types=fuel_types)

#car predict post
@app.route('/carpredict', methods=['POST'])
def predict():
    print('Got CAR PREDICT POST Request!!!')
    car_company = request.form.get('company')
    car_model = request.form.get('car_models')
    car_year = request.form.get('year')
    car_fuel_type = request.form.get('fuel_type')
    car_driven = request.form.get('kilo_driven')

    prediction = car_ml_model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                              data=np.array([car_model, car_company, car_year, car_driven, car_fuel_type]).reshape(1, 5)))
    
    prediction = str(np.round(prediction[0], -3))
    
    return render_template('index.html', 
                           prediction=prediction, 
                           companies=companies, 
                           car_models=car_models, 
                           fuel_types=fuel_types,
                           selected_company=car_company,
                           selected_model=car_model,
                           selected_year=car_year,
                           selected_kilo_driven=car_driven,
                           selected_fuel_type=car_fuel_type)


#aqi predictor ml model
aqi_predictor_model = joblib.load('aqi_predictor_model.joblib')

def getAQICategory(aqi):
    if 0 <= aqi <= 50:
        return "Good"
    elif 51 <= aqi <= 100:
        return "Moderate"
    elif 101 <= aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif 151 <= aqi <= 200:
        return "Unhealthy"
    elif 201 <= aqi <= 300:
        return "Very Unhealthy"
    elif aqi >= 301:
        return "Hazardous"
    else:
        return "NaN"
    
@app.route('/aqipredict', methods=['GET'])
def aqi_form():
    return render_template('aqi_predict.html', predicted_aqi=None, aqi_category=None)

@app.route('/aqipredict', methods=['POST'])
def aqi_predict():
    print('got AQI Predict POST Request!!!')
    aqi_category = None
    predicted_aqi = None

    # Get data from form
    peak_hour = int(request.form.get('peak_hour'))
    peak_hour_text = 'Yes' if peak_hour == 1 else 'No'

      # 1 for Yes, 0 for No
    raw_conc = float(request.form.get('raw_conc'))
    nowcast_conc = float(request.form.get('nowcast_conc'))

    # Prepare input data for the model
    aqi_input_data = {'Peak_Hour': [peak_hour], 'Raw Conc.': [raw_conc], 'NowCast Conc.': [nowcast_conc]}
    aqi_input_df = pd.DataFrame(aqi_input_data)

    # Predict AQI using the model
    predicted_aqi = aqi_predictor_model.predict(aqi_input_df)
    predicted_aqi_value = predicted_aqi[0]

    aqi_category = getAQICategory(predicted_aqi_value)

    return render_template('aqi_predict.html', predicted_aqi=predicted_aqi_value, aqi_category=aqi_category, 
                           peak_hour=peak_hour_text, raw_conc=raw_conc, nowcast_conc=nowcast_conc)

# Function to check allowed extensions for images
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

async def delete_images_after_delay(delay:int):
    await asyncio.sleep(delay)
    print('Going to DELETE IMAGEs Request!!!')
    # Get all files in the uploads folder
    files_in_folder = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # Loop through all files and delete them
    for file_name in files_in_folder:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")  # Log to the console

    delete_message = f'Deleted images after {delay}s to save server storage'
    print(delete_message)

def delete_thread_function():
    asyncio.run(delete_images_after_delay(100))

@app.route('/air_image')
def air_image():
    return render_template('air_poll_img_classify.html') 

@app.route('/air_image', methods=['POST'])
def air_image_submit():
    print('Got AIR IMAGE Classification POST Request!!!')
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    files = request.files.getlist('file')  # Get a list of all uploaded files
    if not files:
        return jsonify({"error": "No selected files"})
    
    # Ensure the upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    image_urls = []
    for file in files:
        if file.filename == '':
            continue  # Skip files with no filename
        
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Create the URL for the uploaded image
            image_url = f"/static/uploads/{filename}"
            image_urls.append({"image_url": image_url})

    if not image_urls:
        return jsonify({"error": "No valid image files uploaded"})
    
    # Start a background thread to delete images after 1 minute
    threading.Thread(target=delete_thread_function, daemon=True).start()

    # Return the list of image URLs as a JSON array
    return jsonify({"images": image_urls})

if __name__ == "__main__":
    app.run()