## EmergenSee

https://www.youtube.com/watch?v=533HwqyZ6as

## Inspiration
86% of security of Quebec emergency call dispatchers say they are **overloaded** [1]. They work long hours in a stressful environment. In situations of **crisis**, calls can begin to stack up while it is crucial that every caller is answered in minimal time. In this context, we decided to build a  human-in-the-loop AI powered visualisation tool for emergency services dispatchers.

## What it does
Our project is divided in 2 parts: a fully automated AI chatbot and a visual dashboard to be used by call dispatchers.
The chatbot answers the call and collects critical information about the emergency and then creates a ticket with a summary of the situation, the caller's name, phone number and location, an estimation of the gravity of the situation and type of service required.
This ticket is then displayed on the dashboard where a human operator can quickly assess the situation and transfer the call to proper help ressources.

## How we built it
We used nGrok and Twilio to receive the phone call and process it using a python script. We then used DeepSeek-R1 to handle the conversation with the caller and summarize the information. We then transfer this information to a MongoDB database, which is then fetched by a website we built from scratch using html/css/javascript.

## Challenges we ran into
We had difficulty choosing the right gen AI model for the assistant to strike the perfect balance between speed of response and accuracy. Emergency calls need to be answered quickly but also accurately. We started with GPT-3.5 turbo, but quickly realised this model had difficulty handling some subtleties. We then settled on DeepSeek-R1 which provides better responses, but the delay before responses can sometimes be an issue.
We also had some challenges integrating Twilio and elevenLabs APIs. Twilio kept routing our calls around the world, charging us extra cost for testing with long distance calls. Finally, merging the different parts of the projects took longer than expected.

## Accomplishments that we're proud of
It is highly rewarding to realize we built something that could really help people and make a difference.
We are proud of the prompt engineering we did to ensure the model’s perfect balance between empathy, accuracy and speed.
The UI of the dashboard is also a source of satisfaction.

## What we learned
How to integrate many API and AI tools into the same project
How to brainstorm efficiently as a team of 4 and come up with a impactful and feasible idea
How to refine a gen AI model with specific system instructions

## What's next for EmergenSee
Improved visual information on the dashboard: Map layout about hot zones, prediction of high call traffic period, time estimation.
Train our Ai: Improve the accuracy of the answers by fine tuning the model on real emergency calls responses.
Give information and plan: With previous data, we will predict where the ambulances and police should be to prevent events.


[1]	C. Boucher. (2024) Débordements dans les centres d’appels de la SQ. [En ligne]. Disponible: https://www.journaldemontreal.com/2024/04/15/debordements-dans-les-centres-dappels-de-la-sq
