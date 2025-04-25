import streamlit as st
from few_shot import FewShotPosts
from test2 import generate_posts

length_options = ["Short", "Medium", "Long"]
tone_options = ["Professional", "Conversational", "Humorous"]

def main():
    st.markdown(
        """
        <style>
            .fixed-top {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background-color: white;
                padding: 10px 0;
                z-index: 1000;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
            .stSelectbox, .stCheckbox { margin-top: 10px; }
            .post-container {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #f6f8fa;
            }
            .modify-btn {
                margin-top: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None

    # Create a fixed container for controls
    with st.container():
        st.markdown('<div class="fixed-top">', unsafe_allow_html=True)
        
        st.title("LinkedIn Post Generator")
        col1, col2, col3, col4 = st.columns(4)

        fs = FewShotPosts()
        tags = fs.get_tags()
        
        with col1:
            selected_tag = st.selectbox("Topic", options=tags)
        
        with col2:
            selected_length = st.selectbox("Length", options=length_options)
        
        with col3:
            selected_tone = st.selectbox("Tone", options=tone_options)
        
        with col4:
            news = st.checkbox("Latest news on the topic")
            research = st.checkbox("Refer related research papers")

        st.markdown('</div>', unsafe_allow_html=True)

    # Display history of posts with modify buttons
    st.markdown("## Post History")
    for idx, message in enumerate(st.session_state.messages):
        if message['role'] == 'assistant':
            with st.container():
                st.markdown(f'<div class="post-container">', unsafe_allow_html=True)
                st.markdown(f"**Post #{idx + 1}**")
                st.markdown(message['content'])
                
                # Add modify button for each post
                if st.button(f"Modify Post #{idx + 1}", key=f"modify_{idx}"):
                    st.session_state.editing_index = idx
                    # st.experimental_user()
                
                st.markdown('</div>', unsafe_allow_html=True)

    # Input for new prompt or modification
    prompt = st.chat_input("Enter your prompt here or describe modifications")
    
    if prompt:
        if st.session_state.editing_index is not None:
            # We're modifying an existing post
            response = generate_posts(
                selected_tag, prompt, selected_length, selected_tone, 
                news, research, st.session_state.messages, 
                modify_index=st.session_state.editing_index
            )
            
            # Replace the existing post with the modified version
            st.session_state.messages[st.session_state.editing_index]['content'] = response
            st.session_state.editing_index = None
        else:
            # We're creating a new post
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({'role': 'user', 'content': prompt})
            
            response = generate_posts(
                selected_tag, prompt, selected_length, selected_tone, 
                news, research, st.session_state.messages
            )
            
            st.chat_message('assistant').markdown(response)
            st.session_state.messages.append({'role': 'assistant', 'content': response})
        
        # st.experimental_user()

if __name__ == "__main__":
    main()