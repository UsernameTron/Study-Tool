# Study App

A web-based application for studying and quiz testing on anatomical systems.

## Features

- Study modules for Lymphatic, Respiratory, and Digestive systems
- Interactive quiz with immediate feedback
- Clean, responsive interface

## Deployment to Streamlit Cloud

The application has been configured for deployment to Streamlit Cloud, a free web-based hosting platform that will make your study app accessible to anyone with the URL.

### How to Deploy to Streamlit Cloud

1. Push your code to GitHub:
   - Create a repository on GitHub
   - Push your local code to the repository using:
   ```
   git remote add origin https://github.com/YOUR_USERNAME/study-app.git
   git push -u origin master
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub:
   - Click "New app"
   - Select your repository
   - Set the main file path to: `streamlit_app.py`
   - Click "Deploy"

3. Your app will be deployed to a URL like: `https://YOUR_USERNAME-study-app-streamlit-app-xxxx.streamlit.app`

## Local Development

If you need to make changes before deploying:

1. Activate the virtual environment:
   ```
   source env/bin/activate
   ```

2. Run the Streamlit app locally:
   ```
   streamlit run streamlit_app.py
   ```

## File Structure

- `streamlit_app.py`: Main application for Streamlit deployment
- `app.py`: Original Flask version of the application
- `data/knowledge/`: HTML content for study materials
- `data/quizzes.json`: Quiz questions and answers
