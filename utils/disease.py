import os, base64, json, urllib.request

# ══════════════════════════════════════════════════════════════
#  Comprehensive disease + fertilizer database
#  Covers all 20 crops in the app
# ══════════════════════════════════════════════════════════════
CROP_DISEASE_DB = {
    # ── RICE ──────────────────────────────────────────────────
    "rice": {
        "diseases": ["Rice Blast","Bacterial Leaf Blight","Brown Spot","Sheath Blight","False Smut","Healthy"],
        "disease_info": {
            "Rice Blast":            {"pesticide":"Tricyclazole 75 WP @ 0.6 g/L",   "fertilizer":"Calcium Silicate + Potassium Chloride (avoid excess N)"},
            "Bacterial Leaf Blight": {"pesticide":"Copper Oxychloride 50 WP @ 3 g/L","fertilizer":"Potassium Nitrate @ 2 g/L"},
            "Brown Spot":            {"pesticide":"Mancozeb 75 WP @ 2.5 g/L",        "fertilizer":"Zinc Sulfate + Potassium (address K deficiency)"},
            "Sheath Blight":         {"pesticide":"Validamycin 3 SL @ 2 ml/L",       "fertilizer":"NPK 15-15-15 balanced"},
            "False Smut":            {"pesticide":"Propiconazole 25 EC @ 1 ml/L",    "fertilizer":"NPK 10-10-10 (reduce N at heading)"},
            "Healthy":               {"pesticide":"No spray needed",                  "fertilizer":"NPK 19-19-19 maintenance"},
        }
    },
    # ── TOMATO ────────────────────────────────────────────────
    "tomato": {
        "diseases": ["Late Blight","Early Blight","Leaf Mold","Septoria Leaf Spot","Yellow Leaf Curl Virus","Spider Mites","Healthy"],
        "disease_info": {
            "Late Blight":           {"pesticide":"Metalaxyl+Mancozeb (Ridomil Gold) @ 2.5 g/L","fertilizer":"Potassium Phosphonate 3 ml/L + Calcium Nitrate"},
            "Early Blight":          {"pesticide":"Mancozeb 75 WP @ 2.5 g/L",                   "fertilizer":"NPK 10-10-10 + Magnesium Sulfate 2 g/L"},
            "Leaf Mold":             {"pesticide":"Copper Hydroxide 77 WP @ 2 g/L",              "fertilizer":"Potassium Silicate 2 ml/L + NPK 12-6-22"},
            "Septoria Leaf Spot":    {"pesticide":"Chlorothalonil 75 WP @ 2 ml/L",               "fertilizer":"Zinc Sulfate 0.5 g/L + Potassium Humate"},
            "Yellow Leaf Curl Virus":{"pesticide":"Imidacloprid 200 SL @ 0.5 ml/L (whitefly)",  "fertilizer":"NPK 19-19-19 + Boron 0.2 g/L"},
            "Spider Mites":          {"pesticide":"Abamectin 1.8 EC @ 0.5 ml/L",                 "fertilizer":"Potassium Silicate 2 ml/L"},
            "Healthy":               {"pesticide":"No spray needed",                              "fertilizer":"NPK 19-19-19 maintenance + micronutrients"},
        }
    },
    # ── POTATO ────────────────────────────────────────────────
    "potato": {
        "diseases": ["Late Blight","Early Blight","Black Scurf","Common Scab","Healthy"],
        "disease_info": {
            "Late Blight":  {"pesticide":"Metalaxyl+Mancozeb @ 2.5 g/L",    "fertilizer":"Potassium Phosphonate 5 ml/L + Calcium Chloride"},
            "Early Blight": {"pesticide":"Iprodione 50 WP @ 1.5 ml/L",      "fertilizer":"Urea foliar 5 g/L + Magnesium Nitrate"},
            "Black Scurf":  {"pesticide":"Thiram 75 WS seed treatment",      "fertilizer":"Potassium Sulfate + Boron micronutrient"},
            "Common Scab":  {"pesticide":"PCNB (Quintozene) soil drench",    "fertilizer":"Acidifying fertilizers (Ammonium Sulfate), avoid excess K"},
            "Healthy":      {"pesticide":"No spray needed",                  "fertilizer":"NPK 15-15-15 + Zinc micronutrient"},
        }
    },
    # ── MAIZE / CORN ─────────────────────────────────────────
    "maize": {
        "diseases": ["Common Rust","Northern Leaf Blight","Gray Leaf Spot","Downy Mildew","Stalk Rot","Healthy"],
        "disease_info": {
            "Common Rust":        {"pesticide":"Tebuconazole 25.9 EC @ 1 ml/L",          "fertilizer":"NPK 28-0-0 + Sulfur 80 WG"},
            "Northern Leaf Blight":{"pesticide":"Propiconazole 25 EC @ 1.5 ml/L",        "fertilizer":"NPK 15-15-15 + Silicic Acid 2 ml/L"},
            "Gray Leaf Spot":     {"pesticide":"Azoxystrobin+Propiconazole @ 1.5 ml/L",  "fertilizer":"Potassium Sulfate + Zinc EDTA"},
            "Downy Mildew":       {"pesticide":"Metalaxyl 35 SD @ 6 g/kg seed",          "fertilizer":"Phosphoric Acid + Potassium (reduce N)"},
            "Stalk Rot":          {"pesticide":"Carbendazim 50 WP soil drench",           "fertilizer":"Potassium + Calcium; avoid excess N"},
            "Healthy":            {"pesticide":"No spray needed",                         "fertilizer":"NPK 20-10-10 maintenance"},
        }
    },
    # ── WHEAT ─────────────────────────────────────────────────
    "wheat": {
        "diseases": ["Stripe Rust","Leaf Rust","Stem Rust","Loose Smut","Powdery Mildew","Healthy"],
        "disease_info": {
            "Stripe Rust":    {"pesticide":"Propiconazole+Tebuconazole @ 1.5 ml/L","fertilizer":"NPK 20-10-10 + Sulfur 15 kg/ha"},
            "Leaf Rust":      {"pesticide":"Tebuconazole 25.9 EC @ 1 ml/L",        "fertilizer":"NPK 15-15-15 + Silicon foliar"},
            "Stem Rust":      {"pesticide":"Mancozeb+Propiconazole @ 2 ml/L",      "fertilizer":"Potassium Chloride + balanced NPK"},
            "Loose Smut":     {"pesticide":"Carboxin+Thiram seed treatment",        "fertilizer":"Zinc Sulfate + Urea (balanced N)"},
            "Powdery Mildew": {"pesticide":"Sulfur 80 WG @ 3 g/L",                 "fertilizer":"Potassium Silicate + reduce N"},
            "Healthy":        {"pesticide":"No spray needed",                       "fertilizer":"NPK 15-15-15 + micronutrients"},
        }
    },
    # ── COTTON ────────────────────────────────────────────────
    "cotton": {
        "diseases": ["Bacterial Blight","Alternaria Leaf Spot","Fusarium Wilt","Bollworm Damage","Healthy"],
        "disease_info": {
            "Bacterial Blight":    {"pesticide":"Copper Oxychloride 50 WP @ 3 g/L","fertilizer":"Potassium Nitrate + Zinc Sulfate"},
            "Alternaria Leaf Spot":{"pesticide":"Mancozeb 75 WP @ 2.5 g/L",       "fertilizer":"NPK 10-10-10 + Boron micronutrient"},
            "Fusarium Wilt":       {"pesticide":"Carbendazim 50 WP soil drench",   "fertilizer":"Potassium Sulfate (avoid excess N)"},
            "Bollworm Damage":     {"pesticide":"Spinosad 45 SC @ 0.3 ml/L",       "fertilizer":"NPK 20-10-20 + Calcium Nitrate"},
            "Healthy":             {"pesticide":"No spray needed",                  "fertilizer":"NPK 20-10-20 maintenance + micronutrients"},
        }
    },
    # ── SOYBEAN ───────────────────────────────────────────────
    "soybean": {
        "diseases": ["Asian Soybean Rust","Frogeye Leaf Spot","Sudden Death Syndrome","Bacterial Pustule","Healthy"],
        "disease_info": {
            "Asian Soybean Rust":      {"pesticide":"Azoxystrobin+Tebuconazole @ 1 ml/L","fertilizer":"Potassium Chloride + Zinc"},
            "Frogeye Leaf Spot":       {"pesticide":"Thiophanate-methyl 70 WP @ 1.5 g/L","fertilizer":"NPK 10-20-10 + Manganese"},
            "Sudden Death Syndrome":   {"pesticide":"Fluopyram soil drench",              "fertilizer":"Calcium Silicate + reduce excess N"},
            "Bacterial Pustule":       {"pesticide":"Copper Hydroxide @ 2.5 g/L",         "fertilizer":"Potassium Nitrate + balanced NPK"},
            "Healthy":                 {"pesticide":"No spray needed",                     "fertilizer":"NPK 10-20-10 + Rhizobium inoculant"},
        }
    },
    # ── GROUNDNUT ─────────────────────────────────────────────
    "groundnut": {
        "diseases": ["Tikka Disease (Leaf Spot)","Rust","Stem Rot (Collar Rot)","Peanut Mottle Virus","Healthy"],
        "disease_info": {
            "Tikka Disease (Leaf Spot)":{"pesticide":"Mancozeb 75 WP @ 2.5 g/L",     "fertilizer":"Gypsum (Ca+S) + NPK 10-26-26"},
            "Rust":                      {"pesticide":"Chlorothalonil 75 WP @ 2 g/L", "fertilizer":"Potassium Sulfate + balanced NPK"},
            "Stem Rot (Collar Rot)":     {"pesticide":"Carbendazim+Mancozeb @ 2 g/L", "fertilizer":"Gypsum soil application + Trichoderma"},
            "Peanut Mottle Virus":       {"pesticide":"Imidacloprid (aphid control)",  "fertilizer":"NPK 10-26-26 + Zinc micronutrient"},
            "Healthy":                   {"pesticide":"No spray needed",               "fertilizer":"NPK 10-26-26 + Gypsum 200 kg/ha"},
        }
    },
    # ── SUGARCANE ─────────────────────────────────────────────
    "sugarcane": {
        "diseases": ["Red Rot","Smut","Grassy Shoot (Phytoplasma)","Pokkah Boeng","Rust","Healthy"],
        "disease_info": {
            "Red Rot":                {"pesticide":"Carbendazim 50 WP sett treatment","fertilizer":"Potassium Silicate + NPK 30-15-15"},
            "Smut":                   {"pesticide":"Propiconazole 25 EC @ 1 ml/L",   "fertilizer":"Balanced NPK; avoid excess N"},
            "Grassy Shoot (Phytoplasma)":{"pesticide":"Hot water sett treatment 52°C","fertilizer":"NPK 30-15-15 + Zinc"},
            "Pokkah Boeng":           {"pesticide":"Mancozeb+Carbendazim @ 2 g/L",   "fertilizer":"Potassium Sulfate + reduce N"},
            "Rust":                   {"pesticide":"Propiconazole 25 EC @ 1 ml/L",   "fertilizer":"NPK 30-15-15 + Sulfur"},
            "Healthy":                {"pesticide":"No spray needed",                 "fertilizer":"NPK 30-15-15 + Zinc + Boron"},
        }
    },
    # ── GREEN GRAM (MOONG) ────────────────────────────────────
    "green gram": {
        "diseases": ["Powdery Mildew","Yellow Mosaic Virus","Cercospora Leaf Spot","Anthracnose","Healthy"],
        "disease_info": {
            "Powdery Mildew":        {"pesticide":"Sulfur 80 WG @ 3 g/L",              "fertilizer":"Potassium Silicate 2 ml/L + DAP"},
            "Yellow Mosaic Virus":   {"pesticide":"Imidacloprid (whitefly control)",   "fertilizer":"NPK 10-26-26 + Zinc"},
            "Cercospora Leaf Spot":  {"pesticide":"Carbendazim 50 WP @ 1.5 g/L",      "fertilizer":"Balanced NPK + Manganese"},
            "Anthracnose":           {"pesticide":"Mancozeb+Carbendazim @ 2 g/L",      "fertilizer":"Potassium Nitrate + Zinc"},
            "Healthy":               {"pesticide":"No spray needed",                   "fertilizer":"NPK 10-26-26 + Rhizobium inoculant"},
        }
    },
    # ── CHILLI ────────────────────────────────────────────────
    "chilli": {
        "diseases": ["Powdery Mildew","Leaf Curl Virus","Fruit Rot (Anthracnose)","Bacterial Wilt","Healthy"],
        "disease_info": {
            "Powdery Mildew":         {"pesticide":"Hexaconazole 5 EC @ 1 ml/L",       "fertilizer":"Potassium Silicate + NPK 12-6-22"},
            "Leaf Curl Virus":        {"pesticide":"Imidacloprid+Neem Oil spray",       "fertilizer":"NPK 19-19-19 + Boron 0.2 g/L"},
            "Fruit Rot (Anthracnose)":{"pesticide":"Azoxystrobin 23 SC @ 1 ml/L",      "fertilizer":"Calcium Nitrate 2 g/L + Potassium"},
            "Bacterial Wilt":         {"pesticide":"Copper Hydroxide soil drench",      "fertilizer":"Potassium Nitrate + Calcium Silicate"},
            "Healthy":                {"pesticide":"No spray needed",                   "fertilizer":"NPK 12-6-22 maintenance + micronutrients"},
        }
    },
    # ── JOWAR (SORGHUM) ───────────────────────────────────────
    "jowar": {
        "diseases": ["Grain Mold","Downy Mildew","Anthracnose","Rust","Healthy"],
        "disease_info": {
            "Grain Mold":    {"pesticide":"Mancozeb+Carbendazim @ 2 g/L",  "fertilizer":"Potassium Sulfate + DAP"},
            "Downy Mildew":  {"pesticide":"Metalaxyl 35 SD seed treatment","fertilizer":"Phosphoric Acid + Potassium"},
            "Anthracnose":   {"pesticide":"Thiophanate-methyl 70 WP @ 1 g/L","fertilizer":"Balanced NPK + Zinc"},
            "Rust":          {"pesticide":"Propiconazole 25 EC @ 1 ml/L",  "fertilizer":"NPK 20-10-10 + Sulfur"},
            "Healthy":       {"pesticide":"No spray needed",               "fertilizer":"NPK 20-10-10 maintenance"},
        }
    },
    # ── SUNFLOWER ─────────────────────────────────────────────
    "sunflower": {
        "diseases": ["Downy Mildew","Alternaria Blight","Sclerotinia Wilt","Rust","Healthy"],
        "disease_info": {
            "Downy Mildew":     {"pesticide":"Metalaxyl 35 SD @ 6 g/kg seed","fertilizer":"Potassium Phosphonate 3 ml/L"},
            "Alternaria Blight":{"pesticide":"Mancozeb 75 WP @ 2.5 g/L",   "fertilizer":"NPK 10-26-26 + Boron"},
            "Sclerotinia Wilt": {"pesticide":"Carbendazim 50 WP @ 1 g/L",  "fertilizer":"Potassium Sulfate + Calcium Nitrate"},
            "Rust":             {"pesticide":"Propiconazole 25 EC @ 1 ml/L","fertilizer":"NPK 10-26-26 + Sulfur"},
            "Healthy":          {"pesticide":"No spray needed",             "fertilizer":"NPK 10-26-26 + Boron 0.3 g/L"},
        }
    },
    # ── TURMERIC ──────────────────────────────────────────────
    "turmeric": {
        "diseases": ["Rhizome Rot","Leaf Blotch","Leaf Spot","Bacterial Wilt","Healthy"],
        "disease_info": {
            "Rhizome Rot":  {"pesticide":"Metalaxyl+Mancozeb @ 2.5 g/L (drench)","fertilizer":"Potassium Silicate + Boron (avoid waterlogging)"},
            "Leaf Blotch":  {"pesticide":"Mancozeb 75 WP @ 2.5 g/L",             "fertilizer":"Balanced NPK + Zinc"},
            "Leaf Spot":    {"pesticide":"Chlorothalonil 75 WP @ 2 g/L",         "fertilizer":"NPK 10-26-26 + Magnesium"},
            "Bacterial Wilt":{"pesticide":"Copper Hydroxide drench + destroy plants","fertilizer":"Potassium Nitrate + Gypsum"},
            "Healthy":      {"pesticide":"No spray needed",                       "fertilizer":"NPK 10-26-26 + Neem cake soil amendment"},
        }
    },
    # ── RED GRAM (PIGEON PEA / ARHAR DAL) ────────────────────
    "red gram": {
        "diseases": ["Fusarium Wilt","Sterility Mosaic","Phytophthora Blight","Leaf Spot","Healthy"],
        "disease_info": {
            "Fusarium Wilt":       {"pesticide":"Carbendazim 50 WP soil drench",  "fertilizer":"Potassium Sulfate (avoid excess N)"},
            "Sterility Mosaic":    {"pesticide":"Imidacloprid (mite control)",    "fertilizer":"NPK 10-26-26 + Zinc + Boron"},
            "Phytophthora Blight": {"pesticide":"Metalaxyl+Mancozeb @ 2.5 g/L", "fertilizer":"Potassium Phosphonate 3 ml/L"},
            "Leaf Spot":           {"pesticide":"Mancozeb 75 WP @ 2.5 g/L",     "fertilizer":"Balanced NPK + Manganese"},
            "Healthy":             {"pesticide":"No spray needed",               "fertilizer":"NPK 10-26-26 + Rhizobium inoculant"},
        }
    },
    # ── BARLEY ────────────────────────────────────────────────
    "barley": {
        "diseases": ["Powdery Mildew","Net Blotch","Stripe Rust","Scald","Healthy"],
        "disease_info": {
            "Powdery Mildew":{"pesticide":"Sulfur 80 WG @ 3 g/L",             "fertilizer":"Potassium Silicate + reduce N"},
            "Net Blotch":    {"pesticide":"Propiconazole 25 EC @ 1 ml/L",     "fertilizer":"Balanced NPK + Zinc"},
            "Stripe Rust":   {"pesticide":"Tebuconazole 25.9 EC @ 1 ml/L",   "fertilizer":"NPK 20-10-10 + Sulfur"},
            "Scald":         {"pesticide":"Mancozeb 75 WP @ 2.5 g/L",        "fertilizer":"Balanced NPK + Silicon"},
            "Healthy":       {"pesticide":"No spray needed",                  "fertilizer":"NPK 15-15-15 maintenance"},
        }
    },
}

# Alias map so variations in crop name still hit the DB
_CROP_ALIASES = {
    "corn":"maize","paddy":"rice","chillies":"chilli","chili":"chilli",
    "millet":"jowar","sorghum":"jowar","moong":"green gram","pesalu":"green gram",
    "peanut":"groundnut","groundnuts":"groundnut","arhar":"red gram",
    "toor":"red gram","pigeon pea":"red gram","tur":"red gram",
}

def _resolve_crop(crop_type: str) -> str:
    c = crop_type.lower().strip()
    return _CROP_ALIASES.get(c, c)

def _image_to_base64(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png',
                '.webp':'image/webp','.gif':'image/gif','.avif':'image/webp'}
    media_type = mime_map.get(ext,'image/jpeg')
    with open(image_path,'rb') as f:
        data_b64 = base64.standard_b64encode(f.read()).decode('utf-8')
    return data_b64, media_type


def _call_claude_vision(image_path: str, crop_type: str):
    """
    Ask Claude claude-sonnet-4 to diagnose the disease from the actual image.
    Returns dict with disease/confidence/symptoms/severity or None on failure.
    """
    crop_key = _resolve_crop(crop_type)
    crop_info = CROP_DISEASE_DB.get(crop_key)
    if not crop_info:
        # Generic fallback list if crop not in DB
        disease_list = "Leaf Blight, Rust, Powdery Mildew, Leaf Spot, Healthy"
    else:
        disease_list = ", ".join(crop_info["diseases"])

    try:
        data_b64, media_type = _image_to_base64(image_path)

        prompt = (
            f"You are a senior plant pathologist specializing in {crop_type} crops.\n"
            f"Examine this image CAREFULLY and identify the exact disease based on what you ACTUALLY SEE.\n"
            f"Possible conditions for {crop_type}: {disease_list}\n\n"
            "Look for: lesion shapes, colors, spots, pustules, mold, curling, yellowing, wilting, "
            "necrotic areas, water-soaking, powder/spores, or any abnormality.\n\n"
            "IMPORTANT: Base your answer ONLY on the visual evidence in THIS specific image. "
            "Different images show different diseases. Do NOT assume a default disease.\n\n"
            "Respond ONLY with valid JSON (no markdown, no extra text):\n"
            '{"disease":"<exact name from list above>","confidence":<0.0-1.0>,'
            '"symptoms_observed":"<2-4 specific visual features you actually see>","severity":"<none|mild|moderate|severe>"}'
        )

        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 400,
            "messages": [{
                "role": "user",
                "content": [
                    {"type":"image","source":{"type":"base64","media_type":media_type,"data":data_b64}},
                    {"type":"text","text":prompt}
                ]
            }]
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": os.environ.get("ANTHROPIC_API_KEY","")
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            response_data = json.loads(resp.read().decode('utf-8'))

        text_content = ""
        for block in response_data.get("content",[]):
            if block.get("type") == "text":
                text_content += block.get("text","")
        text_content = text_content.strip().replace("```json","").replace("```","").strip()

        result = json.loads(text_content)
        return {
            "disease":    result.get("disease","Healthy"),
            "confidence": float(result.get("confidence", 0.75)),
            "symptoms":   result.get("symptoms_observed",""),
            "severity":   result.get("severity","none")
        }

    except Exception as e:
        print(f"[disease.py] Claude Vision error: {e}")
        return None


def _get_solution(crop_type: str, disease: str):
    """
    Look up pesticide + fertilizer for a specific disease from the DB.
    """
    crop_key = _resolve_crop(crop_type)
    crop_info = CROP_DISEASE_DB.get(crop_key, {})
    disease_info = crop_info.get("disease_info", {})

    # Exact match first
    if disease in disease_info:
        info = disease_info[disease]
        return info["pesticide"], info["fertilizer"]

    # Fuzzy match
    dl = disease.lower()
    for key, info in disease_info.items():
        if dl in key.lower() or key.lower() in dl:
            return info["pesticide"], info["fertilizer"]

    # Healthy fallback
    healthy = disease_info.get("Healthy", {})
    return healthy.get("pesticide","No spray needed"), healthy.get("fertilizer","NPK balanced")


def detect_disease(image_path: str, crop_type: str, soil_type: str):
    """
    Main entry point. Returns (disease, pesticide, fertilizer, confidence).
    """
    crop_type = str(crop_type).lower().strip()

    # 1 ── Claude Vision
    vision = _call_claude_vision(image_path, crop_type)
    if vision:
        disease    = vision["disease"]
        confidence = vision["confidence"]
        symptoms   = vision.get("symptoms","")
        print(f"[disease.py] Claude Vision → {disease} conf={confidence:.2f} | {symptoms}")
    else:
        # 2 ── Simple colour heuristic fallback
        disease, confidence = _colour_heuristic(image_path, crop_type)
        print(f"[disease.py] Colour fallback → {disease} conf={confidence:.2f}")

    pesticide, fertilizer = _get_solution(crop_type, disease)
    print(f"[disease.py] FINAL → disease={disease} pesticide={pesticide}")
    return disease, pesticide, fertilizer, confidence


def _colour_heuristic(image_path: str, crop_type: str):
    """Basic colour-based fallback when API unavailable."""
    try:
        from PIL import Image
        import numpy as np, colorsys
        img = Image.open(image_path).convert('RGB').resize((64,64))
        px  = np.array(img, dtype=float)/255.0
        hs  = [colorsys.rgb_to_hsv(*px[r,c]) for r in range(64) for c in range(64)]
        h  = float(np.mean([x[0] for x in hs]))
        s  = float(np.mean([x[1] for x in hs]))
        v  = float(np.mean([x[2] for x in hs]))
        r  = float(np.mean(px[:,:,0]))
        g  = float(np.mean(px[:,:,1]))

        crop_key  = _resolve_crop(crop_type)
        crop_info = CROP_DISEASE_DB.get(crop_key,{})
        diseases  = crop_info.get("diseases",["Healthy"])

        if s < 0.15 and v > 0.75 and any("Mildew" in d for d in diseases):
            return "Powdery Mildew", 0.55
        if 0.08 <= h <= 0.18 and s > 0.3:
            for d in diseases:
                if "Blight" in d or "Spot" in d:
                    return d, 0.55
        if (h < 0.08 or h > 0.90) and s > 0.3:
            for d in diseases:
                if "Rust" in d:
                    return d, 0.55
        if r > 0.45 and g < 0.40:
            for d in diseases:
                if "Rot" in d or "Wilt" in d:
                    return d, 0.52
        if g > 0.45 and s > 0.3:
            return "Healthy", 0.60
        return diseases[0] if diseases else "Healthy", 0.48
    except Exception as e:
        print(f"[disease.py] Colour heuristic error: {e}")
        return "Healthy", 0.48
