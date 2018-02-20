# encoding: utf-8

from flask import Flask, render_template, url_for, request, redirect
from music21 import *
import config
from classes import Questions
import demoQuestions
import algorithm

app = Flask(__name__)
app.config.from_object(config)

# 建立全局question1对象，用的是默认参数，都是空值
# 在得到input之后进行修改
# global question1
# question1 = Questions()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/guide/')
def guide_page():
    return render_template('guide.html')

@app.route('/rules/')
def rules_page():
    return render_template('rules.html')


# demo页面，上面放着历届12年的题，用户选择之后，直接创建题目对象
@app.route('/demo/')
def demo_page():
    return render_template('demo.html')


# 用户输入之后，补充question1对象，并且重定向到等待页面
@app.route('/input/', methods=['GET','POST'])
def input_page():
    if request.method == 'GET':
        return render_template('input.html')
    # 用POST方法从用户那里得到数据，创建全局inputq对象
    # 重定向到show_page, 传入"input"值
    elif request.method == 'POST':
        global inputq
        inputq = Questions()
        inputq.keySign = request.form.get('keySign')
        inputq.timeSign = '4/4'
        # 第一个和弦的四个音（可以乱序），以及时值
        inputq.firstChord[0] = request.form.get('firstChord1')
        inputq.firstChord[1] = request.form.get('firstChord2')
        inputq.firstChord[2] = request.form.get('firstChord3')
        inputq.firstChord[3] = request.form.get('firstChord4')
        inputq.firstChord[4] = 'quarter'
        # 7个和弦，每一个和弦四个属性
        inputq.chordsInfo[0]['chord'] = request.form.get('chord1')
        inputq.chordsInfo[0]['inversion'] = request.form.get('chord1inv')
        inputq.chordsInfo[0]['suspension'] = request.form.get('chord1sus')
        inputq.chordsInfo[0]['secondary'] = request.form.get('chord1sec')
        inputq.chordsInfo[1]['chord'] = request.form.get('chord2')
        inputq.chordsInfo[1]['inversion'] = request.form.get('chord2inv')
        inputq.chordsInfo[1]['suspension'] = request.form.get('chord2sus')
        inputq.chordsInfo[1]['secondary'] = request.form.get('chord2sec')
        inputq.chordsInfo[2]['chord'] = request.form.get('chord3')
        inputq.chordsInfo[2]['inversion'] = request.form.get('chord3inv')
        inputq.chordsInfo[2]['suspension'] = request.form.get('chord3sus')
        inputq.chordsInfo[2]['secondary'] = request.form.get('chord3sec')
        inputq.chordsInfo[3]['chord'] = request.form.get('chord4')
        inputq.chordsInfo[3]['inversion'] = request.form.get('chord4inv')
        inputq.chordsInfo[3]['suspension'] = request.form.get('chord4sus')
        inputq.chordsInfo[3]['secondary'] = request.form.get('chord4sec')
        inputq.chordsInfo[4]['chord'] = request.form.get('chord5')
        inputq.chordsInfo[4]['inversion'] = request.form.get('chord5inv')
        inputq.chordsInfo[4]['suspension'] = request.form.get('chord5sus')
        inputq.chordsInfo[4]['secondary'] = request.form.get('chord5sec')
        inputq.chordsInfo[5]['chord'] = request.form.get('chord6')
        inputq.chordsInfo[5]['inversion'] = request.form.get('chord6inv')
        inputq.chordsInfo[5]['suspension'] = request.form.get('chord6sus')
        inputq.chordsInfo[5]['secondary'] = request.form.get('chord6sec')
        inputq.chordsInfo[6]['chord'] = request.form.get('chord7')
        inputq.chordsInfo[6]['inversion'] = request.form.get('chord7inv')
        inputq.chordsInfo[6]['suspension'] = request.form.get('chord7sus')
        inputq.chordsInfo[6]['secondary'] = request.form.get('chord7sec')
        # 重定向到等待页面
        return redirect(url_for('show_page', i='input'))


@app.route('/show/<i>')
def show_page(i):
    # solution 是直接输入到VF中进行画图的，格式：
    # key: ‘e/5’, 音名中的降号要改为b， Duration：‘q’ 或‘h’
    # 数据列表中只需要第一个和弦和最后一个和弦的长度: ‘v1n1Dur’, 'v1n7Dur'

    global question1
    question1 = Questions()

    # question1是题目，具体是什么根据输入i判定：如果是input，那就输入input
    if i == 'input':
        question1 = inputq
    if i == '2002': question1 = demoQuestions.q2002
    if i == '2003': question1 = demoQuestions.q2003
    if i == '2006': question1 = demoQuestions.q2006
    if i == '2007': question1 = demoQuestions.q2007
    if i == '2009': question1 = demoQuestions.q2009
    if i == '2010': question1 = demoQuestions.q2010
    if i == '2012': question1 = demoQuestions.q2012
    if i == '2013': question1 = demoQuestions.q2013
    if i == '2014': question1 = demoQuestions.q2014
    if i == '2015': question1 = demoQuestions.q2015


    # 进行计算，返回最终字典, 建立global对象
    global solution1
    # print 'firstchord 2: ' + question1.firstChord[2]
    chordsList = algorithm.findChordList(question1,7)
    if chordsList == []:
        print question1.bigError
        return
    else:
        chordsList = algorithm.addDuration(question1,chordsList)
        # 写入midi文件，以便之后播放
        # s = stream.Stream()
        # for c in chordsList:
        #     s.append(c)
        # mf = midi.translate.streamToMidiFile(s)
        # mf.open(url_for('static', filename='mid/solution.mid'), 'wb')
        # mf.write()
        # mf.close()
        solution1 = algorithm.finalSolution(question1, chordsList)

    return render_template('show.html', solution=solution1)



if __name__ == '__main__':
    app.run()
