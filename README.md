# ImageVisionAPI
Image Classification Web Application with FastAPI and Gradio

![License](https://img.shields.io/badge/license-MIT-green)
![Python Versions](https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12-blue)
![CI](https://github.com/SkxPhan/ImageVisionAI/actions/workflows/ci.yml/badge.svg)
![Docker Image Version](https://img.shields.io/docker/v/skxphan/image-vision-api?label=docker%20image&color=blue)
<!-- ![Code Quality](https://img.shields.io/github/workflow/status/SkxPhan/ImageVisionAI/ci/code-quality?label=code-quality) -->
<!-- ![Coverage](https://img.shields.io/codecov/c/github/your-username/your-repo?label=coverage&style=flat) -->

This project demonstrates a complete pipeline for a image classification system using Convolutional Neural Networks (CNNs), FastAPI, Gradio, and Docker. The project includes user authentication, image upload, classification, and history retrieval, with a focus on continuous integration and deployment.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies](#technologies)
- [Setup](#setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [CI/CD](#cicd)
- [License](#license)

## Introduction

This project provides a comprehensive example of how to build a machine learning application with a REST API for model inference and a user-friendly interface for interacting with the model. It includes user authentication, image upload functionality, and a history of past classifications.

## Features

- **CNN Model**: Image classification using a Convolutional Neural Network built with PyTorch.
- **FastAPI**: High-performance API backend.
- **Gradio**: User-friendly interface for image upload and classification. (TODO)
- **PostgreSQL**: Relational database for storing user data and classification history.
- **User Authentication**: Secure JWT-based authentication.
- **CI/CD**: Continuous integration and deployment using GitHub Actions.
- **Docker**: Containerized deployment for easy setup and scaling.

## Technologies

- Python
- PyTorch
- FastAPI
- Gradio
- SQLAlchemy
- PostgreSQL
- JWT
- Docker
- GitHub Actions
- Poetry

## Setup

### Prerequisites

- Docker
- Docker Compose
- Poetry
- Python 3.10+

### Clone the repository

```bash
git clone https://github.com/username/repository.git
cd repository
```

### Install dependencies

```bash
poetry install
```

### Setup environment variables

Create a `.env` file in the root directory and add the following variables:

### Run the application
```bash
docker-compose up --build
```

The FastAPI application will be available at `http://localhost:8000`.

## Usage

### FastAPI Endpoints

- Register: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login`
- Logout: `POST /api/v1/auth/logout`
- Classify Image: `POST /api/v1/ml/predict`
- Get User Info: `GET /api/v1/users/me`
- Get History: `GET /api/v1/users/me/history`

## API Documentation
FastAPI provides interactive API documentation at `http://localhost:8000/docs` and `http://localhost:8000/redoc`.

## CI/CD
The project includes a GitHub Actions workflow for continuous integration and deployment and defined in `.github/workflows`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
