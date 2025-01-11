# Rasa CitiBot 

This project implements a Rasa-powered conversational AI bot designed to interact with users on WhatsApp using the Twilio API. The assistant focuses on providing information about Nigerian civic topics, including rights, responsibilities, and election-related information.  

## Features  
- **WhatsApp Integration**: Seamless connection between Rasa chatbot and WhatsApp via Twilio API.  
- **Dynamic Responses**: Contextual and accurate responses powered by OpenAI's GPT API.  
- **Nigerian Civic Topics**: Includes topics like rights, voting processes, government structure, and more.  

## Technologies Used  
- **Rasa Framework**  
- **Twilio Messaging Service**  
- **OpenAI API (GPT)**  
- **Python**  

## Installation and Setup  

### 1. Clone the Repository  
```bash  
git clone <repository-url>  
cd <repository-folder>  
```

### 2. Create and Activate a Virtual Environment 
For Windows:
```bash  
python -m venv env
env\Scripts\activate
```
For macOS/Linux:
```bash  
python3 -m venv env
source env/bin/activate
```
Once activated, you should see the virtual environment name in your terminal prompt.
Install Required Dependencies:
```bash  
pip install -r requirements.txt
```

### 3. Install Dependencies  
Install Rasa and other required libraries:  
```bash  
pip install rasa  
pip install twilio openai python-dotenv  
```  

### 4. Configure Environment Variables  
Set up sensitive credentials like Twilio keys, OpenAI keys, and others in a `.env` file for secure handling:  
```  
TWILIO_ACCOUNT_SID=<your_account_sid>  
TWILIO_AUTH_TOKEN=<your_auth_token>  
TWILIO_PHONE_NUMBER=whatsapp: <your_twilio_phone_number>  
OPENAI_API_KEY=<your_openai_api_key>  
```  

### 5. Run Rasa Locally
Start the Rasa server:  
```bash  
rasa run --endpoints endpoints.local.yml --enable-api
```  

Run the action server: 
In a seperate terminal run the action command
```bash  
rasa run actions  
```  

### 6. Set Up ngrok for Local Testing  
To expose your Rasa bot to the internet and connect it to Twilio:  
1. Install ngrok:  
   ```bash  
   pip install ngrok  
   ```  
2. Authenticate ngrok using your authtoken (get it from [ngrok dashboard](https://dashboard.ngrok.com/get-started/setup)):  
   ```bash  
   ngrok config add-authtoken <YOUR_NGROK_AUTHTOKEN>  
   ```  
3. Start an ngrok HTTP tunnel for port 5005:  
   ```bash  
   ngrok http 5005  
   ```  
4. Copy the HTTPS forwarding URL (e.g., `https://<your-ngrok-url>.ngrok.io`).  

### 6. Configure Twilio Webhook  
1. Log in to your Twilio console and navigate to **Messaging** > **Phone Numbers**.  
2. Select the Twilio phone number you want to use.  
3. Under the **Messaging** section, add the following webhook URL to **A MESSAGE COMES IN**:  
   ```
   https://<your-ngrok-url>.ngrok.io/webhooks/twilio/webhook  
   ```  

### 7. Test the Bot on WhatsApp  
1. Send a message to your Twilio WhatsApp number.  
2. The bot will respond based on the configured intents and actions.  
