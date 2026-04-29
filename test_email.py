import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")

def test_email():
    """Test l'envoi d'un email de test"""
    if not all([SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL]):
        print(" Configuration incomplète. Vérifiez SMTP_USER, SMTP_PASSWORD et ALERT_EMAIL dans .env")
        return False

    try:
        # Créer le message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Test Email SmartAgri"
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL

        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; background: #f0f9f0; padding: 20px;">
          <div style="max-width: 500px; margin: auto; background: white; border-radius: 12px;
                      border: 2px solid #16a34a; padding: 30px; box-shadow: 0 4px 20px rgba(22,163,74,0.15);">
            <h2 style="color: #16a34a; margin: 0 0 16px;">✅ Test Réussi !</h2>
            <p style="color: #374151;">La configuration email fonctionne correctement.</p>
            <p style="color: #6b7280; font-size: 13px;">
              Votre système SmartAgri peut maintenant envoyer des alertes de sécurité.
            </p>
            <hr style="border: 1px solid #dcfce7; margin: 20px 0;" />
            <p style="color: #9ca3af; font-size: 11px;">SmartAgri — Test de configuration</p>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        # Connexion SMTP
        print(f"Connexion à {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            print(" Authentification...")
            server.login(SMTP_USER, SMTP_PASSWORD)
            print(" Envoi de l'email de test...")
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())

        print(f" Email de test envoyé avec succès à {ALERT_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print(" Erreur d'authentification. Vérifiez votre App Password Gmail.")
        print("   Générer un App Password: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPConnectError:
        print(" Erreur de connexion. Vérifiez l'hôte et le port SMTP.")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print(" Test de configuration email SmartAgri")
    print("=" * 50)
    success = test_email()
    print("=" * 50)
    if success:
        print(" Configuration email validée ! Les notifications fonctionneront.")
    else:
        print("  Corrigez la configuration avant de continuer.")