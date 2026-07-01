from dotenv import load_dotenv
load_dotenv()

import pandas as pd, os, joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score
from gtts import gTTS
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from utils.disease import detect_disease
import warnings; warnings.filterwarnings("ignore")

# ── TRANSLATIONS ───────────────────────────────────────────────
CROP_TELUGU = {
    "rice":"వరి","tomato":"టమాటా","potato":"బంగాళాదుంప","maize":"మొక్కజొన్న",
    "wheat":"గోధుమ","cotton":"పత్తి","soybean":"సోయాబీన్",
    "groundnut":"వేరుశెనగ","sugarcane":"చెరకు","green gram":"పెసలు",
    "chilli":"మిరపకాయలు","jowar":"జొన్న","sunflower":"పొద్దుతిరుగుడు",
    "turmeric":"పసుపు","red gram":"కందులు",
}
DISEASE_TELUGU = {
    "Healthy":"ఆరోగ్యంగా ఉంది","Rice Blast":"వరి బ్లాస్ట్","Bacterial Leaf Blight":"బ్యాక్టీరియల్ ఆకు మాడు",
    "Brown Spot":"గోధుమ మచ్చ","Sheath Blight":"తొడుగు తెగులు","False Smut":"అబద్ధపు నల్ల తెగులు",
    "Late Blight":"లేట్ బ్లైట్","Early Blight":"ఎర్లీ బ్లైట్","Leaf Mold":"ఆకు బూజు",
    "Septoria Leaf Spot":"సెప్టోరియా మచ్చ","Yellow Leaf Curl Virus":"ఆకు మురుగు వైరస్",
    "Spider Mites":"సాలీడు పురుగులు","Common Rust":"సాధారణ తుప్పు","Northern Leaf Blight":"ఉత్తర ఆకు మాడు",
    "Gray Leaf Spot":"బూడిద మచ్చ","Powdery Mildew":"పొడి బూజు","Stripe Rust":"చారల తుప్పు",
    "Leaf Rust":"ఆకు తుప్పు","Stem Rust":"కాండం తుప్పు","Loose Smut":"వదులు నల్ల తెగులు",
    "Bacterial Blight":"బ్యాక్టీరియల్ తెగులు","Fusarium Wilt":"ఫ్యుజేరియం వాడుపోవడం",
    "Tikka Disease (Leaf Spot)":"టిక్కా వ్యాధి","Rust":"తుప్పు","Red Rot":"ఎర్ర కుళ్ళు",
    "Smut":"నల్ల తెగులు","Yellow Mosaic Virus":"పసుపు మోజాయిక్ వైరస్",
    "Anthracnose":"ఆంత్రాక్నోస్","Leaf Curl Virus":"ఆకు మురుగు వైరస్",
    "Grain Mold":"గింజ బూజు","Downy Mildew":"తడి బూజు","Alternaria Blight":"ఆల్టర్నేరియా తెగులు",
    "Rhizome Rot":"దుంప కుళ్ళు","Leaf Blotch":"ఆకు మచ్చ","Leaf Spot":"ఆకు మచ్చ",
    "Bacterial Wilt":"బ్యాక్టీరియల్ వాడుపోవడం","Phytophthora Blight":"ఫైటోఫ్తోరా తెగులు",
    "Sterility Mosaic":"వంధ్యత్వ మోజాయిక్","Asian Soybean Rust":"ఏషియన్ తుప్పు",
    "Frogeye Leaf Spot":"కప్ప కన్ను మచ్చ","Stalk Rot":"కాండం కుళ్ళు",
    "Bollworm Damage":"బొల్వార్మ్ నష్టం","Common Scab":"సాధారణ పుండు",
    "Sclerotinia Wilt":"స్క్లెరోటీనియా వాడుపోవడం","No disease":"వ్యాధి లేదు",
    "Peanut Mottle Virus":"వేరుశెనగ మోజాయిక్","Stem Rot (Collar Rot)":"కాండం కుళ్ళు",
    "Grassy Shoot (Phytoplasma)":"గడ్డి చిగురు","Pokkah Boeng":"పొక్కా బోయెంగ్",
    "Cercospora Leaf Spot":"సెర్కోస్పోరా మచ్చ","Fruit Rot (Anthracnose)":"పండు కుళ్ళు",
}
SOIL_TELUGU = {
    "red":"ఎర్ర నేల","black":"నల్ల నేల","alluvial":"ఒండ్రు నేల","loamy":"లోమీ నేల",
    "clay":"బంకమట్టి","sandy":"ఇసుక నేల","silt":"పూడిక నేల","peaty":"పీటీ నేల",
    "chalky":"సుద్ద నేల","loam":"లోమీ నేల","clayey":"బంకమట్టి",
}

# Crop-specific typical disease when no image uploaded (realistic defaults)
CROP_DEFAULT_DISEASE = {
    "rice":"Brown Spot","tomato":"Early Blight","potato":"Late Blight","maize":"Common Rust",
    "wheat":"Stripe Rust","cotton":"Bacterial Blight","soybean":"Asian Soybean Rust",
    "groundnut":"Tikka Disease (Leaf Spot)","sugarcane":"Red Rot","green gram":"Yellow Mosaic Virus",
    "chilli":"Leaf Curl Virus","jowar":"Grain Mold","sunflower":"Alternaria Blight",
    "turmeric":"Rhizome Rot","red gram":"Fusarium Wilt",
}

# ── DATASET & MODEL ────────────────────────────────────────────
data = pd.read_csv("data/clean_final_dataset.csv").dropna().reset_index(drop=True)
data['crop_type'] = data['crop_type'].str.lower().str.strip()
data['soil_type']  = data['soil_type'].str.lower().str.strip()

le_crop = LabelEncoder()
le_soil = LabelEncoder()
data['crop_enc'] = le_crop.fit_transform(data['crop_type'])
data['soil_enc'] = le_soil.fit_transform(data['soil_type'])

X = data[['rainfall','temperature','soil_quality','soil_enc','crop_enc']]
y = data['yield']

# Load from models/ folder if available, else train
MODEL_PATH = "models/yield_model.pkl"
if os.path.exists(MODEL_PATH):
    saved = joblib.load(MODEL_PATH)
    model = saved['model']
    le_crop = saved['le_crop']
    le_soil = saved['le_soil']
    print("Model loaded from models/")
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                                       subsample=0.8, random_state=42)
    model.fit(X_train, y_train)
    acc = round(r2_score(y_test, model.predict(X_test)), 4)
    print(f"Model trained. R2: {acc}")
    os.makedirs("models", exist_ok=True)
    joblib.dump({'model':model,'le_crop':le_crop,'le_soil':le_soil,'version':'2.1','accuracy':acc}, MODEL_PATH)
    joblib.dump(le_crop, "models/label_encoder_crop.pkl")
    joblib.dump(le_soil, "models/label_encoder_soil.pkl")

# Dataset stats for approximate defaults
DATASET_DEFAULTS = {
    'rainfall':   round(float(data['rainfall'].mean()), 1),
    'temperature':round(float(data['temperature'].mean()), 1),
    'soil_quality':round(float(data['soil_quality'].mean()), 1),
    'acre':       2.0,
    'soil_type':  'loam',
}

def safe_float(v, default=0.0):
    try:
        val = float(str(v).strip()) if v and str(v).strip() else None
        return val
    except:
        return None

def predict_yield(rainfall, temperature, soil_quality, soil_type, crop_type):
    try:
        soil_enc = le_soil.transform([soil_type.lower().strip()])[0]
    except:
        soil_enc = 0
    try:
        crop_enc = le_crop.transform([crop_type.lower().strip()])[0]
    except:
        # For crops not in dataset (tomato, groundnut etc.) use average encoding
        crop_enc = int(len(le_crop.classes_) / 2)
    row = pd.DataFrame([[rainfall, temperature, soil_quality, soil_enc, crop_enc]],
                       columns=['rainfall','temperature','soil_quality','soil_enc','crop_enc'])
    return round(float(model.predict(row)[0]), 1)

def speak_tts(te_text, en_text):
    import time; ts = str(int(time.time()))
    te_f = f"static/te_{ts}.mp3"; en_f = f"static/en_{ts}.mp3"
    try: gTTS(text=te_text, lang='te').save(te_f)
    except: te_f = "static/te.mp3"
    try: gTTS(text=en_text, lang='en').save(en_f)
    except: en_f = "static/en.mp3"
    return te_f, en_f

# ── FLASK APP ──────────────────────────────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', defaults=DATASET_DEFAULTS)

@app.route('/predict', methods=['POST'])
def predict():
    crop_type  = str(request.form.get('crop_type', '')).lower().strip() or 'rice'
    soil_type  = str(request.form.get('soil_type', '')).lower().strip() or DATASET_DEFAULTS['soil_type']

    # Optional fields — use dataset average if blank
    rainfall     = safe_float(request.form.get('rainfall'))
    temperature  = safe_float(request.form.get('temperature'))
    soil_quality = safe_float(request.form.get('soil_quality'))
    acre         = safe_float(request.form.get('acre'))

    used_defaults = []
    if rainfall is None:
        rainfall = DATASET_DEFAULTS['rainfall']; used_defaults.append('rainfall')
    if temperature is None:
        temperature = DATASET_DEFAULTS['temperature']; used_defaults.append('temperature')
    if soil_quality is None:
        soil_quality = DATASET_DEFAULTS['soil_quality']; used_defaults.append('soil_quality')
    if acre is None:
        acre = DATASET_DEFAULTS['acre']; used_defaults.append('acre')

    # Clamp to valid ranges
    rainfall     = max(0, min(4000, rainfall))
    temperature  = max(0, min(55, temperature))
    soil_quality = max(1, min(10, soil_quality))
    acre         = max(0.1, min(1000, acre))

    # Yield prediction
    yield_per_acre = predict_yield(rainfall, temperature, soil_quality, soil_type, crop_type)
    total_yield    = round(yield_per_acre * acre, 1)

    # Disease detection
    disease = pesticide = fertilizer = ""
    confidence = 0.0; image_path = None

    file = request.files.get('image')
    if file and file.filename:
        try:
            fname  = secure_filename(file.filename)
            folder = "static/uploads"; os.makedirs(folder, exist_ok=True)
            fpath  = os.path.join(folder, fname); file.save(fpath); image_path = fpath
            disease, pesticide, fertilizer, confidence = detect_disease(fpath, crop_type, soil_type)
        except Exception as e:
            print("Image error:", e)

    # No image → crop-specific realistic default disease
    if not disease:
        disease    = CROP_DEFAULT_DISEASE.get(crop_type, "Leaf Spot")
        from utils.disease import _get_solution
        pesticide, fertilizer = _get_solution(crop_type, disease)
        confidence = 0.0

    te_disease = DISEASE_TELUGU.get(disease, disease)
    te_crop    = CROP_TELUGU.get(crop_type, crop_type)
    te_soil    = SOIL_TELUGU.get(soil_type, soil_type)

    en_text = (f"Yield per acre: {yield_per_acre} kg. Total yield: {total_yield} kg. "
               f"Disease: {disease}. Treatment: {pesticide}. Fertilizer: {fertilizer}.")
    te_text = (f"ఎకరానికి దిగుబడి {yield_per_acre} కిలోలు. మొత్తం {total_yield} కిలోలు. "
               f"వ్యాధి: {te_disease}. మందు: {pesticide}. ఎరువు: {fertilizer}.")

    te_audio, en_audio = speak_tts(te_text, en_text)

    return render_template('result.html',
        crop_type=crop_type, crop_telugu=te_crop,
        soil_type=soil_type, soil_telugu=te_soil,
        yield_per_acre=yield_per_acre, total_yield=total_yield, acre=acre,
        rainfall=rainfall, temperature=temperature, soil_quality=soil_quality,
        disease=disease, disease_telugu=te_disease,
        pesticide=pesticide, fertilizer=fertilizer,
        confidence=round(confidence * 100, 1),
        image_path=image_path,
        te_audio=te_audio, en_audio=en_audio,
        en_text=en_text, te_text=te_text,
        used_defaults=used_defaults,
        is_approximate=len(used_defaults) > 0,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
