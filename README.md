# ExperienceLoop

Gain practical experience before getting your first job.

ExperienceLoop is a micro-experience platform for BTech students and fresh graduates. It connects students with real-world, short-term technical problems posted by businesses, startups, NGOs, and organizations.

## The Core Loop

```
Real Problem → Student/Team → Real Solution → Feedback → Verified Experience
```

Instead of asking a fresher to prove experience through certificates alone, ExperienceLoop gives them a way to build evidence of what they actually solved, built, and delivered.

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Core Product Loop](#core-product-loop)
- [User Roles](#user-roles)
- [Major Features](#major-features)
- [AI Features](#ai-features)
- [Website Experience](#website-experience)
- [Frontend](#frontend)
- [Backend Architecture](#backend-architecture)
- [Project Structure](#project-structure)
- [Core Pages](#core-pages)
- [Core API Modules](#core-api-modules)
- [Data Model](#data-model)
- [Security](#security)
- [Development Setup](#development-setup)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Product Philosophy](#product-philosophy)

---

## Problem

Students and fresh graduates face an **experience paradox**:

- Companies expect practical experience
- Entry-level opportunities already require previous experience
- This creates a vicious cycle: **No Experience → Difficult to Get Opportunities → No Practical Exposure → Still No Experience**

At the same time, small businesses, startups, NGOs, and local organizations often have smaller technical problems that don't justify hiring a full-time developer.

**ExperienceLoop solves this by connecting these two sides.**

---

## Solution

ExperienceLoop lets an organization post a clearly defined technical problem. A student or student team can then:

1. Understand the requirement
2. Apply for the project
3. Get selected
4. Work on the solution
5. Track tasks and milestones
6. Submit the deliverable
7. Receive structured organizational feedback
8. Build a verified practical-experience record

The goal is to create a practical-experience layer before full-time employment.

---

## Core Product Loop

```
┌─────────────────────┐
│   Organization      │
│   posts problem     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AI structures     │
│   the requirement   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Students discover  │
│  and apply          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Student / Team     │
│  gets selected      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Project Workspace  │
│  tasks + milestones │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Deliverable        │
│  submission         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Organization review│
│  + feedback         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Verified Experience│
│  Record             │
└─────────────────────┘
```

---

## User Roles

### 1. Student

Students can:
- Create an account
- Build a professional profile
- Add technical skills
- Add projects and certifications
- Add GitHub/portfolio links
- Discover real-world projects
- Search and filter projects
- Apply individually or as a team
- Track assigned projects
- Manage tasks and milestones
- Submit deliverables
- Receive feedback
- Build a verified experience profile

### 2. Organization

Organizations can:
- Create an organization profile
- Post real-world technical problems
- Define required skills
- Define expected deliverables
- Set estimated duration, difficulty, and preferred team size
- Review applicants
- Select students or teams
- Track project progress
- Review submissions
- Provide structured feedback

### 3. Admin

Admins can:
- Verify organizations
- Monitor projects
- Moderate content
- Monitor platform activity
- Handle disputes
- Review suspicious activity
- Manage reported users/projects
- Maintain platform integrity

---

## Major Features

### Authentication

- Student/Organization/Admin registration and login
- JWT-based authentication
- Role-based access control
- Protected routes and session/token handling
- Secure password management

### Student Profile

```
Profile
├── Name
├── Profile photo
├── Headline
├── Bio
├── Academic background
├── Technical skills
├── Projects
├── Certifications
├── GitHub & Portfolio links
└── Verified ExperienceLoop Projects
```

### Project Discovery

Students have a dedicated project marketplace with filters:
- Technology
- Skill
- Difficulty
- Duration
- Team size
- Project status
- Category

### Project Posting

Organizations create projects through a guided form with:
- Project title
- Problem description
- Required skills
- Expected deliverables
- Estimated duration
- Difficulty level
- Preferred team size

---

## AI Features

AI is used where it solves meaningful product problems:

### 1. AI Project Structuring
Convert unstructured requirements into:
- Problem statement
- Project scope
- Required skills
- Suggested features
- Deliverables
- Acceptance criteria
- Difficulty estimate

### 2. Skill Matching
Match students with suitable projects based on:
- Skills
- Interests
- Previous projects
- Academic background
- ExperienceLoop history

### 3. Difficulty Estimation
Classify projects as: Beginner, Intermediate, Advanced

### 4. Requirement Analysis
Identify:
- Technologies
- Features
- Dependencies
- Deliverables
- Potential project risks

### 5. Progress Assistance
Help students break projects into manageable tasks.

### 6. Final Project Evaluation
Perform initial evaluation by comparing submitted projects against original requirements.

**Note:** AI evaluation doesn't replace the organization; organization review remains important for final validation.

---

## Website Experience

### Public Website

**Landing Page Sections:**
- Hero
- Problem
- How ExperienceLoop works
- For Students / For Organizations
- How verified experience works
- AI capabilities
- Example projects
- Call to action

### Student Dashboard

```
Welcome back, Student

Profile Completion        82%
Active Projects           2
Completed Projects        5
Verified Experience       5
Average Rating            4.6/5

Recommended Projects
-------------------
Project A | Project B | Project C

Active Work
-----------
Project X ██████████████░░ 78%

Upcoming Milestones
-------------------
Database module | Final submission
```

### Organization Dashboard

```
Active Projects       4
Applications          18
Completed Projects    11

Recent Projects
-----------
Inventory Management | Order Management
Website Analytics    | CRM Automation

[Post New Problem]
```

### Project Workspace

Once selected, the project becomes a workspace with sections:
- Overview
- Tasks
- Milestones
- Team
- Messages
- Files
- Documentation
- Submissions
- Feedback

---

## Project Lifecycle

```
DRAFT
  ↓
PUBLISHED
  ↓
APPLICATIONS_OPEN
  ↓
SELECTION
  ↓
IN_PROGRESS
  ↓
SUBMITTED
  ↓
UNDER_REVIEW
  ↓
COMPLETED
  ↓
VERIFIED_EXPERIENCE
```

Exceptional states: `CANCELLED`, `DISPUTED`, `REJECTED`

### Applications

Application states:
- `PENDING`
- `SHORTLISTED`
- `ACCEPTED`
- `REJECTED`
- `WITHDRAWN`

### Teams

Projects support individual students or teams. Example:
```
Team Alpha

Student 1 → Backend
Student 2 → Frontend
Student 3 → Database
Student 4 → AI / Integration
```

### Tasks and Milestones

```
Milestone 1
├── Requirement analysis
├── Database design
└── API planning

Milestone 2
├── Backend
├── Frontend
└── Integration

Milestone 3
├── Testing
├── Documentation
└── Final submission
```

**Task Fields:** Title, Description, Assignee, Priority, Status, Due date, Attachments, Comments

**Task Status:** `TODO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`

### Submission System

Students submit:
- Project files/repository
- Deployment URL
- Documentation
- Screenshots
- Demo video URL
- Final notes

**Submission Status:** `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`

### Organization Review

Organizations evaluate submissions using:
| Category | Score |
|----------|-------|
| Technical Implementation | /5 |
| Requirement Fulfillment | /5 |
| Communication | /5 |
| Problem Solving | /5 |
| Overall | /5 |

### Verified Experience Record

Instead of: *"Worked on an inventory management project."*

ExperienceLoop creates an evidence-based record containing:
- Project name
- Role
- Problem Solved
- Technologies
- Deliverables
- Duration
- Organization
- Project Outcome
- Organization Feedback
- Rating
- Verification Status

---

## Frontend

### Tech Stack
- **React** (primary frontend framework)
- React Router
- JavaScript or TypeScript
- CSS / CSS Modules
- Fetch API or Axios
- Context API or lightweight state-management

### Architecture

```
React App
│
├── Authentication
│
├── Public Pages
│
├── Student Portal
│   ├── Dashboard
│   ├── Profile
│   ├── Projects
│   ├── Applications
│   ├── Workspace
│   └── Experience
│
├── Organization Portal
│   ├── Dashboard
│   ├── Organization Profile
│   ├── Projects
│   ├── Applications
│   ├── Workspace
│   └── Reviews
│
└── Admin Portal
    ├── Dashboard
    ├── Organizations
    ├── Projects
    ├── Users
    └── Reports
```

---

## Backend Architecture

### Tech Stack
- **Python** with FastAPI or Django REST Framework
- PostgreSQL (production database)
- JWT authentication
- REST API

### API Services

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── organizations.py
│   │   ├── projects.py
│   │   ├── applications.py
│   │   ├── workspaces.py
│   │   ├── submissions.py
│   │   ├── feedback.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   ├── matching_service.py
│   │   ├── evaluation_service.py
│   │   └── ai_service.py
│   │
│   └── utils/
│
└── requirements.txt
```

---

## Project Structure

```
experienceloop/
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── forms/
│   │   │   ├── project/
│   │   │   ├── dashboard/
│   │   │   └── workspace/
│   │   ├── layouts/
│   │   │   ├── PublicLayout.jsx
│   │   │   ├── StudentLayout.jsx
│   │   │   ├── OrganizationLayout.jsx
│   │   │   └── AdminLayout.jsx
│   │   ├── pages/
│   │   │   ├── public/
│   │   │   ├── auth/
│   │   │   ├── student/
│   │   │   ├── organization/
│   │   │   └── admin/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── routes/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env
│
├── README.md
└── .gitignore
```

---

## Core Pages

### Public
- `/` - Home
- `/how-it-works` - Platform overview
- `/projects` - Browse projects
- `/about` - About page
- `/login` - Login
- `/register` - Registration

### Student
- `/student/dashboard` - Dashboard
- `/student/profile` - Profile
- `/student/projects` - My projects
- `/student/projects/:id` - Project details
- `/student/applications` - Applications
- `/student/workspaces/:id` - Active workspace
- `/student/experience` - Experience records
- `/student/settings` - Settings

### Organization
- `/organization/dashboard` - Dashboard
- `/organization/profile` - Profile
- `/organization/projects` - Projects
- `/organization/projects/create` - Create project
- `/organization/projects/:id` - Project details
- `/organization/projects/:id/applications` - Applications
- `/organization/workspaces/:id` - Active workspace
- `/organization/reviews` - Reviews

### Admin
- `/admin/dashboard` - Dashboard
- `/admin/users` - Users
- `/admin/organizations` - Organizations
- `/admin/projects` - Projects
- `/admin/disputes` - Disputes
- `/admin/reports` - Reports

---

## Core API Modules

**REST API Endpoints:**

```
/auth
/students
/organizations
/projects
/applications
/teams
/tasks
/milestones
/workspaces
/submissions
/feedback
/experience
/admin
```

**Example Endpoints:**
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
POST   /api/projects/{id}/apply
GET    /api/projects/{id}/applications
POST   /api/projects/{id}/select
GET    /api/workspaces/{id}
POST   /api/workspaces/{id}/tasks
POST   /api/submissions
POST   /api/feedback
GET    /api/students/{id}/experience
```

---

## Data Model

### Main Entities

- **User** - Base user account
- **StudentProfile** - Student-specific data
- **Organization** - Organization profile
- **Project** - Project listing
- **ProjectSkill** - Required skills
- **Application** - Student application
- **Team** - Team grouping
- **TeamMember** - Team membership
- **Workspace** - Project workspace
- **Task** - Individual tasks
- **Milestone** - Project milestones
- **Submission** - Deliverable submission
- **Feedback** - Organization feedback
- **ExperienceRecord** - Verified experience
- **Notification** - User notifications
- **Message** - Communications
- **Report** - User reports

### Relationships

```
User
 ├── StudentProfile
 └── Organization

Organization
 └── Projects

Project
 ├── Skills
 ├── Applications
 ├── Team
 ├── Workspace
 └── Submissions

Workspace
 ├── Tasks
 ├── Milestones
 ├── Messages
 └── Files

Project
 └── ExperienceRecord
```

### Authentication & Authorization

Authentication uses **JWT**:

```
React
  ↓
JWT Token
  ↓
FastAPI
  ↓
Authentication
  ↓
Role Authorization
  ↓
Business Logic
  ↓
Database
```

**Roles:** `STUDENT`, `ORGANIZATION`, `ADMIN`

---

## Security

Production implementation should include:

- ✅ Password hashing (bcrypt)
- ✅ JWT authentication with secure tokens
- ✅ Role-based authorization (RBAC)
- ✅ Input validation
- ✅ API request validation
- ✅ File type validation & size limits
- ✅ Secure file storage
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Audit logs
- ✅ Organization verification
- ✅ Protected admin endpoints
- ✅ Server-side authorization checks

---

## Development Setup

### Prerequisites

- Node.js & npm
- Python 3.11+
- PostgreSQL
- Git

### Clone Repository

```bash
git clone <repository-url>
cd experienceloop
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The React application will run locally at `http://localhost:5173`

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API
uvicorn app.main:app --reload
```

The API will run at `http://localhost:8000`

---

## Environment Variables

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)

```
DATABASE_URL=postgresql://user:password@localhost:5432/experienceloop

JWT_SECRET_KEY=your-secret-key

AI_API_KEY=your-ai-api-key

CORS_ORIGINS=http://localhost:5173
```

**⚠️ Never commit secrets to GitHub**

---

## Deployment

### Production Architecture

```
Internet
   │
   ▼
Custom Domain
   │
   ├─────────────────────┬─────────────────────┐
   ▼                     ▼
React Frontend      FastAPI Backend
   │                     │
   │                     ▼
   │                PostgreSQL
   │
   └──────────── API ────────────────┘
```

Deploy on production-ready platforms with support for:
- Containerization (Docker)
- CI/CD pipelines
- Database backups
- SSL/TLS certificates
- Custom domain configuration

---

## Roadmap

### MVP Scope

#### Phase 1 - Foundation
- React frontend setup
- Authentication system
- Student registration
- Organization registration
- Role-based dashboards
- PostgreSQL database
- REST API

#### Phase 2 - Project Marketplace
- Organization project creation
- Project discovery and search
- Project filtering
- Project details page
- Student applications
- Organization selection

#### Phase 3 - Project Workspace
- Team management
- Tasks and milestones
- In-project communication
- File and document submission
- Progress tracking

#### Phase 4 - Verification
- Submission review system
- Organization feedback collection
- Rating system
- Verified experience record creation
- Student experience profile

#### Phase 5 - AI Integration
- Requirement structuring
- Skill matching algorithm
- Difficulty estimation
- Requirement analysis
- Progress assistance
- Initial project evaluation

### Long-Term Roadmap

ExperienceLoop can evolve into a broader practical-experience ecosystem:

- Advanced student/project matching algorithms
- Reputation and credibility system
- Organization verification levels
- Public verified portfolios
- Recruiter access and integration
- Skill analytics and insights
- Project recommendations engine
- Team formation assistance
- Project templates library
- Organization analytics dashboard
- Advanced AI-powered career guidance
- Career-readiness scoring system

---

## Product Philosophy

ExperienceLoop follows five core principles:

### 1. Real Problems
Projects originate from genuine organizational needs.

### 2. Real Work
Students actually build and deliver something valuable.

### 3. Real Feedback
Organizations evaluate and provide meaningful feedback.

### 4. Verifiable Evidence
Completed work becomes structured evidence of experience.

### 5. Job Readiness
The platform helps students become job-ready.

### Traditional Internship vs ExperienceLoop

| Aspect | Traditional Model | ExperienceLoop |
|--------|-------------------|-----------------|
| Entry Point | Apply for internship | Discover real problem |
| Timeline | Selection takes weeks | Project has defined scope |
| Experience Building | After getting position | Through selected micro-projects |
| Record | Certificate | Deliverables + feedback + verified evidence |
| Ecosystem | Organization-centric | Student + organization collaboration |
| Commitment | Long internship | Short, well-defined projects |

**Key Transformation:**
```
Traditional:  Student → Apply → Internship/Job → Experience

ExperienceLoop: Real Problem → Student → Real Solution → Feedback → Verified Experience
```

### Example End-to-End Flow

**Scenario: Restaurant Order Management System**

1. **Organization**
   - Restaurant has manual order system with frequent errors
   - Posts project on ExperienceLoop

2. **AI**
   - Structures requirement into clear modules:
     - Authentication
     - Order management
     - Dashboard
     - Reports
     - Database design

3. **Students**
   - Four-person team applies:
     - Student 1: Backend
     - Student 2: Frontend
     - Student 3: Database
     - Student 4: AI/Integration

4. **Workspace**
   - Team receives structured tasks and milestones
   - Tracks progress with documentation and communication

5. **Delivery**
   - Team builds and submits working system

6. **Organization Review**
   - Restaurant tests and provides structured feedback

7. **Verified Experience**
   - Platform creates permanent, verified experience record

### Success Metrics

**Primary Success Metric:** How many students completed real projects and obtained verifiable evidence of practical experience?

**Platform Metrics:**
- Registered Students
- Verified Organizations
- Projects Posted
- Total Applications
- Projects Started
- Projects Completed
- Verified Experience Records Generated
- Average Organization Rating
- Student Completion Rate

---

## Vision

**ExperienceLoop aims to become the bridge between learning and employment.**

A student should join with limited experience and gradually build a credible practical profile by solving real problems.

```
LEARN
  ↓
REAL-WORLD PROJECTS
  ↓
BUILD
  ↓
FEEDBACK
  ↓
VERIFIED EXPERIENCE
  ↓
JOB-READY
  ↓
HIRED
```

---

## One-Line Pitch

*ExperienceLoop is a platform that helps students overcome the experience paradox by connecting them with real-world micro-projects from businesses and organizations, allowing them to build verifiable evidence of practical experience before their first job.*

---

## Project Status

| Aspect | Details |
|--------|---------|
| **Project** | ExperienceLoop |
| **Category** | Micro-Experience Platform |
| **Target Users** | Students, fresh graduates, businesses, startups, NGOs, organizations, recruiters |
| **Frontend** | React |
| **Backend** | Python (FastAPI or Django REST Framework) |
| **Database** | PostgreSQL |
| **Authentication** | JWT + RBAC |
| **AI Capabilities** | Requirement structuring, matching, analysis, assistance, evaluation |
| **Development** | Git + GitHub |
| **Deployment** | Production-ready web with custom domain |

---

## Final Goal

**ExperienceLoop is not another job portal.**

It exists to answer one question:

> *"How can a student prove they have real-world experience before they get their first job?"*

**The answer:**

Give them real problems to solve, let them build real solutions, collect real feedback, and turn the completed work into verifiable experience.

---

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]

---

*Last Updated: September 2026*
