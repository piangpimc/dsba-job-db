import firebase_adminfrom firebase_admin import credentials, dbfrom datetime import datetime, timedeltaimport streamlit as stimport jsondef init_firebase():    if not firebase_admin._apps:        firebase_creds = json.loads(st.secrets["FIREBASE"])        cred = credentials.Certificate(firebase_creds)        firebase_admin.initialize_app(cred, {            'databaseURL': 'https://dsba-interviews-default-rtdb.europe-west1.firebasedatabase.app/'        })def save_submission(email, data):    ref = db.reference("submissions")    user_ref = ref.child(email.replace(".", "_"))    user_ref.push(data)  # create a unique submission under userdef has_valid_submission(email):    ref = db.reference("submissions")    submissions = ref.child(email.replace(".", "_")).get()    if submissions:        for entry in submissions.values():            if isinstance(entry, dict) and "submitted_at" in entry:                try:                    submitted_time = datetime.fromisoformat(entry["submitted_at"])                    if datetime.utcnow() - submitted_time < timedelta(days=7):                        return True                except Exception:                    continue    return Falsedef get_all_submissions():    ref = db.reference("submissions")    all_data = ref.get()    all_submissions = []    if all_data:        for user_entries in all_data.values():            if isinstance(user_entries, dict):                for submission in user_entries.values():                    if isinstance(submission, dict):                        all_submissions.append(submission)    return all_submissionsdef is_manually_approved(email):    ref = db.reference("manual_access")    return ref.child(email.replace(".", "_")).get() == Truedef request_access(email):    ref = db.reference("access_requests")    ref.child(email.replace(".", "_")).set({        "email": email,        "requested_at": datetime.utcnow().isoformat()    })