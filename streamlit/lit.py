# import module
import streamlit as st

# https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav Multi page app
# https://discuss.streamlit.io/t/rename-the-home-page-in-a-multi-page-app/65533/3
st.set_page_config(
    page_title="Heavy Lifter",
    page_icon=":sunglasses:",
)

st.title("Heavy Lifter :sunglasses:")

# builds the sidebar menu
with st.sidebar:
    st.page_link('lit.py', label='Home', icon='🔥')
    st.page_link('pages/dashboard_demo.py', label='Heavy Lifter', icon='🛡️')
    st.page_link('pages/graphql_demo.py', label='GraphQLifter', icon='🛡️')

st.markdown(
        """
        TODO Kapil: Update text from slides!
        
        Heavy Lifter is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        **👈 Select a demo from the sidebar on the left** to see some examples
        of what Heavy Lifter can do!

        ### Want to learn more?

        - Check out [streamlit.io](https://streamlit.io)
        - Jump into our [documentation](https://docs.streamlit.io)
        - Ask a question in our [community
          forums](https://discuss.streamlit.io)

        ### See more complex demos

        - Use a neural net to [analyze the Udacity Self-driving Car Image
          Dataset](https://github.com/streamlit/demo-self-driving)
        - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    """
    )