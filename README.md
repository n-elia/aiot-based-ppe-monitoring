# AIoT-based PPE Monitoring System

## Introduction

This project is about a Personal Protective Equipment (PPE) monitoring system PoC based on an AIoT architecture.
The system is composed of a set of devices mounted on PPEs based on ESP32-S3 boards, a gateway, a cloud platform and a web application.

This repository contains the code for the PPEs devices and the dataset of RSSI measurements used to train the machine learning model.

## Folder structure

- `dataset`: contains the dataset of RSSI measurements used to train the machine learning model.
- `ppe_devices`: contains the code for the PPEs devices, i.e. their firmware.
