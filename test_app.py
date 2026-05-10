import streamlit as st
import cv2
import time

if 'running' not in st.session_state:
    st.session_state.running = False

st.write('Camera Running:', st.session_state.running)

col1, col2 = st.columns(2)
with col1:
    if st.button('Start'):
        st.session_state.running = True
        st.rerun()
with col2:
    if st.button('Stop'):
        st.session_state.running = False
        st.rerun()

placeholder = st.empty()

if st.session_state.running:
    cap = cv2.VideoCapture(0)
    while st.session_state.running:
        ret, frame = cap.read()
        if not ret: break
        # Simulate processing
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        placeholder.image(frame)
        # Small sleep to yield some time (though not strictly necessary)
        time.sleep(0.03)
    cap.release()
