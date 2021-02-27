import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from service import login, logout, recommend, register, show, modify_tag, delete, search, handle_new_data
from utils import jinja_filter
from front import news, users, index
from load_utils import LoadUtils
from global_var import TAG_ID_MAP, SESSION_INTERVAL

app = Flask(__name__)
app.secret_key = 'yanfu_investment_news'
app.session_cookie_name = 'yfNews'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['JSON_AS_ASCII'] = False
app.permanent_session_lifetime = datetime.timedelta(seconds=SESSION_INTERVAL)

app.register_blueprint(news.bp_news)
app.register_blueprint(users.bp_users)
app.register_blueprint(index.bp_index)

app.register_blueprint(login.bp_login)
app.register_blueprint(logout.bp_logout)
app.register_blueprint(delete.bp_delete)
app.register_blueprint(search.bp_search)
app.register_blueprint(recommend.bp_recommend)
app.register_blueprint(register.bp_register)
app.register_blueprint(show.bp_show)
app.register_blueprint(jinja_filter.bp_filter)
app.register_blueprint(modify_tag.bp_tag)
app.register_blueprint(handle_new_data.bp_handle_new_data)

scheduler = BackgroundScheduler()
scheduler.add_job(LoadUtils.handle_cache, 'interval', seconds=10, args=[TAG_ID_MAP])
scheduler.start()

app.run(debug=False, host='0.0.0.0')
# app.run(debug=True)
