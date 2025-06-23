from flask import Flask, render_template, redirect, request, jsonify
from flask_socketio import SocketIO
import uuid

app = Flask(__name__)
socketio = SocketIO(app)

panel_data = []

@app.route('/')
def index():
    return render_template('panel.html', data=panel_data)

@app.route('/generate', methods=['POST'])
def generate():
    new_id = str(uuid.uuid4())[:8]
    new_url = request.host_url + 'ref/' + new_id
    panel_data.append({
        'id': new_id,
        'url': new_url,
        'count': 0,
        'direct_clicks': 0,
        'referer_counts': {}
    })
    socketio.emit('update_panel', panel_data)
    return redirect('/')

@app.route('/ref/<ref_id>')
def ref_click(ref_id):
    referer = request.headers.get('Referer', '') or request.headers.get('referer', '')
    for row in panel_data:
        if row['id'] == ref_id:
            row['count'] += 1

            if referer == '' or referer.startswith(request.host_url):
                row['direct_clicks'] += 1
            else:
                domain = referer.split('/')[2] if '://' in referer else referer
                if domain in row['referer_counts']:
                    row['referer_counts'][domain] += 1
                else:
                    row['referer_counts'][domain] = 1

            socketio.emit('update_panel', panel_data)
            break
    return "✅ Thanks for clicking!"

@app.route('/delete/<ref_id>', methods=['POST'])
def delete_ref(ref_id):
    global panel_data
    panel_data = [row for row in panel_data if row['id'] != ref_id]
    socketio.emit('update_panel', panel_data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
