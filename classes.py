# encoding: utf-8


# Question类，其中一道题就是一个对象，包含输入的:
# 调号：String输入（降号显示b）
# 拍号：String输入，格式（’4/4‘）
# 首个和弦（四个音，时值，在一个list中）
# 所有和弦（级数，转位，悬疑，和附属和弦），每个和弦作为一个字典，再放在一个List中，一共7个元素

class Questions(object):

    def __init__(self, keySign='', timeSign='',
                 firstChord=['','','','',''],
                 chordsInfo=[{},{},{},{},{},{},{}],
                 bigError=[]):
        self.keySign = keySign
        self.timeSign = timeSign
        self.firstChord = firstChord
        # chordsInfo是一个list含有7个字典
        self.chordsInfo = chordsInfo
        # error属性，默认为空，在计算时遇到错误则添加
        self.bigError = bigError

# Sample question initiation

question0 = Questions(
    keySign = 'F',
    timeSign = '2/2',
    firstChord = ['F2','C4','F4','A4','half'],
    chordsInfo = [
        {
            'chord': '1',
            'inversion': '',
            'suspension': '',
            'secondary': ''
        },{
            'chord': '2',
            'inversion': '65',
            'suspension': '',
            'secondary': ''
        },{
            'chord': '5',
            'inversion': '',
            'suspension': '',
            'secondary': ''
        },{
            'chord': '6',
            'inversion': '',
            'suspension': '',
            'secondary': ''
        },{
            'chord': '5',
            'inversion': '7',
            'suspension': '',
            'secondary': '5'
        },{
            'chord': '5',
            'inversion': '',
            'suspension': '',
            'secondary': ''
        },{
            'chord': '1',
            'inversion': '',
            'suspension': '',
            'secondary': ''
        }
    ]
)