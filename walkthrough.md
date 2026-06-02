# Walkthrough - Student Biometric Attendance & Physical Gate Device API

I have successfully updated the implementation! Rather than being restricted to a web-only trigger, Sagarmatha ERP now exposes a robust, **production-ready REST API endpoint** specifically designed for the **physical biometric devices mounted at the college gates**. 

Additionally, the interactive device simulator is wired to hit this exact public API, enabling you to test the physical gate integration logic directly from the UI.

---

## 🛠️ Public Biometric Gate API Specifications

The physical biometric devices at the entry and exit gates can communicate with the live 24-hour Sagarmatha ERP web server via the following endpoint:

### `POST /api/biometric/punch/`

This public endpoint is **CSRF-exempt** and has **public permissions (`AllowAny`)**, meaning gate devices can directly make REST calls without needing session cookies.

#### Request Parameters (JSON or FormData):
* `user_type` (string, required): Either `'staff'` or `'student'`
* `identifier` (string/integer, required): The unique identifier for the individual. This can be:
  1. The Django database User ID (e.g. `24` or `record.code`)
  2. The individual's official College email address (e.g. `john.doe@sagarmatha.edu`)
  3. The internal Profile ID

#### Automatic "Login" and "Logout" Behavior:
1. **First press of the day (Entry Gate - "Login")**: The system automatically registers the current server timestamp as `in_time`.
2. **Subsequent presses of the day (Exit Gate - "Logout")**: The system automatically registers the current server timestamp as `out_time`.
3. **Real-time Status Calculation**: Upon receiving a punch, the server immediately calculates worked hours, late minutes, and attendance status (`PRESENT`, `LATE`, `EARLY_OUT`, etc.) and instantly creates or updates the daily sheet records (`EmployeeAttendance` or `StudentAttendance`).

#### Sample Success Response:
```json
{
    "status": "success",
    "punch_type": "IN",
    "name": "Jungey Sircar",
    "role": "Student (Computer Engineering)",
    "time": "09:05:22 AM",
    "in_time": "09:05 AM",
    "out_time": "--",
    "worked_hours": "--",
    "daily_status": "LATE"
}
```

---

## 🚀 How to Access & Verify

### Step 1: Start the Server
Start the development server using:
```bash
python manage.py runserver
```

### Step 2: Test the Physical Device API (using the Simulator)
1. Open the terminal simulator in your browser:
   [http://127.0.0.1:8000/modules/attendance/device/](http://127.0.0.1:8000/modules/attendance/device/)
2. Toggle between **Staff Member** and **Student** types.
3. Select an individual from the search select dropdown.
4. Click the circular **Fingerprint Scanner**.
5. The simulator page will make a `POST` request directly to `/api/biometric/punch/` (the exact endpoint physical gate devices hit!).
6. The server registers the punch in real-time. You'll hear the scan chime and a synthesized Text-to-Speech voice announcing the status:
   > *"Access Granted. Welcome Jungey Sircar. Punch IN recorded at 9:05 AM."*
7. Click the scanner a second time to test recording a **Punch OUT**!

### Step 3: Verify the Daily Logs Sheet
1. Open the main Attendance dashboard:
   [http://127.0.0.1:8000/modules/attendance/](http://127.0.0.1:8000/modules/attendance/)
2. Select the **Student Daily Sheet** or **Staff Daily Sheet** tab.
3. You will immediately see the logged entry with its exact InTime, OutTime, Worked Hours, and Status computed in real time by the gate API!
