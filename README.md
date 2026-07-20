# 🚨 ResQMesh

> A decentralized emergency communication system that enables SOS message transmission using ESP32 mesh communication when conventional network infrastructure is unavailable.

![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Platform](https://img.shields.io/badge/Platform-ESP32-blue)
![Language](https://img.shields.io/badge/Language-C++-00599C)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

During natural disasters and emergency situations, cellular towers and internet connectivity can become unavailable, making it difficult for people to request help.

**ResQMesh** is an embedded IoT solution that establishes a decentralized communication network using ESP32 devices. Users can submit emergency requests through a nearby access node, which wirelessly relays the SOS information to a gateway node using the ESP-NOW protocol. The gateway forwards the data to a Raspberry Pi for processing and visualization.

The goal is to provide a lightweight, low-power, and infrastructure-independent emergency communication system.

---

## 🏗️ System Architecture

```
                Mobile Phone
                      │
             HTTP Emergency Request
                      │
                      ▼
         ESP32 Access Node (Web Server)
                      │
                 ESP-NOW Protocol
                      │
                      ▼
            ESP32 Gateway Node
                      │
                USB Serial Communication
                      │
                      ▼
               Raspberry Pi Backend
                      │
                Flask Dashboard
```

---

## ✨ Features

- Emergency SOS submission through a mobile browser
- ESP32-based Wi-Fi Access Point
- Embedded HTTP web server
- Wireless communication using ESP-NOW
- Gateway forwarding through serial communication
- Raspberry Pi backend processing
- Live monitoring dashboard (In Progress)
- Modular architecture for future mesh expansion

---

## 🛠️ Technologies Used

### Hardware

- ESP32 Development Boards
- Raspberry Pi 4
- USB Serial Communication

### Software

- Arduino IDE
- ESP-NOW
- Python
- Flask
- HTML
- CSS
- JavaScript

---

## 📂 Repository Structure

```
ResQMesh/
│
├── access-node/
│   ├── access_node.ino
│   └── webpage/
│
├── gateway/
│   └── gateway.ino
│
├── raspberry-pi/
│   ├── src/
│   ├── dashboard/
│   └── logs/
│
├── docs/
│
├── images/
│
└── README.md
```

---

## 🚀 Current Progress

### ✅ Completed

- ESP32 Wi-Fi Access Point
- HTTP Emergency Form
- ESP-NOW Communication
- Gateway Receiver
- Raspberry Pi Serial Communication
- Python SOS Packet Parser

### 🚧 In Progress

- Flask Dashboard
- Live Emergency Updates
- Event Logging

### 📅 Planned

- Multi-hop Mesh Routing
- GPS Integration
- Interactive Map Dashboard
- Emergency Database
- SMS/Email Notifications
- Battery Monitoring
- Analytics Dashboard

---

## 📷 Demo

Project screenshots and demonstration videos will be added soon.

---

## 🎯 Applications

- Disaster Response
- Search and Rescue Operations
- Rural Communication Networks
- Emergency Management
- Temporary Relief Camps
- Industrial Safety Systems

---

## 👩‍💻 Team

Developed as part of a hackathon project focused on resilient emergency communication systems.

---

## 📜 License

This project is licensed under the MIT License.

---

⭐ If you find this project interesting, consider giving it a star!
