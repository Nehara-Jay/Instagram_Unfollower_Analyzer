import streamlit as st
import pandas as pd
import json

# page config
st.set_page_config(page_title="Instagram Unfollower Analyzer", page_icon="🕵️", layout="centered")

st.title("Instagram Unfollower Analyzer")
st.markdown("Find out who doesn't follow you back")

# layout: side by side drag and drop
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Followers")
    followers_file = st.file_uploader(
        "Drop followers.json here",
        type=["json"],
        key="followers"
    )

with col2:
    st.subheader("2. Following")
    following_file = st.file_uploader(
        "Drop following.json here",
        type=["json"],
        key="following"
    )

# processing Logic
if followers_file is not None and following_file is not None:
    try:
        # load json directly from the uploaded file bytes
        followers_data = json.load(followers_file)
        following_data = json.load(following_file)

        # --- DEBUGGING LINES ---
        st.info(f"Raw follower records in file: {len(followers_data)}")
        if isinstance(following_data, dict) and 'relationships_following' in following_data:
            st.info(f"Raw following records in file: {len(following_data['relationships_following'])}")
        elif isinstance(following_data, list):
             st.info(f"Raw following records in file: {len(following_data)}")

        # EXTRACT SETS SAFELY
        # We add conditional 'if' statements to skip deactivated accounts missing the 'value' key
        followers = {
            user['string_list_data'][0]['value'] 
            for user in followers_data 
            if 'string_list_data' in user and len(user['string_list_data']) > 0 and 'value' in user['string_list_data'][0]
        }
        
        # We also use .get() here to prevent a crash if the user uploads the wrong file by mistake
        following = {
            user['string_list_data'][0]['value'] 
            for user in following_data.get('relationships_following', [])
            if 'string_list_data' in user and len(user['string_list_data']) > 0 and 'value' in user['string_list_data'][0]
        }

        # calculate difference
        unfollowers = sorted(list(following - followers))
        mutuals = following.intersection(followers)
        fans = followers - following

        st.divider()
        st.header("Results")

        # metrics dashboard
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Non-Followers", len(unfollowers))
        metric2.metric("Mutuals", len(mutuals))
        metric3.metric("People who follow you", len(fans))

        st.subheader("people who don't follow you back:")

        if unfollowers:
            # display as a table
            df = pd.DataFrame(unfollowers, columns=["Username"])

            # make usernames clickable links to instagram profiles
            df['Profile Link'] = df['Username'].apply(lambda x: f"https://instagram.com/{x}")

            st.dataframe(
                df,
                column_config={
                    # BUG FIX: Changed 'LinkColumns' to 'LinkColumn'
                    "Profile Link": st.column_config.LinkColumn("View Profile") 
                },
                use_container_width=True,
                hide_index=True
            )
    
            # allow users to download final list of csv
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Unfollowers list as csv",
                data=csv,
                file_name='unfollowers.csv',
                mime='text/csv',
            )

        else:
            st.success("Everyone you follow follows you back!")

    except Exception as e:
        st.error(f"Error processing files. Make sure you uploaded the correct JSON files. Error detail: {e}")