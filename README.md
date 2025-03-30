# Anatomy Study App

An interactive cloud-based application for studying anatomical systems with advanced features for visual learning, interactive quizzes, and progress tracking.

## Enhanced Features

### Phase 1: Visual Content Integration
- **Study Content**: Comprehensive text-based anatomical system information
- **Histology Slides**: Visual reference for microscopic anatomy
- **Interactive Diagrams**: Clickable diagrams with highlighting for better understanding

### Phase 2: Enhanced Quiz System
- **Multiple Question Types**: 
  - Free response questions
  - Multiple choice questions
  - Image identification questions
  - Matching questions
- **Difficulty Levels**: Beginner, Intermediate, and Advanced options
- **System-specific Filtering**: Target quizzes to specific anatomical systems

### Phase 3: Progress Tracking
- **Personal Progress Dashboard**: Visual representation of mastery levels
- **Performance History**: Track quiz scores over time
- **Personalized Recommendations**: Get study suggestions based on performance

### Phase 4: UI and Deployment Enhancements
- **Dark/Light Mode**: Toggle between theme preferences
- **Responsive Design**: Works across different device sizes
- **Cloud Deployment**: Ready for Render and Streamlit Cloud deployment

## Cloud Deployment Options

### Option 1: Deploy to Render

The application has been configured for easy deployment to Render using the included `render.yaml` file.

1. Push your code to GitHub:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/anatomy-study-app.git
   git push -u origin main
   ```

2. Connect your repository to Render:
   - Go to [render.com](https://render.com) and sign up/sign in
   - Click "New" > "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file and set up your app

3. Your app will be deployed to a URL like: `https://anatomy-study-app.onrender.com`

### Option 2: Deploy to Streamlit Cloud

1. Push your code to GitHub as described above

2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub:
   - Click "New app"
   - Select your repository
   - Set the main file path to: `cloud_deploy_app_main.py`
   - Click "Deploy"

3. Your app will be deployed to a URL like: `https://username-anatomy-study-app-xxxx.streamlitapp.com`

## Project Structure

```
anatomy-study-app/
│
├── cloud_deploy_app.py            # Main application initialization
├── cloud_deploy_app_main.py       # Application entry point
├── cloud_deploy_app_quiz.py       # Quiz functionality
├── cloud_deploy_app_progress.py   # Progress tracking functionality
├── tabbed_interface.py            # Content display with tabs
├── interactive_diagrams.py        # Interactive anatomy diagrams
├── search_utils.py                # Content search utilities
├── simulations.py                 # Interactive experiments
├── user_progress.py               # User progress tracking
│
├── data/
│   ├── knowledge/                 # HTML content for study materials
│   │   ├── lymphatic.html
│   │   ├── respiratory.html
│   │   └── digestive.html
│   ├── quizzes.json               # Original quiz format
│   ├── enhanced_quizzes.json      # Enhanced quiz with multiple formats
│   └── user_progress/             # User progress data storage
│
├── static/
│   ├── css/
│   │   └── custom.css            # Custom styling
│   └── images/
│       ├── histology/             # Histology slide images
│       └── diagrams/              # Interactive diagram images
│
├── requirements.txt               # Python dependencies
└── render.yaml                    # Render deployment configuration
```

## Technologies Used

- **Streamlit**: Core web application framework
- **Pandas & NumPy**: Data processing and analysis
- **Altair & Matplotlib**: Data visualization
- **PIL**: Image processing for placeholders and diagrams
- **NLTK**: Text processing for search functionality

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/anatomy-study-app.git
   cd anatomy-study-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run cloud_deploy_app_main.py
   ```

## Future Enhancements

- Integration with additional anatomical systems
- 3D anatomy visualizations
- User authentication for personalized experiences
- Social features for collaborative learning
- Mobile app version for offline study
