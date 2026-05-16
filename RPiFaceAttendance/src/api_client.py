import requests
import json

class APIClient:
    def __init__(self, base_url="https://powercampusapi.runasp.net"):
        self.base_url = base_url
        self.token = None
        self.user_info = None

    def login(self, email, password):
        url = f"{self.base_url}/api/Auth/login"
        payload = {
            "email": email,
            "password": password
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_info = data
                return True
        except Exception as e:
            print(f"Login connection error: {e}")
        return False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_courses(self):
        url = f"{self.base_url}/api/Courses"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching courses: {e}")
        return []

    def get_all_students(self):
        # Using Users endpoint - requires Admin but we'll try
        url = f"{self.base_url}/api/Users"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                users = response.json()
                # filter for students if role is available in response
                return [u for u in users if u.get('role') == 'Student']
        except Exception as e:
            print(f"Error fetching students: {e}")
        return []

    def get_course_students(self, course_id):
        url = f"{self.base_url}/api/Enrollments/course/{course_id}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching course students: {e}")
        return []

    def get_lectures(self, course_id):
        url = f"{self.base_url}/api/Lectures/course/{course_id}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching lectures: {e}")
        return []

    def mark_attendance(self, student_id, course_id, lecture_id=None, is_present=True):
        url = f"{self.base_url}/api/Attendance"
        from datetime import datetime
        payload = {
            "studentId": student_id,
            "courseId": course_id,
            "lectureId": lecture_id,
            "date": datetime.now().isoformat(),
            "isPresent": is_present
        }
        response = requests.post(url, json=payload, headers=self.get_headers())
        return response.status_code == 200 or response.status_code == 201

    def start_session(self, course_id, lecture_id=None):
        url = f"{self.base_url}/api/Attendance/session/start"
        payload = {
            "courseId": course_id,
            "lectureId": lecture_id
        }
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            return response.status_code == 200
        except Exception as e:
            print(f"Error starting session: {e}")
        return False

    def stop_session(self):
        url = f"{self.base_url}/api/Attendance/session/stop"
        try:
            response = requests.post(url, headers=self.get_headers())
            return response.status_code == 200
        except Exception as e:
            print(f"Error stopping session: {e}")
        return False
