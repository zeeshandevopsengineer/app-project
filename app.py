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
    """Home page showing deployment info"""
    commit_count, commit_message, commit_sha = get_commit_info()
    
    # Get deployment count (persistent across restarts)
    deploy_count = get_deployment_count()
    
    # Check if this is a special named deployment
    named_deployment = os.environ.get('DEPLOYMENT_NAME', '')
    if named_deployment:
        deployment_name = named_deployment
    else:
        # Extract custom name from commit message (format: "deploy: myname")
        if "deploy:" in commit_message.lower():
            deployment_name = commit_message.split("deploy:")[1].strip().split("\n")[0]
        else:
            deployment_name = f"Deployment #{deploy_count}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CI/CD Demo App</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ margin: 0; color: #2d3748; }}
            .badge-group {{ display: flex; gap: 15px; flex-wrap: wrap; }}
            .deploy-badge {{ background: linear-gradient(135deg, #48bb78, #38a169); color: white; padding: 12px 25px; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4); }}
            .commit-badge {{ background: linear-gradient(135deg, #4299e1, #3182ce); color: white; padding: 12px 25px; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(66, 153, 225, 0.4); }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
            .stat-card {{ background: #f7fafc; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #667eea; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #2d3748; }}
            .stat-label {{ color: #718096; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
            .commit-box {{ background: #2d3748; color: white; padding: 25px; border-radius: 10px; margin: 30px 0; }}
            .commit-message {{ font-size: 20px; margin: 10px 0; }}
            .commit-sha {{ background: #4a5568; padding: 5px 15px; border-radius: 20px; font-size: 14px; display: inline-block; }}
            .deployment-name {{ background: #48bb78; color: white; padding: 8px 20px; border-radius: 20px; display: inline-block; font-size: 16px; margin-top: 10px; }}
            .tasks {{ background: #f7fafc; padding: 20px; border-radius: 10px; margin: 30px 0; }}
            .task-item {{ padding: 10px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 10px; }}
            .history {{ background: #ebf8ff; padding: 20px; border-radius: 10px; margin-top: 30px; border: 2px solid #bee3f8; }}
            .history-item {{ padding: 8px; border-bottom: 1px solid #bee3f8; }}
            .live-indicator {{ display: inline-block; width: 12px; height: 12px; background: #48bb78; border-radius: 50%; margin-right: 10px; animation: pulse 2s infinite; }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            .footer {{ margin-top: 40px; text-align: center; color: #718096; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 CI/CD Pipeline Demo</h1>
                <span class="live-indicator"></span> Live
            </div>
            
            <div class="badge-group">
                <div class="deploy-badge">
                    🎯 {deployment_name}
                </div>
                <div class="commit-badge">
                    📝 Commit #{commit_count}
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{deploy_count}</div>
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
            </div>
            
            <div class="commit-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="commit-sha">🔑 {commit_sha}</span>
                    <span style="color: #a0aec0;">{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="commit-message">📝 {commit_message}</div>
                <div class="deployment-name">🏷️ {deployment_name}</div>
            </div>
            
            <div class="tasks">
                <h2>📋 Tasks</h2>
    """
    
    for task in tasks:
        status = "✅" if task["completed"] else "⬜"
        html += f"<div class='task-item'>{status} {task['title']}</div>"
    
    html += f"""
            </div>
            
            <div class="history">
                <h2>🔄 Deployment History (Last 5)</h2>
    """
    
    # Get history from file if exists
    try:
        with open('/tmp/deploy_history.txt', 'r') as f:
            history_lines = f.readlines()[-5:]
            for line in history_lines:
                html += f"<div class='history-item'>{line.strip()}</div>"
    except:
        # Use in-memory history
        for deploy in deployment_history[-5:]:
            html += f"<div class='history-item'>Deployment #{deploy['number']} - {deploy['time']} - {deploy['commit']}</div>"
    
    html += f"""
            </div>
            
            <div class="footer">
                <p>✨ <strong>Deployment Name:</strong> {deployment_name}</p>
                <p>🔄 This page updates on every GitHub Actions deployment</p>
                <p>⚡ <strong>Tip:</strong> Use commit message format "deploy: My Special Name" for custom names</p>
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
    
    # Get deployment name from environment or commit message
    deploy_name = os.environ.get('DEPLOYMENT_NAME', '')
    if not deploy_name:
        # Extract custom name from commit message (format: "deploy: myname")
        if "deploy:" in commit_message.lower():
            deploy_name = commit_message.split("deploy:")[1].strip().split("\n")[0]
        else:
            deploy_name = f"Deployment #{get_deployment_count()}"
    
    # Increment deployment count
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
        f.write(f"#{current_count} - {deploy_name} - {commit_message[:30]} - {datetime.datetime.now().strftime('%H:%M')}\n")
    
    # Increment for next time
    increment_deployment_count()
    
    return jsonify({
        "status": "deployment recorded",
        "deployment": deployment_record
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
