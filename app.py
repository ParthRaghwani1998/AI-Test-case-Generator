import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from dotenv import load_dotenv
from io import BytesIO
from openpyxl.styles import Alignment
from datetime import datetime

load_dotenv()

# Google Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize session state for history
if "test_case_history" not in st.session_state:
    st.session_state.test_case_history = []

# Page configuration
st.set_page_config(
    page_title="AI Test Case Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
    }
    .main-header p {
        margin: 5px 0 0 0;
        font-size: 1.1em;
        opacity: 0.9;
    }
    .card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("C:\\Users\\Kritika Khandelwal\\Downloads\\raapyd_logo.svg", width=150)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Generate Test Cases", "📚 History", "ℹ️ About"],
        key="page_nav"
    )
    
    st.markdown("---")
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Generated", len(st.session_state.test_case_history))
    with col2:
        total_cases = sum([len(item.get("cases", [])) for item in st.session_state.test_case_history])
        st.metric("Test Cases", total_cases)

# Main header
st.markdown("""
    <div class="main-header">
        <h1>📋 AI Test Case Generator</h1>
        <p>Generate Professional Test Cases Powered by Google Gemini</p>
    </div>
""", unsafe_allow_html=True)

if page == "🏠 Generate Test Cases":
    st.markdown("### Create Test Cases from Your Requirements")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        story = st.text_area(
            "📝 Paste Your Jira User Story or Requirements",
            height=250,
            placeholder="Paste your user story, feature description, or requirements here..."
        )
    
    with col2:
        st.markdown("**✨ Tips:**")
        st.info("""
        • Be specific about features
        • Include acceptance criteria
        • Mention edge cases
        • Add any constraints
        """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        generate_btn = st.button("🚀 Generate Test Cases", use_container_width=True, type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    with col3:
        pass
    
    if clear_btn:
        st.session_state.story_input = ""
        st.rerun()
    
    if generate_btn and story.strip():
        with st.spinner("✨ Generating test cases... Please wait"):
            prompt = f"""You are a Senior QA Engineer with 15+ years of enterprise software testing experience,
specializing in test strategy, risk-based testing, and ISTQB-aligned methodologies.
 
## TASK
Analyze the Jira story below and generate a comprehensive, professional test suite.
 
## JIRA STORY
{story}
 
## TEST CASE REQUIREMENTS
For EACH test case, include ALL of the following fields:
- test_case_id     : Unique ID in format TC-XXX (e.g., TC-001)
- title            : Clear, action-oriented title (max 80 chars)
- category         : One of: Positive | Negative | Boundary | Validation | UI | Integration
- priority         : Critical | High | Medium | Low  (based on risk & business impact)
- preconditions    : Numbered list of setup conditions (at least 1)
- test_steps       : Numbered, atomic steps (action + data if applicable)
- expected_result  : Specific, measurable outcome; include status codes/messages where relevant
- test_data        : Concrete sample data or "N/A"
- severity         : Blocker | Critical | Major | Minor | Trivial
- automation_flag  : "Yes" or "No" (is this a good candidate for automation?)
- notes            : Edge cases, dependencies, or assumptions (or "None")
 
## COVERAGE MANDATE — generate at least 2 cases per category:
1. **Positive**      – Happy path; valid inputs; expected success flows
2. **Negative**      – Invalid inputs; error handling; unauthorised access
3. **Boundary**      – Min/max values, empty inputs, data limits, off-by-one
4. **Validation**    – Field-level rules, format checks, required fields, regex patterns
5. **UI Validation** – Layout, labels, responsiveness, accessibility (WCAG 2.1 AA), error messages
6. **Integration**   – API contracts, third-party dependencies, DB interactions, event flows
 
## QUALITY STANDARDS
- Follow IEEE 829 / ISO 29119 test documentation standards
- Steps must be reproducible by any engineer without prior context
- Expected results must be verifiable (no vague language like "works correctly")
- Priority and severity must reflect business impact and technical risk
- Flag regression candidates and automation-suitable cases
 
## OUTPUT FORMAT
Return ONLY valid JSON — no markdown fences, no extra text.
Schema:
{{
  "story_summary": "<one-sentence summary of the Jira story>",
  "test_cases": [
    {{
      "test_case_id": "TC-001",
      "title": "...",
      "category": "...",
      "priority": "...",
      "preconditions": ["...", "..."],
      "test_steps": ["1. ...", "2. ..."],
      "expected_result": "...",
      "test_data": "...",
      "severity": "...",
      "automation_flag": "Yes",
      "notes": "..."
    }}
  ]
}}"""

            response = model.generate_content(prompt)
            result = response.text

            st.subheader("📋 Generated Test Cases (JSON)")
            
            if not result or result.strip() == "":
                st.error("❌ Empty response from API. Please try again.")
            else:
                st.code(result, language="json")

                try:
                    cleaned_result = result
                    if result.startswith("```"):
                        cleaned_result = result.split("```")[1]
                        if cleaned_result.startswith("json"):
                            cleaned_result = cleaned_result[4:]
                        cleaned_result = cleaned_result.strip()
                    
                    data = json.loads(cleaned_result)

                    if "test_cases" in data and len(data["test_cases"]) > 0:
                        st.subheader("📊 Test Cases Table")
                        
                        df = pd.DataFrame(data["test_cases"])
                        
                        # Format list columns for better Excel readability
                        list_columns = ["preconditions", "test_steps"]
                        
                        for col in list_columns:
                            if col in df.columns:
                                df[col] = df[col].apply(lambda x: "\n".join([f"{i}. {step}" if isinstance(step, str) else f"{i}. {str(step)}" for i, step in enumerate(x, 1)]) if isinstance(x, list) else str(x))

                        st.dataframe(df, use_container_width=True)

                        # Export to Excel using BytesIO
                        output = BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name="Test Cases", index=False)
                            
                            # Adjust column widths for better readability
                            worksheet = writer.sheets["Test Cases"]
                            for column in worksheet.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    try:
                                        if len(str(cell.value)) > max_length:
                                            max_length = len(str(cell.value))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                worksheet.column_dimensions[column_letter].width = adjusted_width
                                
                                # Enable text wrapping for better display
                                for cell in column:
                                    cell.alignment = Alignment(wrap_text=True, vertical='top')
                        
                        excel_data = output.getvalue()

                        # Download button
                        st.download_button(
                            label="📥 Download Excel File",
                            data=excel_data,
                            file_name="test_cases.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        # Save to history
                        history_item = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "summary": data.get("story_summary", story[:50]),
                            "cases": data.get("test_cases", []),
                            "full_story": story
                        }
                        st.session_state.test_case_history.insert(0, history_item)
                        
                        st.markdown("""
                            <div class="success-box">
                                <strong>✅ Success!</strong> Generated """ + str(len(data['test_cases'])) + """ test cases successfully!
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No test cases found in the response.")
                        st.write("Response structure:")
                        st.json(data)

                except json.JSONDecodeError as e:
                    st.error(f"❌ Failed to parse JSON: {str(e)}")
                    st.write("**Raw Response (first 1000 chars):**")
                    st.text(result[:1000])
                except Exception as e:
                    st.error(f"❌ Error processing test cases: {str(e)}")

    elif generate_btn:
        st.warning("⚠️ Please paste a user story before generating test cases.")

elif page == "📚 History":
    st.markdown("### 📚 Test Case Generation History")
    
    if len(st.session_state.test_case_history) == 0:
        st.info("ℹ️ No test cases generated yet. Go to the main page to create some!")
    else:
        for idx, item in enumerate(st.session_state.test_case_history):
            with st.expander(f"📝 {item['summary']} - {item['timestamp']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Generated:** {item['timestamp']}")
                    st.write(f"**Test Cases:** {len(item['cases'])}")
                
                with col2:
                    if st.button("👁️ View", key=f"view_{idx}"):
                        st.write(item['full_story'])
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.session_state.test_case_history.pop(idx)
                        st.rerun()
                
                # Show test cases for this history item
                df_history = pd.DataFrame(item['cases'])
                st.dataframe(df_history, use_container_width=True)

elif page == "ℹ️ About":
    st.markdown("""
    ## 📋 About AI Test Case Generator
    
    ### Features
    - 🤖 **AI-Powered**: Uses Google Gemini to generate professional test cases
    - 📊 **Enterprise Standards**: Follows IEEE 829 and ISO 29119 standards
    - 📥 **Excel Export**: Download test cases in formatted Excel files
    - 📚 **History Tracking**: Keep track of all generated test cases
    - 🎨 **Modern UI**: Industry-standard, professional interface
    
    ### Test Case Coverage
    The generator creates test cases across 6 categories:
    - ✅ **Positive** - Happy path scenarios
    - ❌ **Negative** - Error handling and edge cases
    - 📏 **Boundary** - Min/max and limit testing
    - ✔️ **Validation** - Field and data validation
    - 🖥️ **UI Validation** - User interface testing
    - 🔗 **Integration** - System integration testing
    
    ### How to Use
    1. Paste your Jira user story or requirements
    2. Click "Generate Test Cases"
    3. Review the generated test cases
    4. Download as Excel for your team
    5. Check history to revisit previous generations
    
    ### Built With
    - 🐍 Python & Streamlit
    - 🤖 Google Gemini AI
    - 📊 Pandas & OpenPyXL
    
    ---
    **Version 1.0** | Made by Raapyd QA Team
    """)
