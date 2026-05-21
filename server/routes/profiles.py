"""
Bailando Solo — Profile management routes.
Handles CRUD for user profiles and active profile switching.
"""

import os
import json
import shutil

from flask import Blueprint, request, jsonify

from server.config import PROFILES_CONFIG_FILE, DOWNLOADS_DIR

profiles_bp = Blueprint('profiles', __name__)


# ─── Profile helpers ──────────────────────────────────────────────────────────

def load_profiles():
    """Load profiles configuration from JSON file."""
    if os.path.exists(PROFILES_CONFIG_FILE):
        try:
            with open(PROFILES_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {'active': 'Default', 'profiles': ['Default']}
    return {'active': 'Default', 'profiles': ['Default']}


def save_profiles(config):
    """Save profiles configuration to JSON file."""
    try:
        with open(PROFILES_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving profiles: {e}")


def ensure_default_profile():
    """Ensure Default profile exists and migrate existing music if needed."""
    config = load_profiles()
    default_dir = os.path.join(DOWNLOADS_DIR, 'Default')

    # Create downloads directory if it doesn't exist
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    # Create Default profile directory
    os.makedirs(default_dir, exist_ok=True)

    # Migrate existing music to Default profile
    if os.path.exists(DOWNLOADS_DIR):
        for item in os.listdir(DOWNLOADS_DIR):
            item_path = os.path.join(DOWNLOADS_DIR, item)
            # Skip if it's already a profile directory or the Default folder itself
            if os.path.isdir(item_path) and item in config['profiles']:
                continue
            # Move files and non-profile folders to Default
            if item != 'Default':
                dest_path = os.path.join(default_dir, item)
                try:
                    if os.path.isfile(item_path):
                        shutil.move(item_path, dest_path)
                    elif os.path.isdir(item_path):
                        # Move folder contents
                        if not os.path.exists(dest_path):
                            shutil.move(item_path, dest_path)
                except Exception as e:
                    print(f"Error migrating {item}: {e}")

    # Ensure Default is in profiles list
    if 'Default' not in config['profiles']:
        config['profiles'].append('Default')

    save_profiles(config)
    return config


def get_active_profile_dir():
    """Get the filesystem path for the active profile's downloads directory."""
    config = load_profiles()
    active = config.get('active', 'Default')
    return os.path.join(DOWNLOADS_DIR, active)


# ─── Routes ───────────────────────────────────────────────────────────────────

@profiles_bp.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles and the active one."""
    config = load_profiles()
    return jsonify(config)


@profiles_bp.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create a new profile."""
    data = request.json
    profile_name = data.get('name', '').strip()

    if not profile_name:
        return jsonify({'error': 'Profile name is required'}), 400

    config = load_profiles()

    if profile_name in config['profiles']:
        return jsonify({'error': 'Profile already exists'}), 400

    # Create profile directory
    profile_dir = os.path.join(DOWNLOADS_DIR, profile_name)
    try:
        os.makedirs(profile_dir, exist_ok=True)
        config['profiles'].append(profile_name)
        save_profiles(config)
        return jsonify({'status': 'success', 'profile': profile_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profiles_bp.route('/api/profiles/<profile_name>', methods=['DELETE'])
def delete_profile(profile_name):
    """Delete a profile (cannot delete Default or active profile)."""
    config = load_profiles()

    if profile_name == 'Default':
        return jsonify({'error': 'Cannot delete Default profile'}), 400

    if profile_name == config['active']:
        return jsonify({'error': 'Cannot delete active profile'}), 400

    if profile_name not in config['profiles']:
        return jsonify({'error': 'Profile not found'}), 404

    # Delete profile directory
    profile_dir = os.path.join(DOWNLOADS_DIR, profile_name)
    try:
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
        config['profiles'].remove(profile_name)
        save_profiles(config)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profiles_bp.route('/api/profiles/<profile_name>/rename', methods=['POST'])
def rename_profile(profile_name):
    """Rename a profile (cannot rename Default)."""
    data = request.json
    new_name = data.get('new_name', '').strip()

    if not new_name:
        return jsonify({'error': 'New name is required'}), 400

    if profile_name == 'Default':
        return jsonify({'error': 'Cannot rename Default profile'}), 400

    config = load_profiles()

    if profile_name not in config['profiles']:
        return jsonify({'error': 'Profile not found'}), 404

    if new_name in config['profiles']:
        return jsonify({'error': 'Profile with new name already exists'}), 400

    # Rename profile directory
    old_dir = os.path.join(DOWNLOADS_DIR, profile_name)
    new_dir = os.path.join(DOWNLOADS_DIR, new_name)

    try:
        if os.path.exists(old_dir):
            os.rename(old_dir, new_dir)

        # Update config
        index = config['profiles'].index(profile_name)
        config['profiles'][index] = new_name

        if config['active'] == profile_name:
            config['active'] = new_name

        save_profiles(config)
        return jsonify({'status': 'success', 'new_name': new_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profiles_bp.route('/api/profiles/active', methods=['POST'])
def set_active_profile():
    """Set the active profile."""
    data = request.json
    profile_name = data.get('profile')

    if not profile_name:
        return jsonify({'error': 'Profile name is required'}), 400

    config = load_profiles()

    if profile_name not in config['profiles']:
        return jsonify({'error': 'Profile not found'}), 404

    config['active'] = profile_name
    save_profiles(config)
    return jsonify({'status': 'success', 'active': profile_name})
