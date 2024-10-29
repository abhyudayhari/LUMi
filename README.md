# LUMi - AI Concierge for Lyf Funan Singapore

LUMi is an AI Concierge designed to enhance customer satisfaction and loyalty by delivering a personalized guest experience at Lyf Funan Singapore. This AI-powered solution operates across multiple platforms to streamline guest interactions and promptly address their needs. The core objective is to provide guests with fast, efficient, and intuitive assistance, transforming the traditional customer service model and bridging the feedback loop for enhanced loyalty and satisfaction.

## Project Overview

LUMi operates on:
- **Room Displays**: Allows guests to interact with LUMi directly through in-room displays for instant support.
- **Phone Call Support**: Guests can call a dedicated line where LUMi will offer automated support and escalate issues to a human agent when necessary.
- **WhatsApp Bot**: LUMi is accessible through WhatsApp, providing a convenient way for guests to get assistance via chat.
- **Hotel App Integration**: Offers seamless integration within the hotel's app to ensure guests have easy access to LUMi wherever they are.

The bot remembers guests' previous interactions and preferences to offer a personalized experience. By analyzing existing reviews, it quickly identifies common issues and provides immediate resolutions.

## Features

- **Multilingual Support**: LUMi supports multiple languages to accommodate a diverse guest profile, ensuring guests feel understood and valued.
- **Personalized Experiences**: Stores guest preferences and past interactions to deliver tailored recommendations and support.
- **Two-way Communication**: Engages guests through both chat and call, following up on issues and proactively updating them.
- **Real-Time Sentiment Analysis**: Analyzes guest feedback and resolves grievances based on historical data and trends.
- **Cross-platform Accessibility**: Available across room displays, phone support, WhatsApp, and the Lyf hotel app, ensuring a consistent guest experience.
- **Streamlined Feedback Collection**: Automatically logs feedback from interactions, bridging the feedback loop for management.

## Folder Structure

```plaintext
├── graphs/           # Visualization resources for analysis and presentation
├── ml/               # Machine learning models and scripts (HuggingFace, langchain, langgraph)
├── website/          # Next.js-based web interface for LUMi
├── whatsapp-bot/     # WhatsApp bot backend powered by Twilio and TypeScript
├── .gitignore        # Git ignore file for project
└── README.md         # Project documentation
```

## Tech Stack

- **Machine Learning & NLP**: Python with HuggingFace, Langchain, LangGraph, NVIDIA-Nemo
- **Communication Platform**: Twilio for WhatsApp integration, TypeScript for backend logic
- **Frontend**: Next.js with React for the web console
- **Database & Authentication**: Firebase
- **Orchestration & Deployment**: Tavily

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- Python (v3.8 or later)
- Firebase account for authentication setup
- Twilio account for WhatsApp integration

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/skysingh04/LUMi
   cd LUMi-AI-Concierge
   ```

2. **Install Dependencies**

   - For the website and WhatsApp bot:
     ```bash
     cd website
     npm install
     cd ../whatsapp-bot
     npm install
     ```

   - For the ML models:
     ```bash
     cd ml
     pip install -r requirements.txt
     ```

3. **Set up Firebase**

   - Add Firebase configuration in both `website` and `whatsapp-bot` directories.

4. **Configure Twilio**
   - Add Twilio credentials in the `whatsapp-bot` directory to enable WhatsApp functionality.

### Deployment

LUMi can be deployed using Tavily. Ensure all configuration files are in place and follow the Tavily documentation for deployment steps.

### Running Locally

To test the application locally, run the components as follows:

- **Website**:
  ```bash
  cd website
  npm run dev
  ```

- **WhatsApp Bot**:
  ```bash
  cd whatsapp-bot
  npm run start
  ```

- **Machine Learning Models**:
  ```bash
  cd ml
  python main.py
  ```

## Testing Instructions

1. **Unit Tests**
   - Run unit tests for each component to ensure functionality.
   - For the website and WhatsApp bot, use Jest:
     ```bash
     npm run test
     ```

2. **Integration Tests**
   - End-to-end testing of the interaction between the bot and the backend using Twilio’s testing tools.

3. **Load Testing**
   - Evaluate the bot’s response time and reliability under varying load conditions.
