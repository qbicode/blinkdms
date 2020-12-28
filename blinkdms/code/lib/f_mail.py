'''

- in start.py

from flask_mail import Mail

# email server, due to miguelgrinberg.com
MAIL_SERVER = 'localhost'
MAIL_USE_TLS = False
MAIL_USE_SSL = False
app.config.from_object(__name__)

mail = Mail(app) # due to miguelgrinberg.com

'''

from flask import session
from flask_mail import Message
import urllib.parse
from flask import render_template
from flask import request

from start import mail
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.f_utilities import BlinkError

class MailMain:
    '''
    send mail kann durch user komplett abgeschalten werden (via USER_PREF)
    '''

    def send_email_active(self):
        '''
        system allows sending emails ? 0,1
        '''
        return session['globals'].get('email.send.allow',0)

    def send_mail(self, to_email, user_fullname, subject, meta_content, htmlfile):
        '''
        :param meta_content: dict, will be merged by this method
            e.g. meta_content['reset.url'] = '....'
            reset_url   = base_url+'?mod=doc_edit&cid=...&token='+ urllib.parse.quote(token)
        :param  htmlfile: 'email/p_reset.html'
        '''

        debug.printx(__name__, "Send email to: user: "+user_fullname+" email:" + str(to_email) + ' SUBJECT:' + subject)

        if to_email == '':
            raise BlinkError(1, "No email given.")

        system_name = session['globals'].get('site.title', 'system')
        company = session['globals'].get('system.company', 'Company')
        admin_email = session['globals'].get('admin.email','info@blink-dx.com')
        base_url    = request.base_url

        
        meta_content['site.url'] = base_url
        meta_content['user.fullname'] = user_fullname
        meta_content['site.title'] = system_name

        meta_content['company.url'] = session['globals'].get('company.url', '')
        
        if not session['globals'].get('email.send.allow',0):
            return

        # TBD: check template exists
        message = render_template(htmlfile, meta=meta_content )
        
        msg = Message(subject, sender=admin_email, recipients=[to_email])
        msg.body = message
        msg.html = message
        mail.send(msg)