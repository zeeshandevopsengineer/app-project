from flask import Flask, jsonify, request
import datetime
import subprocess
import os

app = Flask(__name__)

# Store tasks in memory
tasks = [
    {"id": 1, "title": "Learn CI/CD", "completed": False},
    {"id": 2, "title": "Implement GitHub Actions", "completed": False},
]

# Store deployment history
deployment_history = []

def get_commit_info():
    """Get the latest commit message, count, and SHA"""
    try:
        # Get commit count
        count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD']).decode().strip()
        # Get latest commit message
        message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
        # Get short commit SHA
        sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        return count, message, sha
    except:
        return "0", "No commits yet", "N/A"

def get_deployment_count():
    """Get deployment count from file or history"""
    try:
        with open('/tmp/deploy_count.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return len(deployment_history) + 1

def increment_deployment_count():
    """Increment deployment counter"""
    count = get_deployment_count()
    with open('/tmp/deploy_count.txt', 'w') as f:
        f.write(str(count + 1))
    return count

@app.route('/')
def home():
    """Home page showing deployment info with beautiful UI"""
    commit_count, commit_message, commit_sha = get_commit_info()
    
    # Get deployment count
    deploy_count = get_deployment_count()
    
    # Get deployment name from commit message
    if "deploy:" in commit_message.lower():
        deployment_name = commit_message.split("deploy:")[1].strip().split("\n")[0]
    else:
        deployment_name = f"Deployment #{deploy_count}"
    
    # Get the actual deployment number from the commit count
    actual_deploy_num = deploy_count
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CI/CD Pipeline Demo - {deployment_name}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
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
                max-width: 1000px;
                width: 100%;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 30px 80px rgba(0,0,0,0.35);
                animation: slideUp 0.6s ease-out;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(40px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
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
            
            .badge-deploy {{
                background: linear-gradient(135deg, #48bb78, #38a169);
                color: white;
            }}
            
            .badge-commit {{
                background: linear-gradient(135deg, #4299e1, #3182ce);
                color: white;
            }}
            
            .badge-number {{
                background: linear-gradient(135deg, #ed8936, #dd6b20);
                color: white;
            }}
            
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
            
            .stat-card:hover {{
                transform: translateY(-3px);
            }}
            
            .stat-number {{
                font-size: 36px;
                font-weight: 800;
                color: #2d3748;
            }}
            
            .stat-label {{
                color: #718096;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 5px;
            }}
            
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
            
            .commit-message {{
                font-size: 22px;
                margin: 15px 0;
                font-weight: 600;
            }}
            
            .commit-message-small {{
                color: #a0aec0;
                font-size: 14px;
                font-weight: normal;
            }}
            
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
            
            .tasks-section {{
                background: #f7fafc;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
            }}
            
            .tasks-section h2 {{
                margin-bottom: 15px;
                color: #2d3748;
            }}
            
            .task-item {{
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 16px;
            }}
            
            .task-item:last-child {{
                border-bottom: none;
            }}
            
            .task-status {{
                font-size: 20px;
            }}
            
            .history-section {{
                background: #ebf8ff;
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid #bee3f8;
            }}
            
            .history-section h2 {{
                color: #2b6cb0;
                margin-bottom: 15px;
            }}
            
            .history-item {{
                padding: 10px 15px;
                border-bottom: 1px solid #bee3f8;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            
            .history-item:last-child {{
                border-bottom: none;
            }}
            
            .history-number {{
                background: #4299e1;
                color: white;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            
            .history-time {{
                color: #718096;
                font-size: 13px;
            }}
            
            .footer {{
                text-align: center;
                color: #718096;
                font-size: 14px;
                padding-top: 20px;
                border-top: 2px solid #e2e8f0;
                margin-top: 30px;
            }}
            
            .footer strong {{
                color: #2d3748;
            }}
            
            .footer code {{
                background: #edf2f7;
                padding: 2px 8px;
                border-radius: 4px;
                font-family: monospace;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    padding: 20px;
                }}
                .header h1 {{
                    font-size: 22px;
                }}
                .badge {{
                    font-size: 13px;
                    padding: 8px 16px;
                }}
                .commit-message {{
                    font-size: 18px;
                }}
                .stats-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
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
                </div>
            </div>
            
            <!-- BADGES -->
            <div class="badge-container">
                <div class="badge badge-deploy">
                    🎯 {deployment_name}
                </div>
                <div class="badge badge-commit">
                    📝 Commit #{commit_count}
                </div>
                <div class="badge badge-number">
                    🔄 Deploy #{actual_deploy_num}
                </div>
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
                    <div class="stat-number">{datetime.datetime.now().strftime('%H:%M')}</div>
                    <div class="stat-label">Last Updated</div>
                </div>
            </div>
            
            <!-- COMMIT INFO -->
            <div class="commit-box">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <span class="commit-sha">🔑 {commit_sha}</span>
                    <span style="color: #a0aec0; font-size: 14px;">{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="commit-message">
                    📝 {commit_message}
                    <div class="commit-message-small">(commit message)</div>
                </div>
                <div class="deployment-name-display">
                    🏷️ {deployment_name}
                </div>
            </div>
            
            <!-- TASKS -->
            <div class="tasks-section">
                <h2>📋 Current Tasks</h2>
    """
    
    for task in tasks:
        status = "✅" if task["completed"] else "⬜"
        html += f"""
                <div class="task-item">
                    <span class="task-status">{status}</span>
                    <span>{task['title']}</span>
                </div>
        """
    
    html += f"""
            </div>
            
            <!-- HISTORY -->
            <div class="history-section">
                <h2>🔄 Deployment History</h2>
    """
    
    # Get history from file if exists
    try:
        with open('/tmp/deploy_history.txt', 'r') as f:
            history_lines = f.readlines()[-5:]
            if history_lines:
                for line in history_lines:
                    parts = line.strip().split(' - ')
                    if len(parts) >= 2:
                        html += f"""
                        <div class="history-item">
                            <span><span class="history-number">{parts[0]}</span> {parts[1]}</span>
                            <span class="history-time">{parts[2] if len(parts) > 2 else ''}</span>
                        </div>
                        """
            else:
                html += '<div class="history-item">No deployments yet</div>'
    except:
        # Use in-memory history
        if deployment_history:
            for deploy in deployment_history[-5:]:
                html += f"""
                <div class="history-item">
                    <span><span class="history-number">#{deploy['number']}</span> {deploy['name']}</span>
                    <span class="history-time">{deploy['time'][:16]}</span>
                </div>
                """
        else:
            html += '<div class="history-item">No deployments yet</div>'
    
    html += f"""
            </div>
            
            <!-- FOOTER -->
            <div class="footer">
                <p>
                    <strong>💡 Tip:</strong> Use commit message format 
                    <code>deploy: Your Special Name</code>
                    to give each deployment a custom name!
                </p>
                <p style="margin-top: 10px; font-size: 12px;">
                    🔄 This page updates automatically on every GitHub Actions deployment
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "title is required"}), 400
    
    new_task = {
        "id": len(tasks) + 1,
        "title": data['title'],
        "completed": False
    }
    tasks.append(new_task)
    
    return jsonify(new_task), 201

@app.route('/deploy', methods=['POST'])
def record_deployment():
    """Record a deployment with custom name"""
    commit_count, commit_message, commit_sha = get_commit_info()
    
    # Get deployment name from commit message
    if "deploy:" in commit_message.lower():
        deploy_name = commit_message.split("deploy:")[1].strip().split("\n")[0]
    else:
        deploy_name = f"Deployment #{get_deployment_count()}"
    
    # Get current count
    current_count = get_deployment_count()
    
    deployment_record = {
        "number": current_count,
        "time": datetime.datetime.now().isoformat(),
        "commit": commit_message[:50],
        "sha": commit_sha,
        "name": deploy_name
    }
    
    deployment_history.append(deployment_record)
    
    # Save to file for persistence
    with open('/tmp/deploy_history.txt', 'a') as f:
        f.write(f"#{current_count} - {deploy_name} - {datetime.datetime.now().strftime('%H:%M')}\n")
    
    # Increment for next time
    increment_deployment_count()
    
    return jsonify({
        "status": "deployment recorded",
        "deployment": deployment_record
    })

@app.route('/reset', methods=['POST'])
def reset_deployments():
    """Reset deployment counter (for testing)"""
    with open('/tmp/deploy_count.txt', 'w') as f:
        f.write('1')
    with open('/tmp/deploy_history.txt', 'w') as f:
        f.write('')
    return jsonify({"status": "reset successful"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
