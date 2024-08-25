# ImageVisionAPI
Image Classification Web Application with FastAPI and Gradio

![License](https://img.shields.io/badge/license-MIT-green)
![Python Versions](https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12-blue)
![CI](https://github.com/SkxPhan/ImageVisionAI/actions/workflows/ci.yml/badge.svg)
<!-- ![Code Quality](https://img.shields.io/github/workflow/status/SkxPhan/ImageVisionAI/ci/code-quality?label=code-quality) -->
<!-- ![Coverage](https://img.shields.io/codecov/c/github/your-username/your-repo?label=coverage&style=flat) -->
![Docker Image Version](https://img.shields.io/docker/v/SkxPhan/<your-image-name>?label=docker%20image&color=blue)

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
- **Gradio**: User-friendly interface for image upload and classification.
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
- Python 3.8+

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
```bash
DATABASE_URL=postgresql://user:password@db:5432/database
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Initialize the database

```bash
poetry run python app/db/init_db.py
```

### Run the application
```bash
docker-compose up --build
```

The FastAPI application will be available at `http://localhost:8000`, and the Gradio interface will be available at `http://localhost:7860`.

## Usage

### FastAPI Endpoints

- Register: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login`
- Upload Image: `POST /api/v1/images/upload`
- Get History: `GET /api/v1/images/history`

### Gradio Interface
Visit `http://localhost:7860` to use the Gradio interface for image classification.

## API Documentation
FastAPI provides interactive API documentation at `http://localhost:8000/docs` and `http://localhost:8000/redoc`.

## CI/CD
The project includes a GitHub Actions workflow for continuous integration and deployment. The workflow is defined in `.github/workflows/ci.yml` and includes steps for running tests, building Docker images, and deploying the application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
