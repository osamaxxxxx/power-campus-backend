import customtkinter as ctk
import cv2
import os
from PIL import Image, ImageTk
from tkinter import filedialog
import threading
import time
import numpy as np
import platform
from api_client import APIClient
from face_service import FaceService

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Power Campus - Biometric Attendance")
        self.geometry("1100x750")

        self.api_client = APIClient()
        self.face_service = FaceService()

        # UI state
        self.current_frame = None
        self.cap = None
        self.is_camera_running = False
        self.selected_course = None
        self.selected_lecture = None
        self.students = []
        self.courses = []
        self.lectures = []

        # Registration state
        self.captured_faces = []        # list of face ROI numpy arrays
        self.reg_target_count = 10      # how many captures we want
        self.is_auto_capturing = False  # auto-capture mode flag

        # Create sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="POWER CAMPUS",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(pady=20, padx=10)

        self.login_btn = ctk.CTkButton(self.sidebar, text="Login", command=self.show_login)
        self.login_btn.pack(pady=10, padx=20)

        self.reg_btn = ctk.CTkButton(
            self.sidebar, text="Register Face",
            command=self.show_registration, state="disabled"
        )
        self.reg_btn.pack(pady=10, padx=20)

        self.att_btn = ctk.CTkButton(
            self.sidebar, text="Attendance Session",
            command=self.show_attendance, state="disabled"
        )
        self.att_btn.pack(pady=10, padx=20)

        # Main content area
        self.main_content = ctk.CTkFrame(self, corner_radius=10)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.show_login()

    # ================================================================== #
    #  Helpers                                                             #
    # ================================================================== #

    def run_in_thread(self, task_func, callback=None):
        """Run task in background thread; call callback on the main thread."""
        def wrapper():
            result = task_func()
            if callback:
                self.after(0, lambda: callback(result))
        threading.Thread(target=wrapper, daemon=True).start()

    def clear_main_content(self):
        self.stop_camera()
        self.is_auto_capturing = False
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # ================================================================== #
    #  Login                                                               #
    # ================================================================== #

    def show_login(self):
        self.clear_main_content()

        ctk.CTkLabel(
            self.main_content, text="Instructor Login",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=40)

        self.email_entry = ctk.CTkEntry(self.main_content, placeholder_text="Email", width=300)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.main_content, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.main_content, text="Login", command=self.handle_login).pack(pady=20)

        self.login_status = ctk.CTkLabel(self.main_content, text="")
        self.login_status.pack(pady=10)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        for widget in self.main_content.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(state="disabled")

        def do_login():
            return self.api_client.login(email, password)

        def on_login_result(success):
            if success:
                self.login_status.configure(text="Login Successful!", text_color="green")
                self.reg_btn.configure(state="normal")
                self.att_btn.configure(state="normal")
                self.show_attendance()
            else:
                self.login_status.configure(
                    text="Login Failed. Check credentials or connection.", text_color="red"
                )
                for widget in self.main_content.winfo_children():
                    if isinstance(widget, ctk.CTkButton):
                        widget.configure(state="normal")

        self.run_in_thread(do_login, on_login_result)

    # ================================================================== #
    #  Registration  – multi-image with camera auto-capture                #
    # ================================================================== #

    def show_registration(self):
        self.clear_main_content()
        self.captured_faces = []

        ctk.CTkLabel(
            self.main_content, text="Student Face Registration",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)

        # ---- Course / Student selection ----
        selection_frame = ctk.CTkFrame(self.main_content)
        selection_frame.pack(fill="x", padx=20, pady=5)

        self.courses = self.api_client.get_courses()
        course_names = [c['title'] for c in self.courses] or ["No courses"]

        ctk.CTkLabel(selection_frame, text="Course:").grid(row=0, column=0, padx=10, pady=5)
        self.reg_course_var = ctk.StringVar(value=course_names[0])
        self.reg_course_menu = ctk.CTkOptionMenu(
            selection_frame, values=course_names,
            variable=self.reg_course_var, command=self.update_reg_students
        )
        self.reg_course_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(selection_frame, text="Student:").grid(row=1, column=0, padx=10, pady=5)
        self.student_var = ctk.StringVar(value="Select Course First")
        self.student_menu = ctk.CTkOptionMenu(
            selection_frame, values=["Select Course First"],
            variable=self.student_var
        )
        self.student_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        selection_frame.columnconfigure(1, weight=1)

        # ---- Mode selector: Camera vs File images ----
        mode_frame = ctk.CTkFrame(self.main_content)
        mode_frame.pack(fill="x", padx=20, pady=5)

        self.reg_mode_var = ctk.StringVar(value="camera")
        ctk.CTkRadioButton(
            mode_frame, text="📷 Camera Auto-Capture",
            variable=self.reg_mode_var, value="camera"
        ).pack(side="left", padx=20, pady=5)
        ctk.CTkRadioButton(
            mode_frame, text="📁 Upload Images",
            variable=self.reg_mode_var, value="file"
        ).pack(side="left", padx=20, pady=5)

        # ---- Action buttons (فوق الكاميرا) ----
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.open_cam_btn = ctk.CTkButton(
            btn_frame, text="📷  Open Camera",
            command=self.open_registration_camera,
            fg_color="#1a6b9a",
            hover_color="#2980b9",
            text_color="white",
            border_width=2,
            border_color="#3498db"
        )
        self.open_cam_btn.pack(side="left", padx=5, expand=True)

        self.start_capture_btn = ctk.CTkButton(
            btn_frame, text="▶  Start Capture",
            command=self.start_registration_capture, fg_color="#2fa572"
        )
        self.start_capture_btn.pack(side="left", padx=5, expand=True)

        self.upload_btn = ctk.CTkButton(
            btn_frame, text="📁  Upload Images",
            command=self.upload_images
        )
        self.upload_btn.pack(side="left", padx=5, expand=True)

        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑  Clear All",
            command=self.clear_captured, fg_color="#c0392b"
        )
        self.clear_btn.pack(side="left", padx=5, expand=True)

        self.register_btn = ctk.CTkButton(
            btn_frame, text="✅  Register Student",
            command=self.handle_registration, fg_color="#8e44ad"
        )
        self.register_btn.pack(side="left", padx=5, expand=True)

        # ---- Camera feed / preview area (تحت الزراير) ----
        self.reg_cam_label = ctk.CTkLabel(
            self.main_content, text="Select a student and start capture",
            fg_color="black", width=500, height=340
        )
        self.reg_cam_label.pack(pady=5)

        # ---- Status / progress ----
        self.reg_status = ctk.CTkLabel(
            self.main_content, text="", font=ctk.CTkFont(size=14)
        )
        self.reg_status.pack(pady=2)

        self.reg_progress = ctk.CTkProgressBar(self.main_content, width=400)
        self.reg_progress.pack(pady=2)
        self.reg_progress.set(0)

        self.reg_count_label = ctk.CTkLabel(
            self.main_content, text="Captured: 0 / 10",
            font=ctk.CTkFont(size=13)
        )
        self.reg_count_label.pack(pady=2)

        # ---- Thumbnails row ----
        self.thumb_frame = ctk.CTkScrollableFrame(
            self.main_content, orientation="horizontal", height=80
        )
        self.thumb_frame.pack(fill="x", padx=20, pady=5)

        self.update_reg_students(course_names[0])

    # ---- Student dropdown ----

    def update_reg_students(self, course_name):
        selected_course = next((c for c in self.courses if c['title'] == course_name), None)
        if selected_course:
            self.student_var.set("Loading students...")
            self.student_menu.configure(state="disabled")

            def fetch():
                return self.api_client.get_course_students(selected_course['id'])

            def on_done(enrollments):
                if hasattr(self, 'student_menu') and self.student_menu.winfo_exists():
                    self.students = [{"name": e['studentName'], "id": e['studentId']} for e in enrollments]
                    sl = [f"{s['name']} ({s['id']})" for s in self.students] or ["No students enrolled"]
                    self.student_menu.configure(values=sl, state="normal")
                    self.student_var.set(sl[0])

            self.run_in_thread(fetch, on_done)

    # ---- Camera auto-capture ----

    def open_registration_camera(self):
        if self.reg_mode_var.get() == "file":
            self.reg_status.configure(text="Please select Camera mode", text_color="red")
            return

        if self.cap is not None:
            self.stop_camera()

        if platform.system() == 'Windows':
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(0)

        self.is_camera_running = True
        self.is_auto_capturing = False

        self.open_cam_btn.configure(state="disabled")

        threading.Thread(target=self._camera_preview_loop, daemon=True).start()

    def start_registration_capture(self):
        if self.reg_mode_var.get() == "file":
            self.upload_images()
            return

        if self.is_auto_capturing:
            self.is_auto_capturing = False
            self.start_capture_btn.configure(text="▶  Start Capture", fg_color="#2fa572")
            return

        if not self.is_camera_running:
            self.open_registration_camera()

        # Start auto-capture
        self.captured_faces = []
        self.update_capture_ui()
        self.is_auto_capturing = True
        self.start_capture_btn.configure(text="⏹  Stop Capture", fg_color="#e74c3c")

    def _camera_preview_loop(self):
        """Camera loop that previews and auto-captures good-quality face crops."""
        last_capture_time = 0
        CAPTURE_INTERVAL = 0.6  # seconds between captures

        while self.is_camera_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.02)
                continue

            face_roi, box, is_good, msg = self.face_service.assess_quality(frame)

            if box is not None:
                x, y, w, h = box
                color = (0, 255, 0) if is_good else (0, 165, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            if self.is_auto_capturing:
                cv2.putText(frame, msg, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                count_text = f"Captured: {len(self.captured_faces)} / {self.reg_target_count}"
                cv2.putText(frame, count_text, (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

                now = time.time()
                if (is_good and face_roi is not None
                        and len(self.captured_faces) < self.reg_target_count
                        and now - last_capture_time >= CAPTURE_INTERVAL):
                    self.captured_faces.append(face_roi.copy())
                    last_capture_time = now
                    cv2.rectangle(frame, (0, 0),
                                  (frame.shape[1] - 1, frame.shape[0] - 1),
                                  (0, 255, 0), 6)
                    self.after(0, self.update_capture_ui)

                if len(self.captured_faces) >= self.reg_target_count:
                    self.after(0, self._auto_capture_done)
                    self._show_frame_on_label(frame)
                    continue
            else:
                cv2.putText(frame, "Preview Mode - Ready to capture", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            self._show_frame_on_label(frame)
            time.sleep(0.03)

    def _show_frame_on_label(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 340))
        self.after(0, lambda i=ctk_img: self._safe_update_reg_cam(i))

    def _safe_update_reg_cam(self, img):
        if hasattr(self, 'reg_cam_label') and self.reg_cam_label.winfo_exists():
            self.reg_cam_label.configure(image=img, text="")
            self.reg_cam_label.image = img

    def _auto_capture_done(self):
        """Called when auto-capture reaches target count."""
        self.is_auto_capturing = False
        self.start_capture_btn.configure(text="▶  Start Capture", fg_color="#2fa572")
        self.reg_status.configure(
            text=f"✅ Captured {len(self.captured_faces)} images! Click 'Register Student' to save.",
            text_color="#2ecc71"
        )

    # ---- File upload ----

    def upload_images(self):
        paths = filedialog.askopenfilenames(
            parent=self,
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not paths:
            return

        added = 0
        for p in paths:
            try:
                stream = open(p, "rb")
                bytes_arr = bytearray(stream.read())
                numpyarray = np.asarray(bytes_arr, dtype=np.uint8)
                frame = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
                if frame is None:
                    continue
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif len(frame.shape) == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                face_roi, box, is_good, msg = self.face_service.assess_quality(frame)
                if face_roi is not None:
                    self.captured_faces.append(face_roi.copy())
                    added += 1
            except Exception as e:
                print(f"Error loading image {p}: {e}")

        self.update_capture_ui()
        self.reg_status.configure(
            text=f"Added {added} faces from {len(paths)} images",
            text_color="#3498db"
        )

    # ---- UI updates ----

    def update_capture_ui(self):
        count = len(self.captured_faces)
        target = self.reg_target_count

        self.reg_progress.set(min(count / target, 1.0))
        self.reg_count_label.configure(text=f"Captured: {count} / {target}")

        for w in self.thumb_frame.winfo_children():
            w.destroy()

        for i, roi in enumerate(self.captured_faces):
            try:
                rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
                lbl = ctk.CTkLabel(self.thumb_frame, image=ctk_img, text="")
                lbl.image = ctk_img
                lbl.pack(side="left", padx=2)
            except Exception:
                pass

    def clear_captured(self):
        self.captured_faces = []
        self.update_capture_ui()
        self.reg_status.configure(text="Cleared all captured images", text_color="orange")

    # ---- Register ----

    def handle_registration(self):
        selected_text = self.student_var.get()
        if "No students" in selected_text or "Select Course" in selected_text or "Loading" in selected_text:
            self.reg_status.configure(text="Please select a student first", text_color="red")
            return

        if not self.captured_faces:
            self.reg_status.configure(text="No face images captured yet", text_color="red")
            return

        student_id = int(selected_text.split("(")[1].split(")")[0])
        faces_to_register = list(self.captured_faces)

        self.reg_status.configure(
            text=f"Registering {len(faces_to_register)} images... please wait",
            text_color="orange"
        )
        self.register_btn.configure(state="disabled")

        def do_reg():
            return self.face_service.register_student_frames(student_id, faces_to_register)

        def on_reg_result(result):
            stored, attempted = result
            total = self.face_service.get_embedding_count(student_id)
            self.register_btn.configure(state="normal")

            if stored > 0:
                self.reg_status.configure(
                    text=f"✅ Registered {stored}/{attempted} images  —  "
                         f"Total embeddings for student: {total}",
                    text_color="#2ecc71"
                )
                self.captured_faces = []
                self.update_capture_ui()
            else:
                self.reg_status.configure(
                    text="❌ No faces could be processed. Try again with better lighting.",
                    text_color="red"
                )

        self.run_in_thread(do_reg, on_reg_result)

    # ================================================================== #
    #  Attendance Session                                                  #
    # ================================================================== #

    def show_attendance(self):
        self.clear_main_content()
        ctk.CTkLabel(
            self.main_content, text="Attendance Session",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)

        selection_frame = ctk.CTkFrame(self.main_content)
        selection_frame.pack(fill="x", padx=20, pady=10)

        self.courses = self.api_client.get_courses()
        course_names = [c['title'] for c in self.courses] or ["No courses"]

        self.course_var = ctk.StringVar(value=course_names[0])
        ctk.CTkLabel(selection_frame, text="Course:").grid(row=0, column=0, padx=10, pady=5)
        self.course_menu = ctk.CTkOptionMenu(
            selection_frame, values=course_names,
            variable=self.course_var, command=self.update_lectures
        )
        self.course_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(selection_frame, text="Lecture:").grid(row=1, column=0, padx=10, pady=5)
        self.lecture_var = ctk.StringVar(value="Select Lecture")
        self.lecture_menu = ctk.CTkOptionMenu(
            selection_frame, values=["Select Course First"],
            variable=self.lecture_var
        )
        self.lecture_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        selection_frame.columnconfigure(1, weight=1)

        self.session_btn = ctk.CTkButton(
            self.main_content, text="Start Session",
            command=self.toggle_attendance_session
        )
        self.session_btn.pack(pady=10)

        self.cam_label = ctk.CTkLabel(
            self.main_content, text="", fg_color="black",
            width=640, height=480
        )
        self.cam_label.pack(pady=10)

        self.present_label = ctk.CTkLabel(
            self.main_content, text="Present: 0",
            font=ctk.CTkFont(size=18)
        )
        self.present_label.pack()

        self.session_active = False
        self.present_students = set()

        self.update_lectures(course_names[0])

    def update_lectures(self, course_name):
        selected_course = next((c for c in self.courses if c['title'] == course_name), None)
        if selected_course:
            self.selected_course = selected_course
            self.lecture_var.set("Loading lectures...")
            self.lecture_menu.configure(state="disabled")

            def fetch_lectures():
                return self.api_client.get_lectures(selected_course['id'])

            def on_lectures_fetched(lectures):
                if hasattr(self, 'lecture_menu') and self.lecture_menu.winfo_exists():
                    self.lectures = lectures
                    titles = [l['title'] for l in self.lectures] or ["No lectures found"]
                    self.lecture_menu.configure(values=titles, state="normal")
                    self.lecture_var.set(titles[0])

            self.run_in_thread(fetch_lectures, on_lectures_fetched)

    def toggle_attendance_session(self):
        if not self.session_active:
            self.session_active = True
            self.session_btn.configure(text="Stop Session", fg_color="red")
            self.present_students = set()
            self.update_present_count()

            selected_lecture_title = self.lecture_var.get()
            self.selected_lecture = next(
                (l for l in self.lectures if l['title'] == selected_lecture_title), None
            )

            course_id = self.selected_course['id']
            lecture_id = self.selected_lecture['id'] if self.selected_lecture else None
            self.run_in_thread(lambda: self.api_client.start_session(course_id, lecture_id))

            self.start_camera(self.cam_label, mode="attendance")
        else:
            self.session_active = False
            self.session_btn.configure(text="Start Session", fg_color=["#3B8ED0", "#1F6AA5"])
            self.stop_camera()
            self.run_in_thread(lambda: self.api_client.stop_session())

    def update_present_count(self):
        self.present_label.configure(text=f"Present Students: {len(self.present_students)}")

    # ================================================================== #
    #  Camera (Attendance mode)                                            #
    # ================================================================== #

    def start_camera(self, label, mode="preview"):
        if self.cap is not None:
            self.stop_camera()

        if platform.system() == 'Windows':
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(0)
        self.is_camera_running = True

        # Reset liveness calibration when starting the camera
        if hasattr(self.face_service, 'liveness'):
            self.face_service.liveness.reset_calibration()

        def cam_loop():
            while self.is_camera_running:
                ret, frame = self.cap.read()
                if ret:
                    if mode == "attendance":
                        detected_ids, frame = self.face_service.recognize_face(frame)
                        for sid in detected_ids:
                            if sid not in self.present_students:
                                def do_mark(s_id=sid):
                                    if self.api_client.mark_attendance(
                                        s_id, self.selected_course['id'],
                                        self.selected_lecture['id'] if self.selected_lecture else None
                                    ):
                                        return s_id
                                    return None

                                def on_mark_done(s_id):
                                    if s_id:
                                        self.present_students.add(s_id)
                                        self.update_present_count()

                                self.run_in_thread(do_mark, on_mark_done)

                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(img)
                    img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
                    self.after(0, lambda i=img: self.update_cam_label(i))
                time.sleep(0.01)

        threading.Thread(target=cam_loop, daemon=True).start()

    def update_cam_label(self, img):
        if hasattr(self, 'cam_label') and self.cam_label.winfo_exists():
            self.cam_label.configure(image=img)
            self.cam_label.image = img

    def stop_camera(self):
        self.is_camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None


if __name__ == "__main__":
    app = App()
    app.mainloop()