import os
import cohere
from flask import Flask, request, jsonify, render_template

# --- Configuration de l'API Key pour la production (COHERE) ---
api_key = os.environ.get('COHERE_API_KEY')

if not api_key:
    raise ValueError("La variable d'environnement COHERE_API_KEY n'est pas définie. Veuillez la configurer.")

co = cohere.Client(api_key)

app = Flask(__name__)

COHERE_MODEL = 'command'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    bride_name = data.get('brideName', '')
    groom_name = data.get('groomName', '')
    family_names_included = data.get('familyNamesIncluded', False)
    bride_family_names = data.get('brideFamilyNames', '')
    groom_family_names = data.get('groomFamilyNames', '')
    event_date = data.get('eventDate', '')
    event_country = data.get('eventCountry', '')
    event_city = data.get('eventCity', '')
    mairie_time = data.get('mairieTime', '')
    eglise_time = data.get('egliseTime', '')
    cocktail_included = data.get('cocktailIncluded', False)
    cocktail_location = data.get('cocktailLocation', '')
    cocktail_time = data.get('cocktailTime', '')
    reception_included = data.get('receptionIncluded', False)
    reception_location = data.get('receptionLocation', '')
    reception_time = data.get('receptionTime', '')
    style = data.get('style', 'moderne')
    specific_theme = data.get('specificTheme', '')
    additional_info = data.get('additionalInfo', '')
    feedback = data.get('feedback', '')
    previous_text = data.get('previousText', '')

    prompt_parts = []

    if feedback and previous_text:
        prompt_parts.append(f"Je vous ai demandé de générer un faire-part de mariage. Voici le texte que vous avez précédemment généré : \"\"\"{previous_text}\"\"\".")
        prompt_parts.append(f"Maintenant, merci de modifier ce texte en tenant compte du feedback suivant : \"\"\"{feedback}\"\"\".")
        prompt_parts.append("Assurez-vous de n'inclure que le texte final modifié dans votre réponse, sans préambule ni conclusion.")
    else:
        prompt_parts.append("Génère un texte de faire-part de mariage en français. Le ton doit être élégant et adapté au style choisi. Ne donne que le texte du faire-part, sans préambule ni conclusion.")
        prompt_parts.append(f"Les mariés sont {bride_name} et {groom_name}.")

        if family_names_included:
            if bride_family_names and groom_family_names:
                prompt_parts.append(f"Les familles de la mariée sont : {bride_family_names}. Les familles du marié sont : {groom_family_names}.")
            elif bride_family_names:
                prompt_parts.append(f"Les familles de la mariée sont : {bride_family_names}.")
            elif groom_family_names:
                prompt_parts.append(f"Les familles du marié sont : {groom_family_names}.")

        prompt_parts.append(f"La date de l'événement est le {event_date}.")
        prompt_parts.append(f"Les célébrations auront lieu à {event_city} en {event_country}.")

        if mairie_time:
            prompt_parts.append(f"La cérémonie civile (mairie) aura lieu à {mairie_time}.")
        if eglise_time:
            prompt_parts.append(f"La cérémonie religieuse (église) aura lieu à {eglise_time}.")

        if cocktail_included:
            prompt_parts.append(f"Un cocktail aura lieu à {cocktail_time} à {cocktail_location}.")
        if reception_included:
            prompt_parts.append(f"Une réception festive aura lieu à {reception_time} à {reception_location}.")

        prompt_parts.append(f"Le style souhaité est : {style}.")
        if specific_theme:
            prompt_parts.append(f"Le thème particulier est : {specific_theme}.")
        if additional_info:
            prompt_parts.append(f"Informations additionnelles à inclure : {additional_info}.")

    try:
        full_prompt = " ".join(prompt_parts)
        response = co.generate(
            model=COHERE_MODEL,
            prompt=full_prompt,
            max_tokens=500,
            temperature=0.7,
            stop_sequences=[]
        )
        generated_text = response.generations[0].text
        return jsonify({'text': generated_text})
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Cohere: {e}")
        return jsonify({'error': 'Erreur lors de la génération du texte. Veuillez réessayer.'}), 500