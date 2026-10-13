import unittest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, Base

class TestExperienceLoopE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create all database tables
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    def test_01_health_and_root(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "online")

        res_health = self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "healthy")

    def test_02_full_workflow(self):
        client = self.client

        # 1. Register Admin
        admin_email = "admin_test@experienceloop.com"
        res_admin_reg = client.post("/api/v1/auth/register", json={
            "email": admin_email,
            "password": "SecurePassword123!",
            "role": "ADMIN",
            "full_name": "Platform Administrator"
        })
        # If already exists from earlier run, login instead
        if res_admin_reg.status_code == 201:
            admin_token = res_admin_reg.json()["access_token"]
        else:
            res_admin_login = client.post("/api/v1/auth/login", json={
                "email": admin_email,
                "password": "SecurePassword123!"
            })
            self.assertEqual(res_admin_login.status_code, 200)
            admin_token = res_admin_login.json()["access_token"]

        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Register Organization
        org_email = "org_director@techcorp.io"
        res_org_reg = client.post("/api/v1/auth/register", json={
            "email": org_email,
            "password": "SecurePassword123!",
            "role": "ORGANIZATION",
            "organization_name": "TechCorp Innovations"
        })
        if res_org_reg.status_code == 201:
            org_token = res_org_reg.json()["access_token"]
        else:
            res_org_login = client.post("/api/v1/auth/login", json={
                "email": org_email,
                "password": "SecurePassword123!"
            })
            org_token = res_org_login.json()["access_token"]

        org_headers = {"Authorization": f"Bearer {org_token}"}

        # 3. Register Student
        student_email = "jane_doe@student.edu"
        res_stu_reg = client.post("/api/v1/auth/register", json={
            "email": student_email,
            "password": "SecurePassword123!",
            "role": "STUDENT",
            "full_name": "Jane Doe"
        })
        if res_stu_reg.status_code == 201:
            stu_token = res_stu_reg.json()["access_token"]
        else:
            res_stu_login = client.post("/api/v1/auth/login", json={
                "email": student_email,
                "password": "SecurePassword123!"
            })
            stu_token = res_stu_login.json()["access_token"]

        stu_headers = {"Authorization": f"Bearer {stu_token}"}

        # Verify /auth/me for each
        res_me_stu = client.get("/api/v1/auth/me", headers=stu_headers)
        self.assertEqual(res_me_stu.status_code, 200)
        self.assertEqual(res_me_stu.json()["role"], "STUDENT")

        # 4. Student profile update
        res_stu_profile = client.get("/api/v1/students/me", headers=stu_headers)
        self.assertEqual(res_stu_profile.status_code, 200)
        student_profile_id = res_stu_profile.json()["id"]

        res_update_stu = client.put("/api/v1/students/me", json={
            "headline": "Aspiring Full Stack Engineer",
            "university": "State University",
            "degree_program": "B.S. Computer Science",
            "bio": "Passionate about building scalable backend APIs."
        }, headers=stu_headers)
        self.assertEqual(res_update_stu.status_code, 200)

        # 5. Create skill catalog entries
        res_skill = client.post("/api/v1/skills/", json={
            "name": "FastAPI",
            "category": "Backend Frameworks"
        }, headers=admin_headers)
        if res_skill.status_code == 201:
            skill_id = res_skill.json()["id"]
        else:
            # Look up skill
            res_skills = client.get("/api/v1/skills/?query=FastAPI")
            skill_id = res_skills.json()["items"][0]["id"]

        # Student attaches skill
        client.post("/api/v1/students/me/skills", json={
            "skill_id": skill_id,
            "proficiency": "ADVANCED",
            "is_primary": True
        }, headers=stu_headers)

        # 6. Organization creates project
        res_project = client.post("/api/v1/projects/", json={
            "title": "API Gateway Microservice",
            "problem_description": "We need a performant API Gateway microservice with rate limiting, logging, and JWT validation.",
            "deliverables": "Working Dockerized FastAPI service, OpenAPI documentation, and integration tests.",
            "estimated_duration_days": 14,
            "difficulty": "INTERMEDIATE",
            "skills": [
                {"skill_id": skill_id, "is_required": True, "minimum_proficiency": "INTERMEDIATE"}
            ]
        }, headers=org_headers)
        self.assertEqual(res_project.status_code, 201)
        project_id = res_project.json()["id"]

        # Publish project
        res_pub = client.patch(f"/api/v1/projects/{project_id}/status", json={
            "status": "APPLICATIONS_OPEN"
        }, headers=org_headers)
        self.assertEqual(res_pub.status_code, 200)
        self.assertEqual(res_pub.json()["status"], "APPLICATIONS_OPEN")

        # 7. AI Assistive Features on Project
        # 7a. Structure
        res_ai_struct = client.post("/api/v1/ai/structure", json={"project_id": project_id}, headers=org_headers)
        self.assertEqual(res_ai_struct.status_code, 201)
        self.assertEqual(res_ai_struct.json()["analysis_type"], "STRUCTURE")

        # 7b. Difficulty
        res_ai_diff = client.post("/api/v1/ai/difficulty", json={"project_id": project_id}, headers=org_headers)
        self.assertEqual(res_ai_diff.status_code, 201)

        # 7c. Requirements
        res_ai_req = client.post("/api/v1/ai/requirements", json={"project_id": project_id}, headers=org_headers)
        self.assertEqual(res_ai_req.status_code, 201)

        # 7d. Match
        res_ai_match = client.post("/api/v1/ai/match", json={
            "project_id": project_id,
            "student_id": student_profile_id
        }, headers=org_headers)
        self.assertEqual(res_ai_match.status_code, 201)

        # 8. Student applies to project
        res_apply = client.post("/api/v1/applications/", json={
            "project_id": project_id,
            "cover_letter": "I have extensive experience with FastAPI and would love to build this gateway."
        }, headers=stu_headers)
        self.assertEqual(res_apply.status_code, 201)
        app_id = res_apply.json()["id"]

        # 9. Organization reviews and ACCEPTS application
        res_accept = client.patch(f"/api/v1/applications/{app_id}/status", json={
            "status": "ACCEPTED"
        }, headers=org_headers)
        self.assertEqual(res_accept.status_code, 200)
        self.assertEqual(res_accept.json()["status"], "ACCEPTED")

        # Verify project transitioned to IN_PROGRESS
        res_proj_refreshed = client.get(f"/api/v1/projects/{project_id}")
        self.assertEqual(res_proj_refreshed.json()["status"], "IN_PROGRESS")

        # Verify Team & Member exists
        res_team = client.get(f"/api/v1/teams/project/{project_id}", headers=org_headers)
        self.assertEqual(res_team.status_code, 200)
        team_data = res_team.json()
        self.assertTrue(len(team_data["members"]) >= 1)

        # 10. Workspace Collaboration
        res_ws = client.get(f"/api/v1/workspaces/project/{project_id}", headers=stu_headers)
        self.assertEqual(res_ws.status_code, 200)
        ws_id = res_ws.json()["id"]

        # Add milestone
        res_m = client.post(f"/api/v1/workspaces/{ws_id}/milestones", json={
            "title": "Phase 1: Foundation Setup",
            "description": "Initialize boilerplate and routing",
            "sequence_no": 1
        }, headers=org_headers)
        self.assertEqual(res_m.status_code, 201)
        milestone_id = res_m.json()["id"]

        # Add task
        res_t = client.post(f"/api/v1/workspaces/{ws_id}/tasks", json={
            "title": "Setup Docker Compose & Environment",
            "priority": "HIGH",
            "milestone_id": milestone_id,
            "assigned_to": student_profile_id
        }, headers=org_headers)
        self.assertEqual(res_t.status_code, 201)
        task_id = res_t.json()["id"]

        # Update task status
        res_t_status = client.patch(f"/api/v1/workspaces/tasks/{task_id}/status", json={
            "status": "COMPLETED"
        }, headers=stu_headers)
        self.assertEqual(res_t_status.status_code, 200)
        self.assertEqual(res_t_status.json()["status"], "COMPLETED")

        # Workspace messaging
        res_msg = client.post(f"/api/v1/workspaces/{ws_id}/messages", json={
            "body": "Hi team, I finished setting up the Docker environment!"
        }, headers=stu_headers)
        self.assertEqual(res_msg.status_code, 201)

        res_msg_list = client.get(f"/api/v1/workspaces/{ws_id}/messages", headers=org_headers)
        self.assertEqual(res_msg_list.status_code, 200)
        self.assertTrue(len(res_msg_list.json()) >= 1)

        # File upload & download
        dummy_file_bytes = b"Hello, ExperienceLoop Project File Content!"
        res_file_upload = client.post(
            f"/api/v1/workspaces/{ws_id}/files",
            files={"file": ("architecture_diagram.txt", io.BytesIO(dummy_file_bytes), "text/plain")},
            headers=stu_headers
        )
        self.assertEqual(res_file_upload.status_code, 201)
        file_id = res_file_upload.json()["id"]

        res_file_dl = client.get(f"/api/v1/workspaces/files/{file_id}/download", headers=org_headers)
        self.assertEqual(res_file_dl.status_code, 200)
        self.assertEqual(res_file_dl.content, dummy_file_bytes)

        # 11. AI Progress Analysis
        res_ai_prog = client.post("/api/v1/ai/progress", json={"project_id": project_id}, headers=org_headers)
        self.assertEqual(res_ai_prog.status_code, 201)

        # 12. Student Submits Project Deliverables
        res_sub = client.post("/api/v1/submissions/", json={
            "project_id": project_id,
            "repository_url": "https://github.com/student/api-gateway",
            "deployment_url": "https://api-gateway.demo.com",
            "documentation_url": "https://api-gateway.demo.com/docs",
            "notes": "Completed all endpoints with full test suite passing."
        }, headers=stu_headers)
        self.assertEqual(res_sub.status_code, 201)
        submission_id = res_sub.json()["id"]

        # 13. AI Evaluation Analysis
        res_ai_eval = client.post("/api/v1/ai/evaluation", json={
            "project_id": project_id,
            "submission_id": submission_id
        }, headers=org_headers)
        self.assertEqual(res_ai_eval.status_code, 201)

        # 14. Organization Review & Approval via Feedback
        res_feedback = client.post("/api/v1/feedback/", json={
            "project_id": project_id,
            "submission_id": submission_id,
            "technical_implementation": 5.0,
            "requirement_fulfillment": 4.8,
            "communication": 5.0,
            "problem_solving": 4.9,
            "overall_rating": 4.9,
            "comments": "Outstanding work! Code is clean, well-tested, and fully meets specifications."
        }, headers=org_headers)
        self.assertEqual(res_feedback.status_code, 201)

        # 15. Verify Experience Record Created for Student
        res_my_exp = client.get("/api/v1/experience/my", headers=stu_headers)
        self.assertEqual(res_my_exp.status_code, 200)
        exp_items = res_my_exp.json()["items"]
        self.assertTrue(len(exp_items) >= 1)
        public_slug = exp_items[0]["public_slug"]

        # Verify Public slug endpoint (No auth header needed)
        res_pub_exp = client.get(f"/api/v1/experience/public/{public_slug}")
        self.assertEqual(res_pub_exp.status_code, 200)
        self.assertEqual(res_pub_exp.json()["verification_status"], "VERIFIED")

        # 16. Notifications check
        res_notif = client.get("/api/v1/notifications/", headers=stu_headers)
        self.assertEqual(res_notif.status_code, 200)
        res_unread = client.get("/api/v1/notifications/unread-count", headers=stu_headers)
        self.assertEqual(res_unread.status_code, 200)

        # 17. Admin Management & Dashboard
        res_stats = client.get("/api/v1/admin/stats", headers=admin_headers)
        self.assertEqual(res_stats.status_code, 200)
        self.assertTrue(res_stats.json()["total_users"] >= 3)
        self.assertTrue(res_stats.json()["verified_experiences"] >= 1)

        # Submit a report
        res_report = client.post("/api/v1/admin/reports", json={
            "entity_type": "project",
            "entity_id": project_id,
            "reason": "Test question about project scope",
            "description": "Checking project requirements"
        }, headers=stu_headers)
        self.assertEqual(res_report.status_code, 201)
        report_id = res_report.json()["id"]

        # Resolve report
        res_resolve = client.patch(f"/api/v1/admin/reports/{report_id}/resolve", json={
            "status": "RESOLVED"
        }, headers=admin_headers)
        self.assertEqual(res_resolve.status_code, 200)

        # Audit logs check
        res_audit = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        self.assertEqual(res_audit.status_code, 200)
        self.assertTrue(res_audit.json()["total"] >= 1)


if __name__ == "__main__":
    unittest.main()