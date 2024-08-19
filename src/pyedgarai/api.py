import flask 
from pyedgarai import clean_account_name, get_xbrl_frames, get_company_concept
app = flask.Flask(__name__)

# endpoint for account 
@app.route('/account', methods=['GET'])
def account():
    # retrieve units and account 
    units = flask.request.args.get('units')
    account = flask.request.args.get('account')
    frame = "CY2024Q1"

    account = clean_account_name(account)
    taxonomy = "us-gaap"
    frames = get_xbrl_frames(taxonomy, account, units, frame)
    return flask.jsonify(frames)

@app.route('/company', methods=['GET'])
def company():
    # wrap get_company_concept(cik: int, taxonomy: str, tag: str)
    cik = flask.request.args.get('cik')
    # to int 
    cik = int(cik)
    taxonomy = 'us-gaap'
    tag = flask.request.args.get('tag')
    return flask.jsonify(get_company_concept(cik, taxonomy, tag))

# test e.g. using 0000320193 and Income Tax Expense (Benefit)
# http://localhost:5000/company?cik=320193&tag=IncomeTaxExpenseBenefit

# test e.g. using GrossProfit and USD
# http://localhost:5000/account?units=USD&account=GrossProfit

if __name__ == '__main__':
    app.run(debug=True)