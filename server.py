"""
OpenGlaze - Open Source Ceramic Glaze Management System
MIT License
"""
import os
import json
import sqlite3
from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
from auth import get_current_user, require_auth
from billing.router import get_provider

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///glazelab.db')
KRATOS_PUBLIC_URL = os.environ.get('KRATOS_PUBLIC_URL', 'http://localhost:4433')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8768')

# Database setup
def get_db():
    """Get database connection."""
    if DATABASE_URL.startswith('postgres'):
        # PostgreSQL connection
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
    else:
        # SQLite connection
        conn = sqlite3.connect('glazelab.db')
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema."""
    with open('schema.sql', 'r') as f:
        schema = f.read()

    conn = get_db()
    conn.executescript(schema)
    conn.commit()
    conn.close()

# ============================================================================
# STATIC FILES
# ============================================================================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page for authenticated users."""
    return send_from_directory('static', 'dashboard.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.route('/auth/login', methods=['GET'])
def login():
    """Redirect to Kratos login flow."""
    return redirect(f"{KRATOS_PUBLIC_URL}/self-service/login/browser")

@app.route('/auth/register', methods=['GET'])
def register():
    """Redirect to Kratos registration flow."""
    return redirect(f"{KRATOS_PUBLIC_URL}/self-service/registration/browser")

@app.route('/auth/logout', methods=['GET'])
def logout():
    """Redirect to Kratos logout flow."""
    return redirect(f"{KRATOS_PUBLIC_URL}/self-service/logout/browser")

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """Handle Kratos callback after login."""
    user = get_current_user(request)
    if user:
        return redirect('/dashboard')
    return redirect('/login?error=session_invalid')

# ============================================================================
# USER API
# ============================================================================

@app.route('/api/me', methods=['GET'])
@require_auth
def get_me():
    """Get current user info."""
    user = request.user
    return jsonify({
        'id': user['id'],
        'email': user['traits'].get('email'),
        'studio_name': user['traits'].get('studio_name'),
        'tier': user['traits'].get('tier', 'free'),
        'template_id': user['traits'].get('template_id')
    })

@app.route('/api/me', methods=['PATCH'])
@require_auth
def update_me():
    """Update current user info."""
    user = request.user
    data = request.json

    # Update via Kratos admin API
    # TODO: Implement Kratos identity update

    return jsonify({'status': 'updated'})

# ============================================================================
# DEMO API (no auth required)
# ============================================================================

@app.route('/api/demo/glazes', methods=['GET'])
def get_demo_glazes():
    """Get demo glazes for unauthenticated users."""
    conn = get_db()
    cursor = conn.execute(
        'SELECT * FROM glazes WHERE user_id = ? ORDER BY created_at DESC',
        ('demo-user-001',)
    )
    glazes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(glazes)

# ============================================================================
# GLAZE API
# ============================================================================

@app.route('/api/glazes', methods=['GET'])
@require_auth
def list_glazes():
    """List all glazes for current user."""
    conn = get_db()
    cursor = conn.execute(
        'SELECT * FROM glazes WHERE user_id = ? ORDER BY created_at DESC',
        (request.user['id'],)
    )
    glazes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(glazes)

@app.route('/api/glazes', methods=['POST'])
@require_auth
def create_glaze():
    """Create a new glaze."""
    data = request.json

    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO glazes (user_id, name, cone, atmosphere, base_type,
           surface, color, transparency, notes, recipe)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (request.user['id'], data['name'], data.get('cone'),
         data.get('atmosphere'), data.get('base_type'), data.get('surface'),
         data.get('color'), data.get('transparency'), data.get('notes'),
         json.dumps(data.get('recipe', [])))
    )
    glaze_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'id': glaze_id, 'status': 'created'}), 201

@app.route('/api/glazes/<glaze_id>', methods=['GET'])
@require_auth
def get_glaze(glaze_id):
    """Get a specific glaze."""
    conn = get_db()
    cursor = conn.execute(
        'SELECT * FROM glazes WHERE id = ? AND user_id = ?',
        (glaze_id, request.user['id'])
    )
    glaze = cursor.fetchone()
    conn.close()

    if not glaze:
        return jsonify({'error': 'Glaze not found'}), 404

    return jsonify(dict(glaze))

@app.route('/api/glazes/<glaze_id>', methods=['PUT'])
@require_auth
def update_glaze(glaze_id):
    """Update a glaze."""
    data = request.json

    conn = get_db()
    cursor = conn.execute(
        'SELECT id FROM glazes WHERE id = ? AND user_id = ?',
        (glaze_id, request.user['id'])
    )
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Glaze not found'}), 404

    conn.execute(
        '''UPDATE glazes SET name = ?, cone = ?, atmosphere = ?, base_type = ?,
           surface = ?, color = ?, transparency = ?, notes = ?, recipe = ?,
           updated_at = CURRENT_TIMESTAMP
           WHERE id = ?''',
        (data['name'], data.get('cone'), data.get('atmosphere'),
         data.get('base_type'), data.get('surface'), data.get('color'),
         data.get('transparency'), data.get('notes'),
         json.dumps(data.get('recipe', [])), glaze_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'updated'})

@app.route('/api/glazes/<glaze_id>', methods=['DELETE'])
@require_auth
def delete_glaze(glaze_id):
    """Delete a glaze."""
    conn = get_db()
    cursor = conn.execute(
        'SELECT id FROM glazes WHERE id = ? AND user_id = ?',
        (glaze_id, request.user['id'])
    )
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Glaze not found'}), 404

    conn.execute('DELETE FROM glazes WHERE id = ?', (glaze_id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'deleted'})

# ============================================================================
# TEMPLATE API
# ============================================================================

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """List available templates."""
    import yaml
    templates_dir = 'templates'
    templates = []

    for filename in os.listdir(templates_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r') as f:
                template = yaml.safe_load(f)
                template['id'] = filename.rsplit('.', 1)[0]
                templates.append(template)

    return jsonify(templates)

@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template."""
    import yaml

    # Try both .yaml and .yml extensions
    for ext in ['.yaml', '.yml']:
        filepath = f'templates/{template_id}{ext}'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                template = yaml.safe_load(f)
                template['id'] = template_id
                return jsonify(template)

    return jsonify({'error': 'Template not found'}), 404

@app.route('/api/templates/<template_id>/apply', methods=['POST'])
@require_auth
def apply_template(template_id):
    """Apply a template to the current user's account."""
    import yaml

    # Load template
    for ext in ['.yaml', '.yml']:
        filepath = f'templates/{template_id}{ext}'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                template = yaml.safe_load(f)
            break
    else:
        return jsonify({'error': 'Template not found'}), 404

    conn = get_db()

    # Add glazes from template
    for glaze in template.get('glazes', []):
        conn.execute(
            '''INSERT INTO glazes (user_id, name, cone, atmosphere, base_type,
               surface, color, transparency, notes, recipe)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (request.user['id'], glaze['name'], glaze.get('cone'),
             glaze.get('atmosphere'), glaze.get('base_type'),
             glaze.get('surface'), glaze.get('color'),
             glaze.get('transparency'), glaze.get('notes'),
             json.dumps(glaze.get('recipe', [])))
        )

    conn.commit()
    conn.close()

    return jsonify({
        'status': 'applied',
        'glazes_added': len(template.get('glazes', []))
    })

# ============================================================================
# BILLING API
# ============================================================================

@app.route('/api/billing/providers', methods=['GET'])
def list_providers():
    """List available payment providers."""
    providers = ['stripe']

    if os.environ.get('PAYPAL_CLIENT_ID'):
        providers.append('paypal')
    if os.environ.get('BTCPAY_URL'):
        providers.append('btcpay')

    providers.append('manual')  # Always available

    return jsonify(providers)

@app.route('/api/billing/checkout', methods=['POST'])
@require_auth
def create_checkout():
    """Create a checkout session."""
    tier = request.json.get('tier')
    provider_name = request.json.get('provider', 'stripe')

    if tier not in ['pro', 'studio', 'education']:
        return jsonify({'error': 'Invalid tier'}), 400

    provider = get_provider(provider_name)
    if not provider:
        return jsonify({'error': 'Invalid provider'}), 400

    result = provider.create_checkout_session(
        user_id=request.user['id'],
        tier=tier,
        success_url=f"{BASE_URL}/billing/success",
        cancel_url=f"{BASE_URL}/billing/cancel"
    )

    return jsonify(result)

@app.route('/api/billing/webhook/<provider_name>', methods=['POST'])
def billing_webhook(provider_name):
    """Handle webhook from payment provider."""
    provider = get_provider(provider_name)
    if not provider:
        return jsonify({'error': 'Invalid provider'}), 400

    signature = request.headers.get('X-Signature') or request.headers.get('Stripe-Signature')
    result = provider.handle_webhook(request.data, signature)

    if result and result.get('action') == 'subscribe':
        # Update user tier in Kratos
        from auth import update_user_traits
        update_user_traits(result['user_id'], {'tier': result['tier']})

    return jsonify({'status': 'ok'})

# ============================================================================
# KRATOS WEBHOOKS
# ============================================================================

@app.route('/api/hooks/post-registration', methods=['POST'])
def kratos_post_registration():
    """Handle Kratos post-registration webhook."""
    from auth import update_user_traits
    import hmac
    import hashlib

    # Verify webhook signature
    hook_key = os.environ.get('KRATOS_HOOK_KEY', '')
    signature = request.headers.get('X-Kratos-Hook-Key', '')

    if not hmac.compare_digest(signature, hook_key):
        return jsonify({'error': 'Invalid signature'}), 401

    data = request.json
    user_id = data.get('identity_id')
    email = data.get('email', '')

    # Check if education domain
    education_domains = ['.edu', '.ac.uk', '.edu.au']
    tier = 'free'
    for domain in education_domains:
        if email.endswith(domain):
            tier = 'education'
            break

    # Apply template if specified
    template_id = data.get('template_id')
    if template_id:
        # Apply template in background
        pass

    # Update user tier if education
    if tier == 'education':
        update_user_traits(user_id, {'tier': tier})

    return jsonify({'status': 'ok'})

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8768, debug=True)
