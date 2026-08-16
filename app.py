from flask import Flask, jsonify, request, redirect
import datetime
import subprocess
import os
import json

app = Flask(__name__)

# File path in the repository
HISTORY_FILE = 'deploy_history.txt'
COUNT_FILE = 'deploy_count.txt'

tasks = [
    {"id": 1, "title": "Learn CI/CD", "completed": False},
    {"id": 2, "title": "Implement GitHub Actions", "completed": False},
]

def get_deployment_count():
    try:
        with open(COUNT_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def increment_deployment_count():
    count = get_deployment_count()
    new_count = count + 1
    with open(COUNT_FILE, 'w') as f:
        f.write(str(new_count))
    return new_count

def get_deployment_history():
    history = []
    try:
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8:
                    history.append({
                        'run_number': parts[0].strip(),
                        'deployment_name': parts[1].strip(),
                        'engineer': parts[2].strip(),
                        'commit_message': parts[3].strip(),
                        'important_notice': parts[4].strip(),
                        'motd': parts[5].strip(),
                        'actor': parts[6].strip(),
                        'sha': parts[7].strip(),
                        'timestamp': parts[8].strip() if len(parts) > 8 else ''
                    })
    except:
        pass
    return history

@app.route('/', methods=['GET', 'POST'])
def home():
    deploy_count = get_deployment_count()
    history = get_deployment_history()
    latest = history[-1] if history else None
    
    now = datetime.datetime.now()
    current_date = now.strftime('%A, %B %d, %Y')
    current_time = now.strftime('%I:%M:%S %p')
    
    if latest:
        deployment_name = latest.get('deployment_name', f"Deployment #{deploy_count}")
        engineer = latest.get('engineer', 'Zeeshan DevOps Engineer')
        commit_msg = latest.get('commit_message', 'No commit message')
        notice = latest.get('important_notice', 'Use deploy: Your Special Name')
        motd = latest.get('motd', 'Keep coding and deploying! 🚀')
        run_number = latest.get('run_number', str(deploy_count))
        actor = latest.get('actor', 'zeeshandevopsengineer')
        sha = latest.get('sha', 'N/A')
    else:
        deployment_name = f"Deployment #{deploy_count}"
        engineer = 'Zeeshan DevOps Engineer'
        commit_msg = 'No deployments yet'
        notice = 'Use deploy: Your Special Name'
        motd = 'Keep coding and deploying! 🚀'
        run_number = str(deploy_count)
        actor = 'zeeshandevopsengineer'
        sha = 'N/A'
    
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
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
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
            .dashboard-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin: 20px 0;
            }}
            .column {{
                background: #f7fafc;
                border-radius: 15px;
                padding: 25px;
                border: 2px solid #e2e8f0;
            }}
            .column h2 {{
                color: #2d3748;
                font-size: 18px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .deployment-detail {{
                padding: 12px 0;
                border-bottom: 1px solid #e2e8f0;
            }}
            .deployment-detail:last-child {{ border-bottom: none; }}
            .detail-label {{
                font-size: 13px;
                color: #718096;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .detail-value {{
                font-size: 18px;
                font-weight: 600;
                color: #2d3748;
                margin-top: 4px;
            }}
            .detail-value.notice {{
                color: #744210;
                background: #fefcbf;
                padding: 5px 12px;
                border-radius: 8px;
                display: inline-block;
            }}
            .detail-value.motd {{
                color: white;
                background: linear-gradient(135deg, #9f7aea, #805ad5);
                padding: 8px 15px;
                border-radius: 10px;
                display: inline-block;
                font-size: 20px;
            }}
            .detail-value.time {{
                font-size: 24px;
                font-weight: 800;
                color: #48bb78;
                background: #f0fff4;
                padding: 8px 15px;
                border-radius: 10px;
                display: inline-block;
            }}
            .workflow-item {{
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
                border-radius: 8px;
            }}
            .workflow-item:hover {{ background: #edf2f7; }}
            .workflow-item:last-child {{ border-bottom: none; }}
            .workflow-title {{
                font-weight: 600;
                color: #2d3748;
                font-size: 16px;
            }}
            .workflow-title .run-badge {{
                background: #4299e1;
                color: white;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 12px;
                margin-right: 8px;
            }}
            .workflow-details {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 5px;
                font-size: 14px;
                color: #718096;
            }}
            .workflow-commit {{
                font-family: monospace;
                background: #edf2f7;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 13px;
            }}
            .workflow-actor {{
                color: #2d3748;
                font-weight: 500;
            }}
            .workflow-time {{
                color: #a0aec0;
                font-size: 13px;
            }}
            .workflow-duration {{
                background: #c6f6d5;
                color: #22543d;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            .footer {{
                text-align: center;
                color: #718096;
                font-size: 14px;
                padding-top: 20px;
                border-top: 2px solid #e2e8f0;
                margin-top: 30px;
            }}
            @media (max-width: 900px) {{
                .dashboard-grid {{ grid-template-columns: 1fr; }}
                .container {{ padding: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 CI/CD Pipeline Dashboard</h1>
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span style="font-weight: 600; color: #2d3748;">LIVE</span>
                    <span class="engineer-name">👨‍💻 {engineer}</span>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <div class="column">
                    <h2>📋 Current Deployment</h2>
                    <div class="deployment-detail">
                        <div class="detail-label">🎯 Deployment Name</div>
                        <div class="detail-value">{deployment_name}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">📝 Commit Message</div>
                        <div class="detail-value">{commit_msg}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">🔄 Run Number</div>
                        <div class="detail-value">#{run_number}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">📢 Important Notice</div>
                        <div class="detail-value notice">{notice}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">💡 Message of the Day</div>
                        <div class="detail-value motd">{motd}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">📅 Deployed Time</div>
                        <div class="detail-value time">🕐 {current_time}</div>
                        <div style="font-size: 14px; color: #718096; margin-top: 4px;">{current_date}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">👤 Triggered By</div>
                        <div class="detail-value" style="font-size: 16px;">{actor}</div>
                    </div>
                    <div class="deployment-detail">
                        <div class="detail-label">🔑 Commit SHA</div>
                        <div class="detail-value" style="font-size: 14px; font-family: monospace;">{sha}</div>
                    </div>
                </div>
                
                <div class="column">
                    <h2>🔄 GitHub Actions Workflow History</h2>
    """
    
    if history:
        for item in reversed(history[-15:]):
            run_num = item.get('run_number', 'N/A')
            name = item.get('deployment_name', 'Unknown')
            actor = item.get('actor', 'unknown')
            sha = item.get('sha', '')[:7]
            timestamp = item.get('timestamp', '')
            
            time_ago = "N/A"
            if timestamp:
                try:
                    dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    diff = datetime.datetime.now() - dt
                    minutes = int(diff.total_seconds() / 60)
                    if minutes < 1:
                        time_ago = "just now"
                    elif minutes < 60:
                        time_ago = f"{minutes} minutes ago"
                    else:
                        hours = int(minutes / 60)
                        time_ago = f"{hours} hours ago"
                except:
                    time_ago = "N/A"
            
            html += f"""
                    <div class="workflow-item">
                        <div class="workflow-title">
                            <span class="run-badge">#{run_num}</span>
                            {name}
                        </div>
                        <div class="workflow-details">
                            <span>
                                <span class="workflow-commit">Commit {sha}</span>
                                <span class="workflow-actor">pushed by {actor}</span>
                            </span>
                            <span>
                                <span class="workflow-time">main · {time_ago}</span>
                                <span class="workflow-duration">24s</span>
                            </span>
                        </div>
                    </div>
            """
    else:
        html += """
                    <div style="text-align: center; color: #718096; padding: 40px 0;">
                        <p style="font-size: 18px;">📭 No deployments yet</p>
                        <p style="font-size: 14px; margin-top: 10px;">Push to GitHub and run the workflow!</p>
                    </div>
        """
    
    html += f"""
                </div>
            </div>
            
            <div class="footer">
                <p><strong>💡 Tip:</strong> Fill the 5 fields in GitHub Actions "Run workflow" form!</p>
                <p style="margin-top: 10px; font-size: 12px;">🔄 This page displays data from GitHub Actions deployments</p>
                <p style="margin-top: 5px; font-size: 12px; color: #a0aec0;">Made with ❤️ by {engineer}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/deploy', methods=['POST'])
def record_deployment():
    if request.is_json:
        data = request.get_json()
    else:
        data = {}
    
    deploy_engineer = data.get('deployment_engineer', 'Zeeshan DevOps Engineer')
    deploy_name = data.get('deployment_name', 'Auto Deployment')
    commit_msg = data.get('commit_message', 'deploy: Auto Deployment')
    notice = data.get('important_notice', 'Use deploy: Your Special Name')
    motd = data.get('message_of_the_day', 'Keep coding and deploying! 🚀')
    run_number = data.get('run_number', '1')
    actor = data.get('actor', 'Local')
    sha = data.get('sha', 'N/A')
    
    current_count = increment_deployment_count()
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{current_count}|{deploy_name}|{deploy_engineer}|{commit_msg}|{notice}|{motd}|{actor}|{sha}|{timestamp}\n")
    
    return jsonify({"status": "deployment recorded"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
