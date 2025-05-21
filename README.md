<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <div class="container">
    <h1>HealthIntuit: - An AI-powered healthcare assistant</h1>
  </br>
    <image src= "HI2.jpg" alt= "HealthIntuit Demo"></image>
    <h2>Project Overview</h2>
    <p>
      HealthIntuit is a multimodal AI-powered web app that analyzes patient-submitted images and voice queries to generate preliminary medical insights and prescription drafts. Designed for educational purposes, it leverages Groq's ultra-fast LLMs and ElevenLabs' lifelike speech synthesis to simulate doctor-patient interactions while emphasizing the importance of professional consultation. The app streamlines triage workflows, reduces administrative burdens, and empowers patients with accessible preliminary guidance.
    </p>
    <h3>Mission</h3>
    <p>Leverage multimodal AI to streamline preliminary patient triage and prescription drafting, supporting medical education and workflow efficiency without replacing licensed healthcare providers.</p>
      <ul>
          <li><b>Medical Education</b>: Students can simulate doctor-patient interactions for training.</li>
         <li><b>Workflow Automation</b>: Generates draft prescriptions for review (saves ~15 mins/case).</li> 
      </ul>
    <h3>Tech Stack</h3>
    <table>
      <tr><th>Category</th><th>Technologies Used</th></tr>
      <tr><td>AI/ML</td><td>Groq API (Llama-4-Scout-17B, Whisper-Large-v3), ElevenLabs TTS</td></tr>
      <tr><td>Frontend</td><td>Gradio (Python-based UI), Custom CSS Styling</td></tr>
      <tr><td>Backend</td><td>Python 3.10</td></tr>
      <tr><td>Audio/Image</td><td>PyDub, SpeechRecognition, Base64 Encoding</td></tr>
      <tr><td>Security</td><td>Environment Variables, Input Validation</td></tr>
    </table>
      </br>
    <h2>Problem Statement</h2>
    <ul>
      <li><b>Healthcare Access Crisis (Canada Focus):</b> <br>
        <ul>
          <li>4.8 million Canadians lack a family doctor (2025 Statistics Canada), with average wait times of 25.6 weeks for specialist referrals.</li>
          <li>Rural disparities: 23% of rural patients travel &gt;100 km for basic care, exacerbating health inequities.</li>
        </ul>
      </li>
      <li><b>Pain Points Addressed:</b>
        <ul>
          <li>Long Wait Times: Patients face delays in receiving initial feedback for non-emergency conditions (e.g., skin irritations).</li>
          <li>Prescription Errors: 12% of manual prescriptions contain dosage inaccuracies (Canadian Medical Association, 2024).</li>
          <li>Workflow Inefficiencies: Doctors spend 37% of their time on administrative tasks instead of patient care.</li>
        </ul>
      </li>
      <li><b>Impact:</b>
        <ul>
          <li>Misdiagnosis costs Canada’s healthcare system $1.2B annually in preventable complications.</li>
          <li>68% of patients report frustration with "black box" medical jargon in preliminary diagnoses.</li>
        </ul>
      </li>
    </ul>
      </br>
    <h2>System Architecture</h2>
    <h3>High-Level UML Diagram (Text Representation)</h3>
    <pre>
[User Interface (Gradio)]
       ↑ ↓
[Backend Logic (Python)]
       ↑ ↓
[Groq AI Model (Llama-4-Scout-17B, Whisper-Large-v3)]
       ↑
[Prescription Formatter (AI-powered)]
       ↑
[ElevenLabs/gTTS TTS]
    </pre>
      <image src= "WorkflowDiagram.png" alt= "Workflow Diagram"></image>
    <h3>Key Components</h3>
    <ul>
      <li><b>Frontend Operations:</b>
        <ul>
          <li>Responsive, accessible UI using Gradio.</li>
          <li>Secure image (medical photo) and audio (voice) upload.</li>
          <li>Real-time feedback: Progress indicators and error messages for invalid or missing inputs.</li>
        </ul>
      </li>
      <li><b>Backend Operations:</b>
        <ul>
          <li>All logic handled within a Python backend (Gradio app).</li>
          <li>Handles file processing, AI inference, and output formatting.</li>
          <li>Uses environment variables for secure API key management.</li>
        </ul>
      </li>
      <li><b>AI Integrations:</b>
        <ul>
          <li>Groq LLM: For multimodal (image + text) medical analysis.</li>
          <li>Whisper (Groq): For speech-to-text transcription of patient queries.</li>
          <li>ElevenLabs/gTTS: For converting doctor’s AI response to natural-sounding speech.</li>
        </ul>
      </li>
      <li><b>Prescription Generator:</b>
        <ul>
          <li>AI-driven prescription formatter: Converts doctor’s analysis into a structured, downloadable text prescription.</li>
          <li>Downloadable as a .txt file.</li>
        </ul>
      </li>
      <li><b>Multi-modal Input:</b>
        <ul>
          <li>Accepts both voice (audio) and medical image uploads for comprehensive analysis.</li>
        </ul>
      </li>
      <li><b>Dynamic Prescription Templating:</b>
        <ul>
          <li>Uses Groq AI to generate a clear, structured prescription based on the doctor’s response.</li>
        </ul>
      </li>
    </ul>
    <div class="sample"><br>
      <b>Sample Prescription Output:</b><br><br>
      Patient Name: John Doe<br>
      Date: 2025-05-20 14:30:00<br><br>
      Diagnosis: Mild seborrheic dermatitis<br><br>
      Prescription:<br>
      - Ketoconazole 2% shampoo: Apply 10ml to scalp daily<br><br>
      Recommendations:<br>
      - Avoid harsh hair products<br>
      - Follow up in 2 weeks<br><br>
      Diagonosed by ⚕️HealthIntuit<br><br>
      Disclamer: AI Medical Assistant (Educational Use Only)<br><br>
    </div>
    <h2>Technical Highlights</h2>
    <ul>
      <li><b>Code Quality & Principles:</b>
        <ul>
          <li>Partial adherence to SOLID (modular functions, easy to extend AI models).</li>
          <li>Clean, PEP8-compliant code; documented functions.</li>
          <li>Test coverage not yet implemented (future: pytest, target 90%+).</li>
        </ul>
      </li>
      <li><b>Security:</b>
        <ul>
          <li>API keys managed via environment variables.</li>
          <li>Basic input validation and temporary file cleanup.</li>
        </ul>
      </li>
      <li><b>Scalability:</b>
        <ul>
          <li>Single-instance Gradio app (suitable for small user base).</li>
          <li>Groq AI APIs handle inference scaling.</li>
        </ul>
      </li>
      <li><b>Observability:</b>
        <ul>
          <li>Basic logging for audio recording and error handling.</li>
          <li>Future: centralized logging, monitoring, and error tracking.</li>
        </ul>
      </li>
    </ul>
      </br>
    <h2>Product Features</h2>
    <ul>
      <li><b>Multi-modal Input:</b>
        <ul>
          <li>Accepts both patient queries (voice) and medical images (photo upload).</li>
        </ul>
      </li>
      <li><b>Educational Disclaimers:</b>
        <ul>
          <li>Prominently displayed in all outputs and prescription downloads.</li>
          <li>Logic prevents use without user acknowledgment of educational purpose.</li>
        </ul>
      </li>
    </ul>
      </br>
    <h2>Business & Product Vision</h2>
    <ul>
      <li><b>Market Fit:</b>
        <ul>
          <li>Addresses needs in medical education, telehealth, and workflow automation.</li>
        </ul>
      </li>
      <li><b>Monetization:</b>
        <ul>
          <li>SaaS for institutions, API for EMR vendors, open-source core for community adoption.</li>
        </ul>
      </li>
      <li><b>Growth:</b>
        <ul>
          <li>Roadmap includes multilingual support, integration with Canadian EMRs, and expansion to global markets.</li>
        </ul>
      </li>
    </ul>
    <div class="footer">
      <hr>
      For educational use only. Consult a licensed healthcare provider for medical advice.<br>
    </div>
  </div>
</body>
</html>

[![Watch the video](/demo.png)](https://youtu.be/2KuzilloYgc)
