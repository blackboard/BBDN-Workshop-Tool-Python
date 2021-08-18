import os
import pprint
import urllib
import uuid
from tempfile import mkdtemp

from flask import Flask, render_template
from flask import redirect, request
from flask_caching import Cache
from flask_login import login_required
from pylti1p3.contrib.flask import FlaskMessageLaunch, FlaskOIDCLogin, FlaskRequest, FlaskCacheDataStorage
from pylti1p3.tool_config import ToolConfJsonFile

import Config
from RestAuthContoller import RestAuthController

## TODO

PAGE_TITLE = 'Title'


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask('LTI-Workshop', template_folder='templates', static_folder='static')

app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config.from_mapping(Config.config)

cache = Cache(app)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


class ExtendedFlaskMessageLaunch(FlaskMessageLaunch):

    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just skip nonce validation.
        """
        iss = self.get_iss()
        deep_link_launch = self.is_deep_link_launch()
        if iss == "http://imsglobal.org" and deep_link_launch:
            return self
        return super(ExtendedFlaskMessageLaunch, self).validate_nonce()


def get_lti_config_path():
    return os.path.join(app.root_path, 'lti.json')


def get_launch_data_storage():
    return FlaskCacheDataStorage(cache)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    launch_data_storage = get_launch_data_storage()

    flask_request = FlaskRequest()
    target_link_uri = flask_request.get_param('target_link_uri')

    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')

    oidc_login = FlaskOIDCLogin(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    return oidc_login \
        .enable_check_cookies() \
        .redirect(target_link_uri)


@app.route('/launch/', methods=['HEAD', 'GET', 'POST'])
def launch():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    pprint.pprint(message_launch_data)
    tpl_kwargs = {
        'page_title': PAGE_TITLE,
        'is_deep_link_launch': message_launch.is_deep_link_launch(),
        'launch_data': message_launch.get_launch_data(),
        'launch_id': message_launch.get_launch_id(),
        'curr_user_name': message_launch_data.get('name', '')
    }

    learn_url = message_launch_data['https://purl.imsglobal.org/spec/lti/claim/tool_platform']['url'].rstrip('/')

    # Get the value of the one time session token from the LTI claim
    one_time_session_token = message_launch_data['https://blackboard.com/lti/claim/one_time_session_token']

    # If there is no comma in the value, we've hit the bug. Add it and the user's UUID
    if "," not in one_time_session_token:
        one_time_session_token += "," + message_launch_data['sub']

    # TODO We need to make LTI launch data available to the REST application below. Maybe make
    # the state equal to the launchID that has the cached launch data? Is that bad form?

    # Add the one_time_session_cookie to the query parameters to send to the Authorization Code endpoint
    params = {
        'redirect_uri': Config.config['SERVER_NAME'] + '/authcode/',
        'response_type': 'code',
        'client_id': Config.config['LEARN_REST_KEY'],
        'one_time_session_token': one_time_session_token,
        'scope': '*',
        'state': str(uuid.uuid4())
    }

    encodedParams = urllib.parse.urlencode(params)

    get_authcode_url = learn_url + '/learn/api/public/v1/oauth2/authorizationcode?' + encodedParams

    print("authcode_URL: " + get_authcode_url)

    return (redirect(get_authcode_url))


@app.route('/authcode/', methods=['GET', 'POST'])
def authcode():
    authcode = request.args.get('code', '')
    state = request.args.get('state', '')
    print(authcode)

    restAuthController = RestAuthController.RestAuthController(authcode)
    restAuthController.setToken()
    token = restAuthController.getToken()
    uuid = restAuthController.getUuid()


    # TODO Implement REST call to get course created date, add it and data from launch to kwargs


    tp_kwargs = {
        'title': PAGE_TITLE,
    }

    return render_template('index.html', **tp_kwargs)

if __name__ == '__main__':
    restAuthController = None
    app.run(host='0.0.0.0', port=5000)
