import streamlit as stimport pandas as pdfrom datetime import datetimefrom firebase_utils import (    init_firebase,    has_valid_submission,    is_manually_approved,    request_access,    save_submission,    get_all_submissions,)st.set_page_config(layout="wide")init_firebase()st.title("DSBA Interview Experience Database")email = st.text_input("Enter your email to continue")if email:    valid = has_valid_submission(email)    approved = is_manually_approved(email)    show_submission_form = False    if valid or approved:        st.success("You have access to the database.")        show_submission_form = st.checkbox("Submit another experience")    if not valid and not approved:        st.warning("You don’t currently have access to the database.")        choice = st.radio(            "Choose an option:",            [                "Submit a new interview experience",                "If you don't have a new contribution, request access from Pim directly through WhatsApp",            ],            key="access_choice"        )        if choice == "Submit a new interview experience":            show_submission_form = True    if show_submission_form:        st.subheader("Submit Your Interview Experience")        name = st.text_input("Your Name (optional)")        nationality = st.text_input("Your Nationality")        company = st.text_input("Company Name")        role = st.text_input("Role / Position")        method = st.selectbox("Method of Applying", ["LinkedIn/Company Website", "Referral/Networking", "Other"])        city = st.text_input("City (optional)")        language = st.text_input("Language of Interview (optional)")        num_stages = st.number_input("How many stages did you have?", min_value=1, step=1)        stages_data = []        for i in range(num_stages):            st.markdown(f"Stage {i+1}")            stage_name = st.text_input(f"Stage Name {i+1}", key=f"stage_name_{i}")            stage_qs = st.text_area(f"Questions for Stage {i+1}", key=f"stage_qs_{i}")            stages_data.append({                "stage": stage_name,                "questions": stage_qs            })        tips = st.text_area("Any advice or preparation tips? (optional)")        result = st.selectbox("Result (optional)", ["", "Accepted", "Rejected", "Pending", "No Response"])        if st.button("Submit", key="submit_button"):            if not (nationality and company and role and method and any(s["questions"] for s in stages_data)):                st.error("Please fill in all required fields and include at least one stage with questions.")            else:                data = {                    "email": email,                    "name": name or "N/A",                    "nationality": nationality,                    "company": company,                    "role": role,                    "method": method,                    "city": city or "N/A",                    "language": language or "N/A",                    "tips": tips or "N/A",                    "result": result or "N/A",                    "stages": stages_data,                    "submitted_at": datetime.utcnow().isoformat()                }                save_submission(email, data)                st.success("Thank you for your submission! You now have access to the database.")                st.rerun()    if valid or approved:        st.subheader("Browse Submitted Interviews")        submissions = get_all_submissions()        if submissions:            cleaned_entries = []            for entry in submissions:                if not isinstance(entry, dict):                    continue                raw_stages = entry.get("stages", [])                if not isinstance(raw_stages, list):                    raw_stages = []                formatted_stages = "\n\n".join(                    f"Stage {i+1}: {s.get('stage', 'N/A')}\n{s.get('questions', 'N/A')}"                    for i, s in enumerate(raw_stages)                    if isinstance(s, dict)                ) or "N/A"                cleaned_entries.append({                    "name": entry.get("name", "N/A"),                    "nationality": entry.get("nationality", "N/A"),                    "company": entry.get("company", "N/A"),                    "role": entry.get("role", "N/A"),                    "method": entry.get("method", "N/A"),                    "city": entry.get("city", "N/A"),                    "language": entry.get("language", "N/A"),                    "stages": formatted_stages,                    "tips": entry.get("tips", "N/A"),                    "result": entry.get("result", "N/A"),                })            df = pd.DataFrame(cleaned_entries)            st.dataframe(                df,                use_container_width=True,                column_config={                    "stages": st.column_config.TextColumn("Stages", width="medium"),                    "tips": st.column_config.TextColumn("Tips", width="medium"),                    "result": st.column_config.TextColumn("Result"),                }            )        else:            st.info("No submissions yet.")