const quizzes = {
    quiz1: {
        q1: "To manage technological advancements and emerging threats",
        q2: "Universal connectivity",
        q3: "To safeguard computer systems and data from unauthorized access",
        q4: "Protecting data that flows across networks",
        q5: "To handle sensitive information carefully and adhere to legal requirements",
        q6: "An action that could cause harm",
        q7: "An item with value",
        q8: "A weakness in security",
        q9: "Exposure to danger",
        q10: "A person who could carry out a threat",
   
        q11: "How the attack could occur",
        q12: "Avoiding the risk in the first place, such as not storing information that could be stolen",
        q13: "Transferring the risk to someone else, such as by buying insurance",
        q14: "People who exploit vulnerabilities to acquire wealth rather than to seek fame",
        q15: "Those who spy on and disrupt governments and citizens",
        q16: ['Passwords are often too simple or easily guessable', 'People tend to reuse passwords across multiple accounts', 'Passwords are often short and lack complexity'],
        q17: "Use a minimum of 12-16 characters",
        q18: "Combining passwords with another authentication method like SMS codes, authentication apps, or biometrics",
        q19: "They generate and store strong, unique passwords securely",
        q20: "Passphrases are longer and can be harder to guess while still being easy to remember",
    
        
    },
    quiz2: {
        q1: "Software that performs unwanted actions on your computer system",
        q2: "Improve Performance",
        q3: ['Locking the system until a ransom is paid', 'Encrypting files and demanding payment for decryption'],
        q4: "Captures and transmits data without consent",
        q5: "Trojan",
        q6: "Bot",
        q7: "Both A and B",
        q8: "Execute malicious activity under certain conditions",
        q9: ['It can install other malicious software', 'It can monitor user activity without their knowledge'],
        q10: "Hiding malware presence",
   
        q11: "Updates fix security vulnerabilities",
        q12: "Scan and remove malware",
        q13: ['Block unauthorized access', 'Control network traffic'],
        q14: "Helps recognize phishing attempts",
        q15: "Backup important data",
        q16: "Keeps security features up-to-date",
        q17: "Allow the antivirus to remove or quarantine the virus",
        q18: "They control what traffic is allowed in and out",
        q19: ['Isolating backup storage from the network', 'Disconnecting unnecessary devices'],
        q20: "Provides layered security",
    
        q21: "To manage the aftermath of security breaches",
        q22: "Cost management",
        q23: ['Assessing the scope of the breach', 'Categorize the Incident','Analyze the Impact'],
        q24: "Isolate infected machines",
        q25: "SIEM systems",
        q26: "To uncover how attacks were executed",
        q27: "It should be restored from backups",
        q28: ['It helps in legal defense and supports insurance claims', 'It supports refining incident response procedures','It provides a record for compliance and regulations'],
        q29: "Conduct a review to identify improvements",
        q30: "Invest in advanced forensic technologies"
    },
    quiz3: {
        q1: "To investigate cybercrimes and uphold legal requirements",
        q2: "It enables forensic analysis of digital devices",
        q3: "It helps organizations identify potential threats",
        q4: "To identify the perpetrators accurately",
        q5: "The Surface Web",
        q6: "It requires specific software or permissions to access.",
        q7: "Serves as a hub for underground transactions and illicit activities",
        q8: "By using specialized software like Tor (The Onion Router) browser",
        q9: "Random ads seen on popular websites that may contain malware",
        q10: "Infection of user devices with malware from infected websites",

        q11: "Forging the sender's email address to make it appear from a trusted source",
        q12: "To trick recipients into revealing sensitive information",
        q13: ["Overwhelming a target system with a flood of traffic from multiple sources"],
        q14: "Sophisticated and targeted cyberattacks typically carried out by nation-state actors or organized cybercriminal groups",
        q15: "Vulnerabilities in software or hardware that are unknown to the vendor or have not been patched yet",
        q16: "Encryption of a victim's files or locking them out of their systems until a ransom is paid",
        q17: "Signs or signals that indicate potential security threats, vulnerabilities, or suspicious activities",
        q18: "Security professionals, automated systems, or users",
        q19: ["To detect and respond to security incidents effectively"],
        q20: "They help identify potential security threats and vulnerabilities",
    
        q21: "Unauthorized access or potential security breaches",
        q22: "Attempted cyber-attacks or data exfiltration",
        q23: ["Insider threats or compromised user accounts"],
        q24: "Phishing attempts targeting criminal justice personnel",
        q25: "Encrypting web traffic for secure transmission",
        q26: "Exposing users to malware or other security threats if not managed properly",
        q27: "Unauthorized access to sensitive information",
        q28: ["Implementing robust email security measures and educating users"],
        q29: "Increasing attachment awareness",
        q30: "By blocking unwanted or harmful emails"
    },
    quiz4: {
        q1: "To protect it from unauthorized access",
        q2: "Physical security measures",
        q3: "Data at rest is stored; data in transit is being transferred",
        q4: "TLS",
        q5: "To ensure data is encrypted from the sender to the recipient without intermediary decryption",
        q6: "Man-in-the-Middle (MitM) attack",
        q7: "It makes intercepted data unreadable to unauthorized parties",
        q8: "By changing data so that it cannot be traced back to an individual but remains usable",
        q9: ["It can make user services less user-friendly"],
        q10: "Access controls",

        q11: "The illegal access and transfer of data without permission",
        q12: "Blood type",
        q13: "To track user activity and location for advertising",
        q14: "Advertisers",
        q15: "Identity theft",
        q16: "By unauthorized transactions using their information",
        q17: "Reputation damage",
        q18: "The General Data Protection Regulation (GDPR)",
        q19: "Emotional stress and a sense of vulnerability",
        q20: "Using strong, unique passwords and enabling two-factor authentication (2FA)",

        q21: "To secure communications to prevent unauthorized access",
        q22: "It converts it into an unreadable format known as ciphertext",
        q23: "Writing a message with invisible ink",
        q24: "Confidentiality of sensitive data",
        q25: "Symmetric",
        q26: "Encryption key",
        q27: "Sender cannot deny sending the data",
        q28: "Frequency analysis",
        q29: "To verify data integrity",
        q30: "Digital certificates",

        q31: "To remember site-specific preferences like language and login status",
        q32: "Third-party cookies",
        q33: "By reducing the ability of advertisers to track your browsing across multiple sites",
        q34: "To track activity across apps and websites for advertising purposes",
        q35: "By limiting ad tracking in the privacy settings",
    }
    
};


$(document).ready(function() {
    const shuffleArray = (array) => {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]]; // Swap elements
        }
        return array;
    };

    const setupQuiz = () => {
        const $questions = $('.question');
        $questions.hide(); // Hide all questions initially

        const shuffledQuestions = shuffleArray($questions.toArray());
        const selectedQuestions = shuffledQuestions.slice(0, 15);

        const $quizContainer = $questions.parent(); // Assuming all questions are in the same container
        $quizContainer.empty(); // Clear the container

        selectedQuestions.forEach((question, index) => {
            const $question = $(question);
            let currentText = $question.find('h4').text();
            $question.find('h4').text((index + 1) + currentText);
            $quizContainer.append($question); // Append the question to the container in new order
            $quizContainer.append($('#quiz-submit')); // Append the question to the container in new order
            $question.show();
        });
    };

    setupQuiz();
});
    
    function submitQuiz(quizId) {
        let score = 0;
        const quiz = quizzes[quizId]; // Access the correct quiz dictionary using the quizId
        
        // Specify the context for the jQuery selector to the quiz container
        const quizContainer = $('#' + quizId);
        
        // Check each radio button answer within the quiz container
        $('input[type="radio"]:checked', quizContainer).each(function () {
            const name = $(this).attr('name');
            if ($(this).val() === quiz[name]) {
                score++;
            }
        });
        
        // Check checkbox answers within the quiz container
        $('.question', quizContainer).each(function() {
            const checkboxes = $(this).find('input[type=checkbox]');
            if (checkboxes.length > 0) { // Ensure that there are checkboxes present
                let allCorrect = true;
                // Assuming that checkbox names are in the format q3a1, q3a2... Extract q3 from the name of the first checkbox
                const questionId = checkboxes.first().attr('name').split('a')[0];
                const correctAnswers = quiz[questionId].map(answer => answer.trim().toLowerCase()); // Normalize answers
                
                checkboxes.each(function() {
                    const isChecked = $(this).is(':checked');
                    const answerText = $(this).next('label').text().trim().toLowerCase(); // Normalize text
                    
                    // Check if the current checkbox should be checked or not
                    const isCorrectAnswer = correctAnswers.includes(answerText);
                    if (isChecked && !isCorrectAnswer || !isChecked && isCorrectAnswer) {
                        allCorrect = false;
                    }
                });
                
                // Only increment score if all checkboxes are correctly checked
                if (allCorrect) {
                    score++;
                }
            }
        });
        
        // Show the score
        alert('Your score is: ' + score + '/15');
        
        // Clear all checkboxes and radio buttons within the quiz container after the alert is dismissed
        $('input[type="checkbox"], input[type="radio"]', quizContainer).prop('checked', false);

    }
    
    
    