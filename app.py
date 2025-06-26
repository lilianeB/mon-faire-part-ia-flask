import os
import cohere
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)

# Assurez-vous que votre clé API Cohere est définie comme variable d'environnement
cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    # Cette erreur est levée si la clé n'est pas définie. Assurez-vous de la définir.
    raise ValueError("La variable d'environnement COHERE_API_KEY n'est pas définie. Veuillez la configurer.")

co = cohere.Client(cohere_api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_text():
    try:
        data = request.json
        print("Received data from frontend:", data) # Debugging line

        bride_name = data.get('brideName', '')
        groom_name = data.get('groomName', '')
        event_date = data.get('eventDate', '')
        event_city = data.get('eventCity', '') # Assurez-vous que cette donnée est envoyée par le frontend si nécessaire
        mairie_time = data.get('mairieTime', '')
        church_wedding = data.get('churchWedding', 'non')
        church_date = data.get('churchDate', '')
        church_time = data.get('churchTime', '')
        cocktail_included = data.get('cocktailIncluded', False)
        cocktail_location = data.get('cocktailLocation', '')
        cocktail_time = data.get('cocktailTime', '')
        reception_included = data.get('receptionIncluded', False)
        reception_location = data.get('receptionLocation', '')
        reception_time = data.get('receptionTime', '')
        brunch_included = data.get('brunchIncluded', False)
        brunch_location = data.get('brunchLocation', '')
        brunch_time = data.get('brunchTime', '')
        style = data.get('style', 'classique')
        specific_theme = data.get('specificTheme', '')
        additional_info = data.get('additionalInfo', '')
        feedback = data.get('feedback', '')
        previous_text = data.get('previousText', '')

        prompt = f"Rédige UNIQUEMENT le texte d'une annonce de mariage. N'ajoute aucun préambule, aucune salutation, et aucune note ou conclusion non pertinente au texte de l'annonce lui-même. Le texte doit être prêt à être copié/collé directement.\n"
        prompt += f"En tant qu'écrivain talentueux de génie très prolifique, capable d'écrire avec brio, rédige un texte exceptionnel, original, et percutant. Assure-toi qu'il n'y ait aucune faute de grammaire, d'orthographe, ou de vocabulaire. Évite toute redondance de mots ou de tournures. Les phrases doivent être fluides, avoir un sens parfait et une élégance irréprochable.\n"

        # Instructions de style basées sur le choix de l'utilisateur
        if style == 'romantique':
            prompt += f"Le ton doit être romantique, poétique et élégant. Le style doit faire ressentir la profondeur des sentiments, la tendresse, l’amour vrai, sans tomber dans le cliché ni le sirupeux. Vise entre 700 et 1000 caractères (espaces inclus). Suis la structure suivante, en intégrant chaque élément dans un texte fluide, sans lister ni isoler les infos pratiques. Le tout doit sonner comme une lettre d’amour partagée avec les proches : - Une phrase d’ouverture émotionnelle (poétique ou symbolique) - Noms des mariés - Annonce du mariage (\"ont la joie de vous faire part…\") - Date complète du mariage - Déroulé du jour (lieux + horaires de la mairie, cérémonie, cocktail, dîner, brunch…) - Mot d’ambiance (saison, nature du lieu, esprit de la journée) - RSVP (date limite + contact) - Tenue vestimentaire si nécessaire - Autres infos pratiques (hébergement, navette, contacts utiles).\n"
        elif style == 'classique':
            prompt += f"Le ton doit être classique et traditionnel, sobre, respectueux et formel, convenant à toutes les générations. Vise entre 600 et 800 caractères (espaces inclus). Suis la structure suivante, en intégrant les informations de manière claire, fluide et posée. Pas d'humour ni de trop plein d’émotion : on reste dans l’élégance discrète : - Noms des mariés - Formule d’annonce du mariage (\"ont la joie de vous faire part du mariage de leurs enfants…\") - Date complète du mariage - Déroulé du jour avec lieux et horaires (mairie, église/cérémonie, réception, brunch…) - Formule de clôture polie (\"Nous serions honorés de vous compter parmi nous\") - RSVP avec date limite + contact - Dress code ou consigne tenue si nécessaire - Autres infos pratiques (hébergement, navette, contact) intégrées en fin de texte.\n"
        elif style == 'glamour':
            prompt += f"Le ton doit être glamour, raffiné et évocateur, comme l’annonce d’un événement chic et marquant. Le style doit être élégant, stylisé, sans être pompeux. Vise entre 800 et 1100 caractères (espaces inclus). Suis la structure suivante. Le texte doit faire rêver, mais rester précis. Aucune info ne doit être présentée de manière brute — chaque détail doit se fondre dans la narration. Commencez par une accroche percutante (citation, phrase forte, image). Enchaînez sur les noms des mariés, puis sur la date et le déroulé de la journée, en évitant les listes. Intégrez les informations pratiques (lieux, horaires, RSVP, tenue) de manière discrète et sophistiquée.\n"
        elif style == 'humoristique':
            prompt += f"Le ton doit être humoristique, léger et décalé, pour un mariage joyeux et plein de surprises. Le style doit être pétillant, amusant, sans être lourd ou grossier. Vise entre 700 et 1000 caractères (espaces inclus). Suis la structure suivante, en intégrant les informations pratiques avec une touche d'humour. Le texte doit faire sourire et donner envie de participer à la fête : - Accroche originale et drôle - Noms des mariés (avec une touche d'autodérision si possible) - Annonce du mariage (avec une formule inattendue) - Date et déroulé du jour (lieux et horaires présentés de manière ludique) - RSVP (avec une note amusante sur la date limite) - Dress code (avec des suggestions fantaisistes ou décalées) - Autres infos pratiques (hébergement, navette, contacts) intégrées de façon légère.\n"
        elif style == 'original':
            prompt += f"Le ton doit être original, créatif et unique, pour un mariage qui sort de l'ordinaire. Le style doit être innovant, surprenant, sans être obscur ou incompréhensible. Vise entre 800 et 1200 caractères (espaces inclus). Suis la structure suivante, en intégrant les informations pratiques de manière non conventionnelle. Le texte doit marquer les esprits et refléter la personnalité des mariés : - Accroche inattendue (énigme, début d'histoire, question) - Noms des mariés (avec un surnom ou une description poétique) - Annonce du mariage (avec une métaphore ou une analogie) - Date et déroulé du jour (lieux et horaires présentés de manière narrative ou sous forme de \"chapitres\") - RSVP (avec un appel à l'action créatif) - Dress code (avec une thématique originale) - Autres infos pratiques (hébergement, navette, contacts) intégrées de façon artistique.\n"
        elif style == 'elegant':
            prompt += f"Le ton doit être élégant, sobre et raffiné, pour un mariage sophistiqué et intemporel. Le style doit être distingué, classique, sans être austère. Vise entre 600 et 900 caractères (espaces inclus). Suis la structure suivante, en intégrant les informations pratiques avec discrétion et harmonie. Le texte doit refléter le bon goût et la solennité de l'événement : - Accroche distinguée - Noms des mariés - Annonce du mariage (avec une formule classique et belle) - Date et déroulé du jour (lieux et horaires présentés avec clarté et élégance) - RSVP (avec une formulation polie) - Dress code (avec des suggestions de tenue appropriées) - Autres infos pratiques (hébergement, navette, contacts) intégrées avec finesse.\n"
        else: # Style par défaut si non reconnu
            prompt += f"Le ton doit être élégant et clair. Vise entre 600 et 900 caractères (espaces inclus). Suis la structure suivante : Noms des mariés - Annonce du mariage - Date complète du mariage - Déroulé du jour (lieux et horaires de la mairie, église/cérémonie, cocktail, dîner, brunch) - RSVP (date limite + contact) - Tenue vestimentaire si nécessaire - Autres infos pratiques (hébergement, navette, contacts utiles).\n"

        # Ajout des informations spécifiques au prompt
        prompt += f"Informations spécifiques : Mariée: {bride_name}, Marié: {groom_name}. "
        prompt += f"Date du mariage civil: {event_date}. Heure de la mairie: {mairie_time}. "

        if church_wedding == 'oui':
            prompt += f"Mariage à l'église: Oui. Date de l'église: {church_date}. Heure de l'église: {church_time}. "
        else:
            prompt += f"Mariage à l'église: Non. "

        if cocktail_included:
            prompt += f"Cocktail: Oui. Lieu du cocktail: {cocktail_location}. Heure du cocktail: {cocktail_time}. "
        else:
            prompt += f"Cocktail: Non. "

        if reception_included:
            prompt += f"Réception: Oui. Lieu de la réception: {reception_location}. Heure de la réception: {reception_time}. "
        else:
            prompt += f"Réception: Non. "

        if brunch_included:
            prompt += f"Brunch le lendemain: Oui. Lieu du brunch: {brunch_location}. Heure du brunch: {brunch_time}. "
        else:
            prompt += f"Brunch le lendemain: Non. "

        if specific_theme:
            prompt += f"Thème spécifique: {specific_theme}. "

        if additional_info:
            prompt += f"Informations complémentaires: {additional_info}. "

        if feedback:
            prompt += f"Modifications demandées par l'utilisateur pour le texte précédent: \"{feedback}\". Le texte précédent à modifier était : \"{previous_text}\". Intègre ces modifications dans la nouvelle version du texte. "

        print("Sending prompt to Cohere:", prompt) # Debugging line

        response = co.generate(
            model='command-r-plus', # Modèle Cohere à utiliser
            prompt=prompt,
            max_tokens=1500, # Augmenté la limite de tokens pour permettre un texte plus long et complet
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        generated_text = response.generations[0].text
        return jsonify({'text': generated_text})

    except cohere.CohereAPIError as e:
        print(f"Cohere API Error: {e}")
        # En cas d'erreur de l'API Cohere, renvoyer un message d'erreur clair
        return jsonify({'error': f"Erreur de l'API Cohere : {str(e)}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Pour obtenir plus de détails sur l'erreur
        return jsonify({'error': f"Une erreur inattendue est survenue côté serveur : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)