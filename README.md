# College-project
# QR-Based Voice-Assisted Campus Navigation System with Real-Time Facility Updates

## Project Description
This project aims to improve university campus navigation and accessibility using QR codes, voice assistance, and real-time facility updates. It is designed to help students, staff, and visitors easily find departments, offices, canteens, and more—especially beneficial for visually impaired individuals or newcomers.

By simply scanning a QR code placed across the campus, users are directed to a responsive web interface that provides:
- Real-time location details
- Working hours
- Navigation paths
- Voice-guided assistance

## Objective
To create a smart, accessible, and real-time campus navigation system using:
- QR Code technology
- Web-based voice assistant
- Real-time data updates using Firebase Firestore

## Features
- QR Code-based indoor navigation
- Voice assistant for hands-free navigation
- Real-time facility status updates (library open/closed, canteen status, etc.)
- Google Maps integration for outdoor navigation
- Visually-impaired-friendly UI with screen reader and voice support
- Admin dashboard for updating live campus info

## Modules
- QR Code Scanner Module – Scans codes at locations and shows navigation.
- Voice-Guided Navigation – Responds to voice queries like “Where is the library?”
- Real-Time Facility Status – Admins update the current status of facilities.
- Admin Dashboard – Role-based portal for location and data management.
- Multilingual Support – Supports languages like Tamil for local adaptability.

## Tech Stack

| Layer         | Technologies Used                  |
|---------------|------------------------------------|
| Frontend      | HTML, CSS, JavaScript              |
| Backend       | Python (Flask)                     |
| Database      | Firebase Firestore (Real-time DB)  |
| QR Scanner    | html5-qrcode, ZBar, OpenCV         |
| Voice         | Web Speech API, SpeechRecognition  |
| Hosting       | Firebase Hosting / AWS             |

## Algorithms Used
- A* Pathfinding (for indoor route optimization)
- Dijkstra’s Algorithm (for outdoor paths via Google Maps)
- Event-driven live updates via Firebase triggers

## Testing
- Validated QR scanning and voice recognition under noisy conditions
- Tested edge cases: poor internet, invalid QR, low light
- User tested with positive feedback from students and staff

## Future Enhancements
- Mobile app using Flutter
- AR Navigation with live camera overlay
- Offline support and multilingual enhancements
- Crowd level or event display in real-time

## Screenshots
Include screenshots of:
- QR scanner view
- Navigation map
- Admin dashboard
- Facility status display
- Voice query interface

## Conference Presentation
This project was presented at:
International Conference on Innovative Research in Engineering and Technology (ICIRET - 2025)  
Date: 28.03.2025  
Venue: A.V.C. College of Engineering, Mayiladuthurai

## References
- Bhandari A., “QR Code Tech for Campus”, IJSC, 2021
- Das P., “Dynamic Info for Universities”, IJER, 2022
- Gupta M., “Real-Time Campus Systems”, EIT, 2023
- Additional references listed in project report

## How to Run This Project

```bash
# Clone the project
git clone https://github.com/yourusername/qr-campus-navigation.git

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
