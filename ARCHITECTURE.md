# DevOpsHub Architecture

## 1. Purpose

DevOpsHub is a production-style task management platform designed as a progressive DevOps engineering project.

The application itself is intentionally simple. The primary engineering objective is to learn how to design, deploy, secure, monitor, troubleshoot, scale, and operate a production-style system.

---

## 2. Initial Application Architecture

The first application version will use a simple three-tier architecture:

User
 |
 v
React Frontend
 |
 v
FastAPI Backend
 |
 v
PostgreSQL

Redis will be introduced when the application requires caching or other appropriate distributed-state functionality.

---

## 3. Application Components

### Frontend

Technology:

- React

Responsibilities:

- User interface
- Authentication interface
- Project management
- Task management
- API communication

### Backend

Technology:

- Python
- FastAPI
- SQLAlchemy
- Alembic

Responsibilities:

- REST API
- Authentication
- Authorization
- Business logic
- Database access
- Health endpoints
- Metrics endpoint

### Database

Technology:

- PostgreSQL

Responsibilities:

- Persistent application data
- Users
- Projects
- Tasks
- Comments
- Activity records

### Cache / Supporting Services

Technology:

- Redis

Initial purpose:

- Caching
- Short-lived application state
- Future background-job support if required

Redis will not be introduced into the application merely for the sake of using another technology.

---

## 4. Application Features

The application will initially support:

- User registration
- User login
- Authentication
- Current-user endpoint
- Projects
- Tasks
- Task status
- Task priority
- Comments
- Activity logs

Initial API surface:

POST   /auth/register
POST   /auth/login

GET    /users/me

POST   /projects
GET    /projects
GET    /projects/{id}

POST   /projects/{id}/tasks
GET    /projects/{id}/tasks

PATCH  /tasks/{id}
DELETE /tasks/{id}

GET    /health
GET    /metrics

---

## 5. Infrastructure Evolution

The architecture will evolve through multiple stages.

### v0.1 — Local Application

React
  |
FastAPI
  |
PostgreSQL

### v0.2 — Linux Deployment

Linux Server
 |
 +-- Nginx
 |
 +-- FastAPI
 |
 +-- PostgreSQL

### v0.3 — Containerized Application

Docker
 |
 +-- Frontend
 +-- Backend
 +-- PostgreSQL
 +-- Redis

### v0.4 — Docker Compose

                 Nginx
                   |
          +--------+--------+
          |                 |
      Frontend           Backend
                              |
                    +---------+---------+
                    |                   |
                PostgreSQL            Redis

### v0.5 — HTTPS

Internet
   |
 HTTPS
   |
 Nginx
   |
 Backend / Frontend

### v0.6 — CI/CD

Developer
    |
    v
GitHub
    |
    v
GitHub Actions
    |
    +-- Tests
    +-- Lint
    +-- Security checks
    +-- Docker build
    +-- Image push
    +-- Deployment

### v0.7 — AWS

AWS
 |
 +-- VPC
 |    |
 |    +-- Public Subnet
 |    +-- Private Subnet
 |
 +-- EC2
 +-- RDS
 +-- S3
 +-- IAM
 +-- Security Groups
 +-- CloudWatch

### v0.8 — Infrastructure as Code

Terraform will manage the AWS infrastructure.

Terraform
    |
    +-- Network
    +-- Security
    +-- Compute
    +-- Database
    +-- Storage

### v0.9 — Observability

Application / Infrastructure
          |
    +-----+-----+
    |     |     |
    v     v     v
 Metrics Logs  Health
    |     |
    v     v
Prometheus Loki
    |     |
    +--+--+
       |
       v
    Grafana

### v1.0 — Kubernetes

The application will first be deployed to a local Kubernetes environment.

Core Kubernetes resources will include:

- Namespace
- Deployment
- Service
- ConfigMap
- Secret
- Ingress
- Health probes
- Resource requests and limits
- Persistent storage where required
- HPA

### v1.1 — AWS EKS

The Kubernetes deployment will eventually move to Amazon EKS.

---

## 6. Production Engineering

The final architecture will progressively introduce:

- Health checks
- Readiness probes
- Liveness probes
- Graceful shutdown
- Resource limits
- Horizontal autoscaling
- Rolling deployments
- Blue/green deployments
- Rollbacks
- Database backups
- Disaster recovery
- Monitoring
- Centralized logging
- Security scanning

---

## 7. Architecture Principles

### Simplicity

Do not introduce infrastructure or technologies without a concrete reason.

### Incremental Complexity

Each technology should be introduced only after the underlying problem is understood.

### Reproducibility

Infrastructure and deployments should eventually be reproducible through automation and Infrastructure as Code.

### Observability

Systems should expose enough information to understand their behavior and diagnose failures.

### Security

Credentials must never be committed to source control.

Systems should follow least-privilege principles wherever practical.

### Failure Awareness

Every major component should have documented failure modes and troubleshooting procedures.

### Cost Awareness

AWS architecture should distinguish between learning/demo infrastructure and production-scale infrastructure.

---

## 8. Current State

Current project phase:

Phase 0 — Architecture + Environment Setup

Current implementation:

- Git repository initialized
- GitHub repository configured
- Initial repository structure created
- Application implementation not started
- Infrastructure not deployed
