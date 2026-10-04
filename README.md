# MagHub

MagHub is an AI-powered research and decision-support platform designed for Virginia magistrates. It provides a conversational interface for researching legal and procedural questions while grounding responses in authoritative Virginia sources.

**Live Application:** https://maghub.app

## Overview

Virginia magistrates routinely work with legal and procedural information spread across statutes, manuals, and other reference materials. MagHub was created to make that information easier to access and navigate through a single conversational interface.

Users can ask questions in natural language and receive structured responses supported by relevant legal and procedural sources. MagHub is designed as a research and decision-support tool rather than a replacement for the independent judgment or legal responsibilities of a magistrate.

## Key Features

- Conversational AI interface for legal and procedural research
- Retrieval-Augmented Generation (RAG) using Virginia magistrate reference materials
- Live retrieval of Virginia Code sections from official Virginia legislative sources
- Source citations linking users to supporting authority
- Persistent conversations and chat history
- Multiple chat sessions with rename and delete functionality
- Streaming AI responses
- Dark and light themes
- Adjustable display sizes
- Responsive web interface
- PostgreSQL vector search using pgvector
- Dockerized application and database
- AWS cloud deployment with HTTPS and custom domain
- Automated CI/CD deployment through GitHub Actions

## Architecture

MagHub combines traditional application infrastructure with AI retrieval and generation.

The frontend sends user questions to a FastAPI backend. Relevant magistrate reference material is retrieved from PostgreSQL using vector similarity search, while applicable Virginia Code sections can be retrieved from official Virginia legislative resources. This information is supplied as context to the AI model before the final response is generated.

The application is containerized with Docker and deployed to AWS behind an Application Load Balancer.

### Request Flow

User  
↓  
HTML / CSS / JavaScript  
↓  
FastAPI REST API  
↓  
RAG Retrieval + Virginia Code Retrieval  
↓  
OpenAI API  
↓  
Grounded Response + Sources

## Technology

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- OpenAI API
- Uvicorn

### Frontend
- JavaScript
- HTML
- CSS

### Cloud & DevOps
- AWS EC2
- Application Load Balancer
- Route 53
- AWS Certificate Manager
- Docker
- Docker Compose
- Terraform
- GitHub Actions CI/CD

## Retrieval-Augmented Generation

MagHub uses vector embeddings to retrieve relevant portions of Virginia magistrate reference materials.

Reference documents are divided into chunks and converted into embeddings. These embeddings are stored in PostgreSQL using pgvector. When a user submits a question, MagHub embeds the question and performs vector similarity search to identify relevant material.

Retrieved context is then supplied to the AI model so responses can be grounded in the reference material rather than relying solely on the model's general knowledge.

## Virginia Code Integration

MagHub can identify potentially relevant Virginia Code sections from natural-language questions and retrieve current statutory information from official Virginia legislative resources.

Relevant Virginia Code sources are displayed with the response so users can review the underlying statutory authority directly.

## Cloud Deployment

MagHub is deployed on AWS using a containerized architecture.

Production traffic follows:

User → Route 53 → Application Load Balancer → EC2 → Docker → FastAPI

HTTPS is provided using AWS Certificate Manager, and the application is available through the custom `maghub.app` domain.

## CI/CD

MagHub uses GitHub Actions for continuous integration and deployment.

Pushes to the main branch automatically:

1. Check out the repository
2. Build the Docker image
3. Connect to the AWS EC2 environment
4. Pull the latest application code
5. Rebuild and restart the application containers

This allows production deployments to occur automatically after code is pushed to the main branch.

## Purpose

MagHub explores how modern AI tools can responsibly support the day-to-day work of Virginia magistrates by making authoritative information easier to locate, review, and understand.

The platform is intended to assist research and decision-making while preserving the independent judgment and responsibility of the magistrate.
