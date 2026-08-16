from flask import Flask, jsonify, request, render_template_string, redirect
import datetime
import subprocess
import os
import json

app = Flask(__name__)

# Store tasks in memory
tasks = [
    {"id": 1, "title": "Learn CI/CD", "completed": False},
    {"id": 2, "title": "Implement GitHub Actions", "completed": False},
]

# Store deployment history
deployment_history = []

# Default values
user_inputs = {
    "deployment_engineer": "Zeeshan DevOps Engineer",
    "deployment_name": "",
    "commit_message": "",
    "important_notice": "Use commit message format deploy: Your Special Name",
    "message_of_the_day": "Keep coding and deploying! 🚀"
}

def get_commit_info():
    """Get the latest commit message, count, and SHA"""
    try:
        count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD']).decode().strip()
        message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
        sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        return count, message, sha
    except:
        return "0", "No commits yet", "N/A"

def get_deployment_count():
    """Get deployment count from file"""
    try:
        with open('/tmp/deploy_count.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def increment_deployment_count():
    """Increment deployment counter"""
    count = get_deployment_count()
    new_count = count + 1
    with open('/tmp/deploy_count.txt', 'w') as f:
        f.write(str(new_count))
    return new_count

def get_github_run_number():
    """Get GitHub Actions run number from environment"""
    run_number = os.environ.get('GITHUB_RUN_NUMBER', '')
    if run_number:
        return f"#{run_number}"
    try:
        with open('/tmp/github_run.txt', 'r') as f:
            return f.read().strip()
    except:
        return "N/A"

@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page with input forms and dashboard display"""
    
    # Handle POST requests (form submissions)
    if request.method == 'POST':
        if 'deployment_engineer' in request.form:
            user_inputs['deployment_engineer'] = request.form['deployment_engineer']
        if 'deployment_name' in request.form and request.form['deployment_name']:
            user_inputs['deployment_name'] = request.form['deployment_name']
        if 'commit_message' in request.form and request.form['commit_message']:
            user_inputs['commit_message'] = request.form['commit_message']
        if 'important_notice' in request.form and request.form['important_notice']:
            user_inputs['important_notice'] = request.form['important_notice']
        if 'message_of_the_day' in request.form and request.form['message_of_the_day']:
            user_inputs['message_of_the_day'] = request.form['message_of_the_day']
        
        # Record deployment
        if user_inputs['deployment_name']:
            record_custom_deployment()
        
        return redirect('/')
    
    # GET request - display the dashboard
    commit_count, commit_message, commit_sha = get_commit_info()
    deploy_count = get_deployment_count()
    
    # Use user-provided values or defaults
    deployment_name = user_inputs.get('deployment_name') or f"Deployment #{deploy_count}"
    display_commit_message = user_inputs.get('commit_message') or commit_message
    deployment_engineer = user_inputs.get('deployment_engineer', 'Zeeshan DevOps Engineer')
    important_notice = user_inputs.get('important_notice', 'Use commit message format deploy: Your Special Name')
    message_of_the_day = user_inputs.get('message_of_the_day', 'Keep coding and deploying! 🚀')
    
    github_run = get_github_run_number()
    github_actor = os.environ.get('GITHUB_ACTOR', 'Local')
    github_sha = os.environ.get('GITHUB_SHA', '')[:7]
    actual_deploy_num = deploy_count if deploy_count > 0 else 1
    
    # Current date/time
    now = datetime.datetime.now()
    current_date = now.strftime('%A, %B %d, %Y')
    current_time = now.strftime('%I:%M:%S %p')
    full_datetime = f"{current_date} at {current_time}"
    
    # Get deployment history
    all_deployments = []
    try:
        with open('/tmp/deploy_history.txt', 'r') as f:
            all_deployments = f.readlines()
    except:
        pass
    
    # Get GitHub runs from file
    github_run_history = []
    try:
        with open('/tmp/github_runs.txt', 'r') as f:
            github_run_history = f.readlines()
    except:
        pass
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CI/CD Pipeline Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                width: 100%;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 30px 80px rgba(0,0,0,0.35);
                animation: slideUp 0.6s ease-out;
            }}
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translateY(40px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #667eea;
                padding-bottom: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
                gap: 15px;
            }}
            .header h1 {{
                font-size: 28px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .live-indicator {{
                display: flex;
                align-items: center;
                gap: 10px;
                background: #f0fff4;
                padding: 8px 18px;
                border-radius: 50px;
                border: 2px solid #48bb78;
            }}
            .live-dot {{
                width: 12px;
                height: 12px;
                background: #48bb78;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(0.8); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            .engineer-name {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
            }}
            .badge-container {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin: 20px 0 30px 0;
            }}
            .badge {{
                padding: 12px 25px;
                border-radius: 50px;
                font-weight: 700;
                font-size: 16px;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .badge-deploy {{ background: linear-gradient(135deg, #48bb78, #38a169); color: white; }}
            .badge-commit {{ background: linear-gradient(135deg, #4299e1, #3182ce); color: white; }}
            .badge-number {{ background: linear-gradient(135deg, #ed8936, #dd6b20); color: white; }}
            .badge-success {{ background: linear-gradient(135deg, #38a169, #2f855a); color: white; }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-card {{
                background: #f7fafc;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                border-left: 5px solid #667eea;
                transition: transform 0.2s;
            }}
            .stat-card:hover {{ transform: translateY(-3px); }}
            .stat-number {{ font-size: 36px; font-weight: 800; color: #2d3748; }}
            .stat-label {{ color: #718096; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }}
            .commit-box {{
                background: linear-gradient(135deg, #2d3748, #1a202c);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
            }}
            .commit-sha {{
                background: #4a5568;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 13px;
                font-family: monospace;
                display: inline-block;
            }}
            .commit-message {{ font-size: 22px; margin: 15px 0; font-weight: 600; }}
            .commit-message-small {{ color: #a0aec0; font-size: 14px; font-weight: normal; }}
            .deployment-name-display {{
                background: #48bb78;
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                display: inline-block;
                font-size: 16px;
                font-weight: 600;
                margin-top: 10px;
            }}
            .input-section {{
                background: #f0f4ff;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid #667eea;
            }}
            .input-section h2 {{ color: #2d3748; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }}
            .input-group {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .input-field {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .input-field label {{ font-weight: 600; color: #2d3748; font-size: 14px; }}
            .input-field input, .input-field textarea {{
                padding: 10px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }}
            .input-field input:focus, .input-field textarea:focus {{
                outline: none;
                border-color: #667eea;
            }}
            .input-field textarea {{ resize: vertical; min-height: 60px; }}
            .btn-submit {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                grid-column: 1 / -1;
                width: 200px;
                margin: 0 auto;
            }}
            .btn-submit:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }}
            .steps-section {{
                background: #f7fafc;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid #e2e8f0;
            }}
            .steps-section h2 {{ color: #2d3748; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }}
            .step-item {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
                transition: background 0.2s;
            }}
            .step-item:last-child {{ border-bottom: none; }}
            .step-item:hover {{ background: #edf2f7; }}
            .step-icon {{ font-size: 20px; width: 40px; text-align: center; }}
            .step-name {{ flex: 1; font-weight: 500; color: #2d3748; }}
            .step-status {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .step-status.success {{ background: #c6f6d5; color: #22543d; }}
            .step-status.running {{ background: #fefcbf; color: #744210; }}
            .step-status.failed {{ background: #fed7d7; color: #742a2a; }}
            .step-time {{ color: #718096; font-size: 13px; font-weight: 500; }}
            .github-info {{
                background: linear-gradient(135deg, #f6f8fa, #e1e4e8);
                padding: 15px 20px;
                border-radius: 10px;
                margin: 15px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                font-size: 14px;
            }}
            .github-info span {{ color: #0366d6; font-weight: 600; }}
            .notice-section {{
                background: linear-gradient(135deg, #fefcbf, #f6e05e);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border: 2px solid #d69e2e;
            }}
            .notice-section h3 {{ color: #744210; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }}
            .notice-section p {{ color: #744210; font-size: 15px; line-height: 1.6; }}
            .motd-section {{
                background: linear-gradient(135deg, #9f7aea, #805ad5);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border: 2px solid #6b46c1;
                text-align: center;
            }}
            .motd-section h3 {{ color: white; margin-bottom: 10px; }}
            .motd-section p {{ color: #e9d8fd; font-size: 18px; font-weight: 600; }}
            .tasks-section {{
                background: #f7fafc;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
            }}
            .tasks-section h2 {{ margin-bottom: 15px; color: #2d3748; }}
            .task-item {{
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 16px;
            }}
            .task-item:last-child {{ border-bottom: none; }}
            .task-status {{ font-size: 20px; }}
            .history-section {{
                background: #ebf8ff;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid #bee3f8;
            }}
            .history-section h2 {{ color: #2b6cb0; margin-bottom: 15px; }}
            .history-item {{
                padding: 10px 15px;
                border-bottom: 1px solid #bee3f8;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .history-item:last-child {{ border-bottom: none; }}
            .history-number {{
                background: #4299e1;
                color: white;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            .history-time {{ color: #718096; font-size: 13px; }}
            .deployment-time {{
                background: #2d3748;
                color: #a0aec0;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 13px;
                display: inline-block;
                margin-top: 5px;
            }}
            .github-run-item {{
                padding: 10px 15px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                background: #f7fafc;
                border-radius: 8px;
                margin: 5px 0;
            }}
            .github-run-item:hover {{ background: #edf2f7; }}
            .run-number {{
                background: #2d3748;
                color: white;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            .run-commit {{ font-weight: 500; color: #2d3748; }}
            .run-actor {{ color: #718096; font-size: 13px; }}
            .run-time {{ color: #a0aec0; font-size: 12px; }}
            .footer {{
                text-align: center;
                color: #718096;
                font-size: 14px;
                padding-top: 20px;
                border-top: 2px solid #e2e8f0;
                margin-top: 30px;
            }}
            .footer strong {{ color: #2d3748; }}
            .footer code {{
                background: #edf2f7;
                padding: 2px 8px;
                border-radius: 4px;
                font-family: monospace;
            }}
            @media (max-width: 768px) {{
                .input-group {{ grid-template-columns: 1fr; }}
                .container {{ padding: 20px; }}
                .header h1 {{ font-size: 22px; }}
                .badge {{ font-size: 13px; padding: 8px 16px; }}
                .commit-message {{ font-size: 18px; }}
                .stats-grid {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- HEADER -->
            <div class="header">
                <h1>🚀 CI/CD Pipeline Dashboard</h1>
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span style="font-weight: 600; color: #2d3748;">LIVE</span>
                    <span class="engineer-name">👨‍💻 {deployment_engineer}</span>
                </div>
            </div>
            
            <!-- INPUT SECTION -->
            <div class="input-section">
                <h2>✏️ Enter Deployment Details</h2>
                <form method="POST" action="/">
                    <div class="input-group">
                        <div class="input-field">
                            <label for="deployment_engineer">👨‍💻 Deployment Engineer Name</label>
                            <input type="text" id="deployment_engineer" name="deployment_engineer" 
                                   value="{deployment_engineer}" placeholder="Enter your name">
                        </div>
                        <div class="input-field">
                            <label for="deployment_name">🎯 Deployment Name</label>
                            <input type="text" id="deployment_name" name="deployment_name" 
                                   value="{user_inputs.get('deployment_name', '')}" placeholder="Enter deployment name">
                        </div>
                        <div class="input-field">
                            <label for="commit_message">📝 Commit Message</label>
                            <input type="text" id="commit_message" name="commit_message" 
                                   value="{user_inputs.get('commit_message', '')}" placeholder="Enter commit message">
                        </div>
                        <div class="input-field">
                            <label for="important_notice">📢 Important Notice</label>
                            <textarea id="important_notice" name="important_notice" 
                                      placeholder="Enter custom notice">{important_notice}</textarea>
                        </div>
                        <div class="input-field">
                            <label for="message_of_the_day">💡 Message of the Day</label>
                            <input type="text" id="message_of_the_day" name="message_of_the_day" 
                                   value="{message_of_the_day}" placeholder="Enter MOTD">
                        </div>
                        <button type="submit" class="btn-submit">🚀 Deploy Now</button>
                    </div>
                </form>
            </div>
            
            <!-- BADGES -->
            <div class="badge-container">
                <div class="badge badge-deploy">🎯 {deployment_name}</div>
                <div class="badge badge-commit">📝 Commit #{commit_count}</div>
                <div class="badge badge-number">🔄 Deploy #{actual_deploy_num}</div>
                <div class="badge badge-success">✅ Build #{commit_count}</div>
            </div>
            
            <!-- STATS -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{actual_deploy_num}</div>
                    <div class="stat-label">Total Deployments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{commit_count}</div>
                    <div class="stat-label">Total Commits</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(tasks)}</div>
                    <div class="stat-label">Total Tasks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="font-size: 20px;">{current_time}</div>
                    <div class="stat-label" style="font-size: 11px;">{current_date}</div>
                </div>
            </div>
            
            <!-- GITHUB ACTIONS INFO -->
            <div class="github-info">
                <span>🔗 GitHub Actions: <span>Run {github_run}</span></span>
                <span>👤 Triggered by: <span>{github_actor}</span></span>
                <span>🔑 SHA: <span>{github_sha or commit_sha}</span></span>
                <span>✅ Status: <span style="color: #48bb78;">Success</span></span>
            </div>
            
            <!-- COMMIT INFO -->
            <div class="commit-box">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <span class="commit-sha">🔑 {commit_sha}</span>
                    <span class="deployment-time" style="font-weight: bold; color: #48bb78;">📅 Deployed: {full_datetime}</span>
                </div>
                <div class="commit-message">
                    📝 {display_commit_message}
                    <div class="commit-message-small">(commit message)</div>
                </div>
                <div class="deployment-name-display">
                    🏷️ {deployment_name}
                </div>
            </div>
            
            <!-- MESSAGE OF THE DAY -->
            <div class="motd-section">
                <h3>💡 Message of the Day</h3>
                <p>{message_of_the_day}</p>
            </div>
            
            <!-- GITHUB ACTIONS STEPS -->
            <div class="steps-section">
                <h2>⚙️ GitHub Actions Steps</h2>
                <div style="margin-bottom: 10px; font-size: 14px; color: #718096;">
                    Run {github_run} · Total duration: 24s
                </div>
                <div class="step-item">
                    <span class="step-icon">📥</span>
                    <span class="step-name">Checkout code</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">2s</span>
                </div>
                <div class="step-item">
                    <span class="step-icon">🐍</span>
                    <span class="step-name">Set up Python</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">1s</span>
                </div>
                <div class="step-item">
                    <span class="step-icon">📦</span>
                    <span class="step-name">Install dependencies</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">6s</span>
                </div>
                <div class="step-item">
                    <span class="step-icon">🧪</span>
                    <span class="step-name">Run tests</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">1s</span>
                </div>
                <div class="step-item">
                    <span class="step-icon">🚀</span>
                    <span class="step-name">Start app and record deployment</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">10s</span>
                </div>
                <div class="step-item">
                    <span class="step-icon">📊</span>
                    <span class="step-name">Show deployment info</span>
                    <span class="step-status success">✅ SUCCESS</span>
                    <span class="step-time">0s</span>
                </div>
            </div>
            
            <!-- NOTICE SECTION -->
            <div class="notice-section">
                <h3>📢 Important Notice</h3>
                <p>{important_notice}</p>
                <p style="margin-top: 10px; font-size: 13px;">
                    🔄 This page updates automatically on every GitHub Actions deployment
                </p>
            </div>
            
            <!-- HISTORY -->
            <div class="history-section">
                <h2>🔄 Deployment History</h2>
    """
    
    # Display GitHub Actions runs
    if github_run_history:
        for line in github_run_history[-10:]:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                html += f"""
                        <div class="github-run-item">
                            <span><span class="run-number">{parts[0].strip()}</span></span>
                            <span class="run-commit">{parts[1].strip()}</span>
                            <span class="run-actor">👤 {parts[2].strip()}</span>
                            <span class="run-time">{parts[3].strip()}</span>
                        </div>
                        """
    
    # Display local deployment history
    if all_deployments:
        for line in all_deployments[-10:]:
            parts = line.strip().split(' - ')
            if len(parts) >= 2:
                html += f"""
                        <div class="history-item">
                            <span><span class="history-number">{parts[0]}</span> {parts[1]}</span>
                            <span class="history-time">{parts[2] if len(parts) > 2 else ''}</span>
                        </div>
                        """
    elif deployment_history:
        for deploy in deployment_history[-10:]:
            html += f"""
                    <div class="history-item">
                        <span><span class="history-number">#{deploy['number']}</span> {deploy['name']}</span>
                        <span class="history-time">{deploy['time'][:16]}</span>
                    </div>
                    """
    else:
        html += '<div class="history-item" style="justify-content: center; color: #718096;">📭 No deployments yet. Fill the form above or push to GitHub!</div>'
    
    html += f"""
            </div>
            
            <!-- FOOTER -->
            <div class="footer">
                <p>
                    <strong>💡 Tip:</strong> Use the form above to enter your deployment details!
                </p>
                <p style="margin-top: 10px; font-size: 12px;">
                    🔄 This page updates automatically on every GitHub Actions deployment
                </p>
                <p style="margin-top: 5px; font-size: 12px; color: #a0aec0;">
                    Made with ❤️ by {deployment_engineer}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def record_custom_deployment():
    """Record a deployment with custom details"""
    commit_count, commit_message, commit_sha = get_commit_info()
    
    deploy_name = user_inputs.get('deployment_name', f"Deployment #{get_deployment_count() + 1}")
    deploy_engineer = user_inputs.get('deployment_engineer', 'Zeeshan DevOps Engineer')
    commit_msg = user_inputs.get('commit_message', commit_message)
    notice = user_inputs.get('important_notice', 'Default notice')
    motd = user_inputs.get('message_of_the_day', 'Keep coding! 🚀')
    
    current_count = increment_deployment_count()
    now = datetime.datetime.now()
    full_time = now.strftime('%A, %B %d, %Y at %I:%M:%S %p')
    
    deployment_record = {
        "number": current_count,
        "time": full_time,
        "commit": commit_msg[:50],
        "sha": commit_sha,
        "name": deploy_name,
        "engineer": deploy_engineer,
        "notice": notice,
        "motd": motd
    }
    
    deployment_history.append(deployment_record)
    
    # Save to files
    with open('/tmp/deploy_history.txt', 'a') as f:
        f.write(f"#{current_count} - {deploy_name} - {full_time}\n")
    
    with open('/tmp/github_runs.txt', 'a') as f:
        f.write(f"#{current_count} | {deploy_name} | {deploy_engineer} | {full_time}\n")
    
    return deployment_record

@app.route('/deploy', methods=['POST'])
def record_deployment():
    """Record a deployment from GitHub Actions"""
    # Check if JSON is provided
    if request.is_json:
        data = request.get_json()
    else:
        data = {}
    
    # Get values from GitHub Actions or use defaults
    deploy_engineer = data.get('deployment_engineer', os.environ.get('DEPLOYMENT_ENGINEER', 'Zeeshan DevOps Engineer'))
    deploy_name = data.get('deployment_name', os.environ.get('DEPLOYMENT_NAME', 'Auto Deployment'))
    commit_msg = data.get('commit_message', os.environ.get('COMMIT_MESSAGE', 'deploy: Auto Deployment'))
    notice = data.get('important_notice', os.environ.get('IMPORTANT_NOTICE', 'Default notice'))
    motd = data.get('message_of_the_day', os.environ.get('MESSAGE_OF_THE_DAY', 'Keep coding! 🚀'))
    run_number = data.get('github_run_number', os.environ.get('GITHUB_RUN_NUMBER', 'N/A'))
    actor = data.get('github_actor', os.environ.get('GITHUB_ACTOR', 'Local'))
    sha = data.get('github_sha', os.environ.get('GITHUB_SHA', ''))[:7]
    
    # Update user inputs
    user_inputs['deployment_engineer'] = deploy_engineer
    user_inputs['deployment_name'] = deploy_name
    user_inputs['commit_message'] = commit_msg
    user_inputs['important_notice'] = notice
    user_inputs['message_of_the_day'] = motd
    
    # Record deployment
    current_count = increment_deployment_count()
    now = datetime.datetime.now()
    full_time = now.strftime('%A, %B %d, %Y at %I:%M:%S %p')
    
    deployment_record = {
        "number": current_count,
        "time": full_time,
        "commit": commit_msg[:50],
        "sha": sha,
        "name": deploy_name,
        "engineer": deploy_engineer,
        "notice": notice,
        "motd": motd,
        "run_number": run_number,
        "actor": actor
    }
    
    deployment_history.append(deployment_record)
    
    # Save to files
    with open('/tmp/deploy_history.txt', 'a') as f:
        f.write(f"#{current_count} - {deploy_name} - {full_time}\n")
    
    with open('/tmp/github_runs.txt', 'a') as f:
        f.write(f"#{current_count} | {deploy_name} | {actor} | {full_time}\n")
    
    return jsonify({
        "status": "deployment recorded",
        "deployment": deployment_record
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "title is required"}), 400
    new_task = {"id": len(tasks) + 1, "title": data['title'], "completed": False}
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/reset', methods=['POST'])
def reset_deployments():
    with open('/tmp/deploy_count.txt', 'w') as f:
        f.write('0')
    with open('/tmp/deploy_history.txt', 'w') as f:
        f.write('')
    with open('/tmp/github_runs.txt', 'w') as f:
        f.write('')
    return jsonify({"status": "reset successful"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
