from django.http import HttpResponse, Http404, JsonResponse
from django.template.loader import get_template
from django.shortcuts import render, render_to_response, redirect
from django.template import loader
import pickle, HTMLParser, os, random
from settings import BASE_DIR, BASE_ROOT, SITE_ROOT, SCRIPT_ROOT, DATA_DIR, STATIC_DIR, DOWNLOAD_DIR
import pandas


def hello(request):
    return HttpResponse("Hello world")


# home page
def home(request):
    t = get_template('home_page.html')
    html = t.render()
    return HttpResponse(html)


# python multiple choice
def mcq_home(request):
    return render_to_response("mcqs_home.html")


html_parser = HTMLParser.HTMLParser()
mcqs_data = pickle.load(open(os.path.join(BASE_DIR, "ourcase/data3.p"), 'rb'))


def mcqs(request, q_no):
    q_no = q_no.encode('utf-8')
    try:
        q_no = int(q_no)
    except:
        raise Http404()

    if q_no in range(1, 689):
        dct = mcqs_data[str(q_no)]
        for key in dct.keys():
            if key != 'code':
                unescaped = html_parser.unescape(dct[key])
                dct.update({key: unescaped})

        request.session['current_q'] = q_no

        return render_to_response("mcqs.html", {'mcq': dct, 'next_q': q_no+1, 'rand_q': random.randint(1,689)})

    else:
        raise Http404()


def test_mcqs(request, q_no):
    if request.method == 'POST':
        if request.session['c_ans'] == request.POST['ans']:
            result = 'correct'
        else:
            result = 'incorrect'

        try:
            request.session['ans_list']
        except KeyError:
            request.session['ans_list'] = []
        if not request.session['ans_list']:
            request.session['ans_list'].append(result)
        elif request.session['ans_list'][-1] == result:
            request.session['ans_list'].append(result)
        else:
            del request.session['ans_list'][:]
            request.session['ans_list'].append(result)

        # print request.session['ans_list']

        return HttpResponse(status=204)

    else:
        q_no = q_no.encode('utf-8')
        try:
            q_no = int(q_no)
        except:
            raise Http404()

        if q_no in range(1, 689):
            dct = mcqs_data[str(q_no)]
            for key in dct.keys():
                if key != 'code':
                    unescaped = html_parser.unescape(dct[key])
                    dct.update({key: unescaped})

            request.session['current_q'] = q_no
            request.session['c_ans'] = dct['ans']

            return HttpResponse(loader.get_template('test_mcqs.html').render(
                {'mcq': dct, 'next_q': q_no + 1, 'rand_q': random.randint(1, 689)}, request))

        else:
            raise Http404()


# plot data online
new = ['Revenue USD Mil', 'Gross Margin %', 'Operating Income USD Mil', 'Operating Margin %',
       'Net Income USD Mil', 'Earnings Per Share USD', 'Dividends USD', 'Payout Ratio %', 'Shares Mil',
       'Book Value Per Share USD', 'Operating Cash Flow USD Mil', 'Cap Spending USD Mil',
       'Free Cash Flow USD Mil', 'Free Cash Flow Per Share USD', 'Working Capital USD Mil',
       'Key Ratios -> Profitability', 'Margins % of Sales', 'Revenue', 'COGS', 'Gross Margin', 'SG&A', 'R&D',
       'Other', 'Operating Margin', 'Net Int Inc & Other', 'EBT Margin', 'Profitability', 'Tax Rate %',
       'Net Margin %', 'Asset Turnover (Average)', 'Return on Assets %', 'Financial Leverage (Average)',
       'Return on Equity %', 'Return on Invested Capital %', 'Interest Coverage', 'Key Ratios -> Growth', 'nan',
       'Revenue %', 'Revenue Year over Year', 'Revenue 3-Year Average', 'Revenue 5-Year Average',
       'Revenue 10-Year Average', 'Operating Income %', 'Operating Income Year over Year',
       'Operating Income 3-Year Average', 'Operating Income 5-Year Average', 'Operating Income 10-Year Average',
       'Net Income %', 'Net Income Year over Year', 'Net Income 3-Year Average', 'Net Income 5-Year Average',
       'Net Income 10-Year Average', 'EPS %', 'EPS Year over Year', 'EPS 3-Year Average', 'EPS 5-Year Average',
       'EPS 10-Year Average', 'Key Ratios -> Cash Flow', 'Cash Flow Ratios', 'Operating Cash Flow Growth % YOY',
       'Free Cash Flow Growth % YOY', 'Cap Ex as a % of Sales', 'Free Cash Flow/Sales %',
       'Free Cash Flow/Net Income', 'Key Ratios -> Financial Health', 'Balance Sheet Items (in %)',
       'Cash & Short-Term Investments', 'Accounts Receivable', 'Inventory', 'Other Current Assets',
       'Total Current Assets', 'Net PP&E', 'Intangibles', 'Other Long-Term Assets', 'Total Assets',
       'Accounts Payable', 'Short-Term Debt', 'Taxes Payable', 'Accrued Liabilities',
       'Other Short-Term Liabilities', 'Total Current Liabilities', 'Long-Term Debt',
       'Other Long-Term Liabilities', 'Total Liabilities', "Total Stockholders' Equity",
       'Total Liabilities & Equity', 'Liquidity/Financial Health', 'Current Ratio', 'Quick Ratio',
       'Financial Leverage', 'Debt/Equity', 'Key Ratios -> Efficiency Ratios', 'Efficiency',
       'Days Sales Outstanding', 'Days Inventory', 'Payables Period', 'Cash Conversion Cycle',
       'Receivables Turnover', 'Inventory Turnover', 'Fixed Assets Turnover', 'Asset Turnover']


def pdo(request):
    return HttpResponse(get_template('pdo.html').render())


def json_receive(request):
    json_dict = {}
    if request.method == "POST":
        com_code_lst = [i.encode('utf-8') for i in request.POST.values()]
        df_list = [reset_index(
            pandas.read_csv("http://financials.morningstar.com/ajax/exportKR2CSV.html?t=" + com_code, skiprows=2,
                            index_col=0, thousands=',', na_values=["0"])) for com_code in com_code_lst]
        for i in range(len(com_code_lst)):
            json_dict.update({com_code_lst[i]: df_list[i].to_json(orient='index')})
    return JsonResponse(json_dict)


def reset_index(df):
    try:                # TODO add more validation
        df.ix['Revenue USD Mil']        # to validate df that is in usd
    except KeyError:
        raise KeyError          # TODO add self-defined error
    else:
        df.insert(len(df.columns), 'new_index', new)
        df = df.set_index('new_index')
        return df


# wechat server
from django.views.decorators.csrf import csrf_exempt
import hashlib, re, time, json, random
from django.utils.encoding import smart_str


WEIXIN_TOKEN = '12578ssdga256a'


class GfycatUrl(str):
    """get the download url by using gfycat id as input"""
    def __init__(self, gfycat_id):
        super(GfycatUrl, self).__init__(gfycat_id)
        if type(gfycat_id) is str:
            self.data = gfycat_id
        else:
            raise TypeError

    def get_thumb_v(self):
        return "https://thumbs.gfycat.com/"+self.data+"-mobile.mp4"

    def get_thumb_c(self):
        return "https://thumbs.gfycat.com/"+self.data+"-mobile.jpg"

    def get_giant_v(self):
        return "https://giant.gfycat.com/"+self.data+".mp4"

    def get_giant_c(self):
        return "https://giant.gfycat.com/" + self.data + ".jpg"


def logging_python_quest(msg):
    import datetime
    with open('/home/rc/PySites/ourcase/Data/python_quest_log.txt', 'a') as pql:
        pql.write(str(datetime.datetime.now().date())+'\t'+msg+'\n')


@csrf_exempt
def wechat_test(request):
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin  index")
    else:
        xml_str = smart_str(request.body)
        logging_python_quest(xml_str)   # delete in the future
        if re.findall(r'(<MsgType><!\[CDATA\[)(.*)(]]></MsgType>)', xml_str)[0][1] == 'text':
            return HttpResponse(wechat_process_text(xml_str))
        else:
            return HttpResponse('success')


def wechat_process_text(text_received):
    toUser = re.findall(r'(<FromUserName><!\[CDATA\[)(.*)(]]></FromUserName>)', text_received)[0][1]
    fromUser = re.findall(r'(<ToUserName><!\[CDATA\[)(.*)(]]></ToUserName>)', text_received)[0][1]
    CreateTime = str(int(time.time()))
    requested_content = re.findall(r'(<Content><!\[CDATA\[)(.*)(]]></Content>)', text_received)[0][1]
    requested_content = requested_content.strip()
    if requested_content.isalpha():
        requested_content = requested_content.lower()
    if requested_content == 'smm':
        with open('/home/rc/PySites/ourcase/Data/smm_price_daily', 'r') as k:
            smm_price = json.load(k).values()[0][1]
        msg = str(smm_price)
    elif requested_content.startswith('hl'):
        msg = get_highlight(requested_content)
    else:
        msg = "msg get"
    return "<xml><ToUserName><![CDATA[" + toUser + "]]></ToUserName><FromUserName><![CDATA[" + fromUser + "]]></FromUserName><CreateTime>" + CreateTime + "</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[" + msg + "]]></Content></xml>"


def get_highlight(rq_text):
    p = open(DATA_DIR+"gfycat_hl",'r')
    d = json.load(p)
    text2r = ''
    if rq_text == 'hl':
        for item in d.values():
            text2r += item[0] + " \n" + GfycatUrl(item[1].encode('utf-8')).get_thumb_v() + '\n\n'
        return text2r
    elif rq_text == 'hl -ad':
        return GfycatUrl(random.choice(d.values())[1].encode('utf-8'))
    else:
        return 'Unknown Command'


# wechat ow hightlights
def wechat_owhl(requests):
    return HttpResponse(get_template('ow_hl_base.html').render())