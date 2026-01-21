# -*- coding: utf-8 -*-
"""Test SSL fix for corporate environments"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_slack_ssl():
    print('Testing Slack webhook with SSL fix...')
    webhook_url = 'https://hooks.slack.com/services/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'
    message = {
        'text': 'SSL Fix Test - Monitor Portable funcionando correctamente en servidor corporativo',
        'username': 'Security Monitor',
        'icon_emoji': ':white_check_mark:'
    }

    try:
        # First try with SSL verification
        response = requests.post(webhook_url, json=message, timeout=10)
        print(f'SSL Normal - Status: {response.status_code}')
        if response.status_code == 200:
            print('EXITO: SSL normal funcionando')
            return True
        else:
            raise Exception('SSL normal failed')
    except Exception as e:
        print(f'SSL normal fallo: {e}')
        print('Intentando sin verificacion SSL...')
        try:
            response = requests.post(webhook_url, json=message, timeout=10, verify=False)
            print(f'SSL Deshabilitado - Status: {response.status_code}')
            print(f'Response: {response.text}')
            if response.status_code == 200:
                print('EXITO: Webhook funcionando con SSL deshabilitado')
                return True
            else:
                print('ERROR: Webhook fallo incluso con SSL deshabilitado')
                return False
        except Exception as e2:
            print(f'ERROR: {e2}')
            return False

if __name__ == "__main__":
    success = test_slack_ssl()
    print(f"\nResultado final: {'EXITO' if success else 'FALLO'}")