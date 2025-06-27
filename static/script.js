document.addEventListener('DOMContentLoaded', () => {
    const steps = [
        'introStep', 'namesStep', 'familyNamesOptionStep',
        'brideFamilyStep', 'groomFamilyStep', 'dateStep',
        'locationStep', 'mairieTimeStep', 'egliseTimeStep',
        'cocktailOptionStep', 'cocktailDetailsStep',
        'receptionOptionStep', 'receptionDetailsStep',
        'styleStep', 'additionalInfoStep', 'resultStep',
        'secretQuestionResponse'
    ];
    let currentStepIndex = 0;
    let currentFormData = {};

    function showStep(stepId) {
        steps.forEach(id => {
            document.getElementById(id).classList.add('hidden');
        });
        document.getElementById(stepId).classList.remove('hidden');
        currentStepIndex = steps.indexOf(stepId);

        const progressBarContainer = document.getElementById('progressBarContainer');
        const progressBarFill = document.getElementById('progressBar');

        if (progressBarContainer && progressBarFill) {
            const mappableSteps = steps.filter(id => !['introStep', 'resultStep', 'secretQuestionResponse'].includes(id));
            const currentMappedIndex = mappableSteps.indexOf(stepId);

            if (currentMappedIndex !== -1) {
                progressBarContainer.classList.remove('hidden');
                const progressPercentage = ((currentMappedIndex + 1) / mappableSteps.length) * 100;
                progressBarFill.style.width = `${progressPercentage}%`;
            } else {
                progressBarContainer.classList.add('hidden');
                progressBarFill.style.width = '0%';
            }
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function setupNextButton(buttonId, nextStepId, condition = () => true) {
        document.getElementById(buttonId).addEventListener('click', () => {
            if (condition()) {
                updateFormData();
                showStep(nextStepId);
            }
        });
    }

    function updateFormData() {
        currentFormData = {
            brideName: document.getElementById('brideName').value,
            groomName: document.getElementById('groomName').value,
            familyNamesIncluded: document.getElementById('familyNamesYes').checked,
            brideFamilyNames: document.getElementById('brideFamilyNames').value,
            groomFamilyNames: document.getElementById('groomFamilyNames').value,
            eventDate: document.getElementById('eventDate').value,
            eventCountry: document.getElementById('eventCountry').value,
            eventCity: document.getElementById('eventCity').value,
            mairieTime: document.getElementById('mairieTime').value,
            egliseTime: document.getElementById('egliseTime').value,
            cocktailIncluded: document.getElementById('cocktailYes').checked,
            cocktailLocation: document.getElementById('cocktailLocation').value,
            cocktailTime: document.getElementById('cocktailTime').value,
            receptionIncluded: document.getElementById('receptionYes').checked,
            receptionLocation: document.getElementById('receptionLocation').value,
            receptionTime: document.getElementById('receptionTime').value,
            style: document.querySelector('.style-button.selected')?.dataset.style || 'moderne',
            specificTheme: document.getElementById('specificTheme').value,
            additionalInfo: document.getElementById('additionalInfo').value
        };
    }

    async function callGenerateAPI(payload, retries = 3, delay = 2000) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.status === 429) {
                    console.warn(`Quota API atteint ou trop de requêtes. Tentative de réessai ${i + 1}/${retries} dans ${delay / 1000} secondes...`);
                    await new Promise(res => setTimeout(res, delay));
                    delay *= 2;
                    continue;
                }

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error(`Erreur lors de la requête API (tentative ${i + 1}/${retries}):`, error);
                if (i < retries - 1) {
                    await new Promise(res => setTimeout(res, delay));
                    delay *= 2;
                } else {
                    throw error;
                }
            }
        }
        throw new Error('Toutes les tentatives de connexion à l\'API ont échoué.');
    }

    document.getElementById('startButton').addEventListener('click', () => {
        showStep('namesStep');
    });

    setupNextButton('namesNext', 'familyNamesOptionStep', () => {
        return document.getElementById('brideName').value.trim() !== '' &&
            document.getElementById('groomName').value.trim() !== '';
    });

    document.getElementById('familyNamesOptionNext').addEventListener('click', () => {
        if (document.getElementById('familyNamesYes').checked) {
            showStep('brideFamilyStep');
        } else if (document.getElementById('familyNamesNo').checked) {
            showStep('dateStep');
        } else {
            alert("Veuillez sélectionner une option.");
        }
    });

    setupNextButton('brideFamilyNext', 'groomFamilyStep');
    setupNextButton('groomFamilyNext', 'dateStep');

    setupNextButton('dateNext', 'locationStep', () => {
        return document.getElementById('eventDate').value.trim() !== '';
    });

    setupNextButton('locationNext', 'mairieTimeStep', () => {
        return document.getElementById('eventCountry').value.trim() !== '' &&
            document.getElementById('eventCity').value.trim() !== '';
    });

    setupNextButton('mairieTimeNext', 'egliseTimeStep');
    setupNextButton('egliseTimeNext', 'cocktailOptionStep');

    document.getElementById('cocktailOptionNext').addEventListener('click', () => {
        if (document.getElementById('cocktailYes').checked) {
            showStep('cocktailDetailsStep');
        } else if (document.getElementById('cocktailNo').checked) {
            showStep('receptionOptionStep');
        } else {
            alert("Veuillez sélectionner une option.");
        }
    });

    setupNextButton('cocktailDetailsNext', 'receptionOptionStep', () => {
        return document.getElementById('cocktailLocation').value.trim() !== '' &&
            document.getElementById('cocktailTime').value.trim() !== '';
    });

    document.getElementById('receptionOptionNext').addEventListener('click', () => {
        if (document.getElementById('receptionYes').checked) {
            showStep('receptionDetailsStep');
        } else if (document.getElementById('receptionNo').checked) {
            showStep('styleStep');
        } else {
            alert("Veuillez sélectionner une option.");
        }
    });

    setupNextButton('receptionDetailsNext', 'styleStep', () => {
        return document.getElementById('receptionLocation').value.trim() !== '' &&
            document.getElementById('receptionTime').value.trim() !== '';
    });

    document.querySelectorAll('.style-button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.style-button').forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');

            if (button.dataset.style === 'theme_particulier') {
                document.getElementById('specificThemeInput').classList.remove('hidden');
            } else {
                document.getElementById('specificThemeInput').classList.add('hidden');
                document.getElementById('specificTheme').value = '';
            }
        });
    });

    setupNextButton('styleNext', 'additionalInfoStep', () => {
        const selectedStyleButton = document.querySelector('.style-button.selected');
        if (!selectedStyleButton) {
            alert("Veuillez sélectionner un style.");
            return false;
        }
        if (selectedStyleButton.dataset.style === 'theme_particulier' && document.getElementById('specificTheme').value.trim() === '') {
            alert("Veuillez préciser votre thème particulier.");
            return false;
        }
        return true;
    });

    document.getElementById('additionalInfoNext').addEventListener('click', async () => {
        updateFormData();

        document.getElementById('loadingIndicator').classList.remove('hidden');
        document.getElementById('generatedText').textContent = '';
        showStep('resultStep');

        try {
            const data = await callGenerateAPI(currentFormData);
            document.getElementById('generatedText').textContent = data.text;

        } catch (error) {
            console.error('Erreur lors de la génération du texte :', error);
            document.getElementById('generatedText').textContent = 'Erreur: ' + error.message + '. Veuillez réessayer plus tard.';
        } finally {
            document.getElementById('loadingIndicator').classList.add('hidden');
        }
    });

    document.getElementById('sendFeedbackButton').addEventListener('click', async () => {
        const feedbackInput = document.getElementById('feedbackInput').value;
        const generatedTextElement = document.getElementById('generatedText');
        const previousText = generatedTextElement.textContent;

        if (!feedbackInput.trim()) {
            alert("Veuillez saisir votre demande de modification.");
            return;
        }

        document.getElementById('loadingIndicator').classList.remove('hidden');
        generatedTextElement.textContent = '';

        const formDataForFeedback = {
            ...currentFormData,
            feedback: feedbackInput,
            previousText: previousText
        };

        try {
            const data = await callGenerateAPI(formDataForFeedback);
            generatedTextElement.textContent = data.text;
            document.getElementById('feedbackInput').value = '';

        } catch (error) {
            console.error('Erreur lors de la modification du texte :', error);
            generatedTextElement.textContent = 'Erreur lors de la modification: ' + error.message + '. Veuillez réessayer plus tard.';
        } finally {
            document.getElementById('loadingIndicator').classList.add('hidden');
        }
    });

    document.getElementById('downloadTextButton').addEventListener('click', () => {
        const textToDownload = document.getElementById('generatedText').textContent;
        if (!textToDownload.trim()) {
            alert("Aucun texte à télécharger.");
            return;
        }

        const filename = "faire_part_mariage.txt";
        const blob = new Blob([textToDownload], { type: "text/plain;charset=utf-8" });

        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
    });

    document.getElementById('restartButton').addEventListener('click', () => {
        document.getElementById('brideName').value = '';
        document.getElementById('groomName').value = '';
        document.getElementById('familyNamesYes').checked = false;
        document.getElementById('familyNamesNo').checked = false;
        document.getElementById('brideFamilyNames').value = '';
        document.getElementById('groomFamilyNames').value = '';
        document.getElementById('eventDate').value = '';
        document.getElementById('eventCountry').value = '';
        document.getElementById('eventCity').value = '';
        document.getElementById('mairieTime').value = '';
        document.getElementById('egliseTime').value = '';
        document.getElementById('cocktailYes').checked = false;
        document.getElementById('cocktailNo').checked = false;
        document.getElementById('cocktailLocation').value = '';
        document.getElementById('cocktailTime').value = '';
        document.getElementById('receptionYes').checked = false;
        document.getElementById('receptionNo').checked = false;
        document.getElementById('receptionLocation').value = '';
        document.getElementById('receptionTime').value = '';
        document.getElementById('specificTheme').value = '';
        document.getElementById('additionalInfo').value = '';

        document.querySelectorAll('.style-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('specificThemeInput').classList.add('hidden');

        document.getElementById('generatedText').textContent = '';
        document.getElementById('feedbackInput').value = '';
        currentFormData = {};

        showStep('introStep');
    });

    document.querySelector('.header-logo').addEventListener('click', () => {
        if (confirm("Voulez-vous en savoir plus sur mon fonctionnement ?")) {
            showStep('secretQuestionResponse');
        }
    });

    document.getElementById('backFromSecretButton').addEventListener('click', () => {
        if (!document.getElementById('resultStep').classList.contains('hidden')) {
            showStep('resultStep');
        } else {
            showStep('introStep');
        }
    });

    showStep('introStep');
});