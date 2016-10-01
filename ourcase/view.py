from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render, render_to_response
from django.template import loader
import pickle, HTMLParser, os, random
from settings import BASE_DIR


def hello(request):
    return HttpResponse("Hello world")


def home(request):
    t = get_template('home_page.html')
    html = t.render()
    return HttpResponse(html)


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