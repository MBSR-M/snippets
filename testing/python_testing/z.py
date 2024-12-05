#!/usr/bin/env python3
# coding=utf-8

import configparser
import os


class Config:
    """Configuration class for the Flask application."""

    def __init__(self, config_file='fileuploadsystem.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.load_defaults()

    def load_defaults(self):
        """Load default configurations and override with environment variables if available."""
        defaults = [
            ('uploads', 'UPLOAD_FOLDER', 'UPLOAD_FOLDER', 'uploads'),
            ('files', 'static_files', 'STATIC_FILES', 'static'),
            ('files', 'template_files', 'TEMPLATE_FILES', 'templates'),
            ('hosts', 'ip_address', 'IP_ADDRESS', '127.0.0.1'),
            ('hosts', 'port', 'PORT', '8080'),
            ('jwt_token', 'token', 'JWT_SECRET_KEY', 'd7f585a766b5dce2783dc3fc319ffebb'),
        ]

        for sec, key, envkey, val in defaults:
            if not self.config.has_section(sec):
                self.config.add_section(sec)
            if not self.config.has_option(sec, key):
                self.config.set(sec, key, str(os.environ.get(envkey, val)))

    def get_upload_folder(self):
        return self.config.get('uploads', 'UPLOAD_FOLDER')

    def get_static_files(self):
        return self.config.get('files', 'static_files')

    def get_template_files(self):
        return self.config.get('files', 'template_files')

    def get_jwt_token(self):
        return self.config.get('jwt_token', 'token')

    def get_ip_address(self):
        return self.config.get('hosts', 'ip_address')

    def get_port(self):
        return self.config.get('hosts', 'port')



c = Config()
print(c.get_upload_folder())