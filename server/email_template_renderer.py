"""
Professional Email Template Renderer
Loads HTML templates and replaces placeholders with actual data
"""

import os
from datetime import datetime

class EmailTemplateRenderer:
    """Renders professional HTML email templates with dynamic data"""
    
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'email_templates')
    
    @staticmethod
    def render_template(template_name, data):
        """
        Load template and replace placeholders with data
        
        Args:
            template_name (str): Template filename (e.g., 'test_failure.html')
            data (dict): Dictionary of placeholder keys and values
            
        Returns:
            str: Rendered HTML email
        """
        template_path = os.path.join(EmailTemplateRenderer.TEMPLATE_DIR, template_name)
        
        # Add default values
        data.setdefault('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data.setdefault('portal_url', 'https://prosite.com/portal')
        data.setdefault('dashboard_url', 'https://prosite.com/dashboard')
        
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace all placeholders
        for key, value in data.items():
            placeholder = '{{' + key + '}}'
            template = template.replace(placeholder, str(value))
        
        return template
    
    @staticmethod
    def render_test_failure(batch_number, test_date, age_days, project_name, location, 
                           test_results, doc_ref):
        """Render concrete test failure email"""
        
        # Build test results table rows
        rows_html = ''
        for result in test_results:
            status_class = 'fail' if result['status'] == 'FAIL' else 'pass'
            rows_html += f'''
                <tr>
                    <td>{result['cube_id']}</td>
                    <td><strong>{result['strength']}</strong></td>
                    <td>{result['required']}</td>
                    <td class="{status_class}">{result['status']}</td>
                </tr>
            '''
        
        data = {
            'batch_number': batch_number,
            'test_date': test_date,
            'age_days': age_days,
            'project_name': project_name,
            'location': location,
            'test_results_rows': rows_html,
            'doc_ref': doc_ref,
        }
        
        return EmailTemplateRenderer.render_template('test_failure.html', data)
    
    @staticmethod
    def render_batch_rejection(batch_number, delivery_date, supplier_name, volume, 
                               project_name, rejected_by, rejection_reason, 
                               mix_design, slump_required, slump_actual, temperature, ncr_ref):
        """Render batch rejection email"""
        
        data = {
            'batch_number': batch_number,
            'delivery_date': delivery_date,
            'supplier_name': supplier_name,
            'volume': volume,
            'project_name': project_name,
            'rejected_by': rejected_by,
            'rejection_reason': rejection_reason,
            'mix_design': mix_design,
            'slump_required': slump_required,
            'slump_actual': slump_actual,
            'temperature': temperature,
            'ncr_ref': ncr_ref,
        }
        
        return EmailTemplateRenderer.render_template('batch_rejection.html', data)
    
    @staticmethod
    def render_safety_nc(nc_number, date_reported, location, reported_by, category, 
                        severity_level, risk_score, risk_level, description, 
                        immediate_hazards, assigned_to, target_date, status, ncr_ref):
        """Render safety non-conformance email"""
        
        severity_class_map = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        
        data = {
            'nc_number': nc_number,
            'date_reported': date_reported,
            'location': location,
            'reported_by': reported_by,
            'category': category,
            'severity_level': severity_level,
            'severity_class': severity_class_map.get(severity_level.upper(), 'medium'),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'description': description,
            'immediate_hazards': immediate_hazards,
            'assigned_to': assigned_to,
            'target_date': target_date,
            'status': status,
            'ncr_ref': ncr_ref,
        }
        
        return EmailTemplateRenderer.render_template('safety_nc.html', data)
    
    @staticmethod
    def render_password_reset(user_name, reset_link, expiry_hours=1):
        """
        Render password reset request email
        
        Args:
            user_name (str): Full name of user
            reset_link (str): Complete URL with reset token
            expiry_hours (int): Hours until link expires (default: 1)
            
        Returns:
            str: Rendered HTML email
        """
        data = {
            'USER_NAME': user_name,
            'RESET_LINK': reset_link,
            'EXPIRY_HOURS': str(expiry_hours),
        }
        
        return EmailTemplateRenderer.render_template('password_reset.html', data)
    
    @staticmethod
    def render_password_reset_confirmation(user_name, reset_time):
        """
        Render password reset confirmation email
        
        Args:
            user_name (str): Full name of user
            reset_time (str): Timestamp when password was reset
            
        Returns:
            str: Rendered HTML email
        """
        data = {
            'USER_NAME': user_name,
            'RESET_TIME': reset_time,
        }
        
        return EmailTemplateRenderer.render_template('password_reset_confirmation.html', data)
