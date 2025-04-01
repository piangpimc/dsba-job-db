import streamlit as stimport pandas as pdfrom datetime import datetimefrom firebase_utils import (    init_firebase,    has_valid_submission,    is_manually_approved,    request_access,    save_submission,    get_all_submissions,)from st_aggrid import AgGrid, GridOptionsBuilderst.set_page_config(layout="wide")init_firebase()st.title("DSBA Interview Experience Database")email = st.text_input("Enter your email to continue")if email:    valid = has_valid_submission(email)    approved = is_manually_approved(email)    show_submission_form = False    if valid or approved:        st.success("You have access to the database.")        show_submission_form = st.checkbox("Submit another experience")    if not valid and not approved:        st.warning("You don’t currently have access to the database.")        choice = st.radio(            "Choose an option:",            [                "Submit a new interview experience",                "If you don't have a new contribution, request access from Pim directly.",            ],            key="access_choice"        )        if choice == "Submit a new interview experience":            show_submission_form = True    if show_submission_form:        st.subheader("Submit Your Interview Experience")        name = st.text_input("Your Name (optional)")        nationality = st.text_input("Your Nationality")        company = st.text_input("Company Name (Please note that Nestlé interview contributions will NOT be accepted.)")        role = st.text_input("Role / Position (Please specify if intern or CDI)")        method = st.selectbox("Method of Applying", ["LinkedIn/Company Website", "Referral/Networking", "Other"])        city = st.text_input("City (optional)")        language = st.text_input("Language of Interview (optional)")        num_rounds = st.number_input("How many rounds did you have? (Please note: CV screening does not count as a round.)", min_value=1, step=1)        rounds_data = []        for i in range(num_rounds):            st.markdown(f"Round {i+1}")            round_qs = st.text_area(f"Questions for Round {i+1}", key=f"round_qs_{i}")            rounds_data.append({                "questions": round_qs            })        tips = st.text_area("Any advice or preparation tips? (optional)")        result = st.selectbox("Result (optional)", ["", "Accepted", "Rejected", "Pending", "No Response"])        if st.button("Submit", key="submit_button"):            if not (nationality and company and role and method and any(r["questions"] for r in rounds_data)):                st.error("Please fill in all required fields and include at least one round with questions.")            else:                data = {                    "email": email,                    "name": name or "N/A",                    "nationality": nationality,                    "company": company,                    "role": role,                    "method": method,                    "city": city or "N/A",                    "language": language or "N/A",                    "tips": tips or "N/A",                    "result": result or "N/A",                    "rounds": rounds_data,                    "submitted_at": datetime.utcnow().isoformat()                }                save_submission(email, data)                st.success("Thank you for your submission! You now have access to the database.")                st.rerun()    if valid or approved:        st.subheader("Browse Submitted Interviews")        submissions = get_all_submissions()        if submissions:            cleaned_entries = []            for entry in submissions:                if not isinstance(entry, dict):                    continue                raw_rounds = entry.get("rounds", [])                if not isinstance(raw_rounds, list):                    raw_rounds = []                formatted_rounds = "\n\n".join(                    f"Round {i+1}: {round_data.get('round', 'N/A')}\n{round_data.get('questions')}"                    for i, round_data in enumerate(raw_rounds)                    if isinstance(round_data, dict)                ) or "N/A"                cleaned_entries.append({                    "name": entry.get("name", "N/A"),                    "nationality": entry.get("nationality", "N/A"),                    "company": entry.get("company", "N/A"),                    "role": entry.get("role", "N/A"),                    "method": entry.get("method", "N/A"),                    "city": entry.get("city", "N/A"),                    "language": entry.get("language", "N/A"),                    "rounds": formatted_rounds,                    "tips": entry.get("tips", "N/A"),                    "result": entry.get("result", "N/A"),                })            df = pd.DataFrame(cleaned_entries)            gb = GridOptionsBuilder.from_dataframe(df)            gb.configure_default_column(                wrapText=True,                autoHeight=True,                cellStyle={'whiteSpace': 'normal', 'wordWrap': 'break-word'}            )            gb.configure_grid_options(domLayout='autoHeight')            grid_options = gb.build()            AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True)        else:            st.info("No submissions yet.")