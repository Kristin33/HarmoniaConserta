# encoding: utf-8

from music21 import *
import itertools
import random
import checks
from classes import Questions

# 全局变量，显示问题
global bigError
bigError = []

# 获取调号，拍号等
# global keySign; keySign = question1.keySign
# timeSign = question1.timeSign
# firstChord = question1.firstChord
# global chordsInfo; chordsInfo = question1.chordsInfo

# 确立调性之后，找出音域允许范围（五线谱F3-G5）内所有的调内音，放入列表
# global globalKey
# globalKey = key.Key(keySign)
# global keyNotes
# keyNotes = [str(p) for p in globalKey.getScale().getPitches('F2','G5')]


##########################################################################

# 用户输入的时候降号是取‘b’, 所以要将它变成‘-’
def translateQuestion(question):
    # 调号
    keySign = question.keySign
    if len(keySign) == 2 and keySign[1] == 'b':
        newKeySign = keySign[0] + '-'
        question.keySign = newKeySign
    # 音符
    for x in xrange(0,4):
        thisNote = question.firstChord[x]
        if len(thisNote) == 3 and thisNote[1] == 'b':
            newThisNote = thisNote[0] + '-' + thisNote[2]
            question.firstChord[x] = newThisNote
    return question


##########################################################################

# 因为有附属和弦的存在，使用本函数找到附属和弦的调
# 在findBassChord, getAllSols 中会用到
# 返回附属和弦的调,key对象
def findKey(question, thisSec):

    # 先获取本调音阶（因为小调音阶的默认设定是自然而不是和声，故分开讨论
    oldKey = key.Key(question.keySign)
    if oldKey.mode == 'major':
        thisScale = [str(p) for p in oldKey.getScale().getPitches()]
    if oldKey.mode == 'minor':
        sc = scale.HarmonicMinorScale(question.keySign)
        thisScale = [str(p) for p in sc.pitches]

    # 获取附属调的主音
    s = thisScale[thisSec - 1]
    # 根据原调以及功能和弦级数，判断附属调是大调还是小调
    # 原调是大调时第一，四，五级为大
    if oldKey.mode == 'major':
        if thisSec == 2 or thisSec == 3 or thisSec == 6:
            newKey = key.Key(s, 'minor')
        elif thisSec == 1 or thisSec == 4 or thisSec == 5:
            newKey = key.Key(s)
        else:
            question.bigError.append('Error: Requesting secondary chords, '
                                     'but can\'t build new key. \n For example: '
                                     'the seventh scale degree of major key is diminished, '
                                     'the second scale degree of minor key is diminished, '
                                     'the third scale degree of minor key is augmented'
                                     'thus can\'t build secondary key. ')
    # 原调是小调时五级为大
    elif oldKey.mode == 'minor':
        if thisSec == 1 or thisSec == 4 or thisSec == 6 or thisSec == 7:
            newKey = key.Key(s, 'minor')
        elif thisSec == 5:
            newKey = key.Key(s)
        else:
            question.bigError.append('Error: Requesting secondary chords, '
                                     'but can\'t build new key. \n For example: '
                                     'the seventh scale degree of major key is diminished, '
                                     'the second scale degree of minor key is diminished, '
                                     'the third scale degree of minor key is augmented'
                                     'thus can\'t build secondary key. ')

    return newKey


# 返回一个最低位的和弦，并且设置底音
def findBassChord(question, chordNo):

    chordsInfo = question.chordsInfo
    c = []
    thisRoot = int(chordsInfo[chordNo - 1].get('chord'))
    thisInv = int(chordsInfo[chordNo - 1].get('inversion')) if chordsInfo[chordNo - 1].get('inversion') != '' else ''
    thisSec = int(chordsInfo[chordNo - 1].get('secondary')) if chordsInfo[chordNo - 1].get('secondary') != '' else ''

    # 根据是否是附属和弦，判断调性
    if thisSec != '':
        thisKey = findKey(question, thisSec)
    else:
        thisKey = key.Key(question.keySign)

    # 创建音阶和调内音集合：因为小调音阶的默认设定是自然而不是和声，故分开讨论
    if thisKey.mode == 'major':
        keyNotes = [str(p) for p in thisKey.getScale().getPitches('F2', 'G5')]
        thisScale = [str(p) for p in thisKey.getScale().getPitches()]
    if thisKey.mode == 'minor':
        sc = scale.HarmonicMinorScale(question.keySign)
        keyNotes = [str(p) for p in sc.getPitches('F2', 'G5')]
        thisScale = [str(p) for p in sc.pitches]

    # 从chordInfo中获取和弦的根音位置，然后在调音阶中找到该位置，创建音符
    r = pitch.Pitch(thisScale[thisRoot-1])

    # 因为是根音，在允许范围内取最低的八度
    while r.nameWithOctave in keyNotes:
        r.octave -= 1
    r.octave += 1
    # 在音阶中获取根音，并且照推出三音和五音
    i = keyNotes.index(r.nameWithOctave)
    c.extend([keyNotes[i], keyNotes[i+2], keyNotes[i+4]])
    # 根据转位判断根音
    if thisInv == 7 or thisInv == 65 or thisInv == 43 or thisInv == 42:
        c.append(keyNotes[i+6])
        if (thisInv == 7): b = pitch.Pitch(c[0])
        if (thisInv == 65): b = pitch.Pitch(c[1])
        if (thisInv == 43): b = pitch.Pitch(c[2])
        if (thisInv == 42): b = pitch.Pitch(c[3])
    else:
        if (thisInv == ''): b = pitch.Pitch(c[0])
        elif (thisInv == 6): b = pitch.Pitch(c[1])
        elif (thisInv == 64): b = pitch.Pitch(c[2])
        else:
            question.bigError.append('Error: Inversion is not valid: \n'
                                     'valid inversion: 7, 65, 43, 42, 6, 64 or blank input. ')
    # 再把b降到最低
    while b.nameWithOctave in keyNotes:
        b.octave -= 1
    b.octave += 1
    thisChord = chord.Chord(c)
    thisChord.bass(b)
    return thisChord


#############################################################################

# 获得所有可能的和弦排布，返回allSols一个list,里面放着所有可能的和弦(完整和弦包括底音！)
def getAllSols(question, chordNo):

    thisChord = findBassChord(question,chordNo)
    bass = thisChord.bass()
    allSols = []
    # 从问题中先提取所需要的信息
    chordsInfo = question.chordsInfo
    thisSec = int(chordsInfo[chordNo - 1].get('secondary')) if chordsInfo[chordNo - 1].get('secondary') != '' else ''

    # 根据是否是附属和弦，判断调性
    if thisSec != '':
        thisKey = findKey(question, thisSec)
    else:
        thisKey = key.Key(question.keySign)

    # 创建音阶和调内音集合：因为小调音阶的默认设定是自然而不是和声，故分开讨论
    if thisKey.mode == 'major':
        keyNotes = [str(p) for p in thisKey.getScale().getPitches('F2', 'G5')]
    if thisKey.mode == 'minor':
        sc = scale.HarmonicMinorScale(question.keySign)
        keyNotes = [str(p) for p in sc.getPitches('F2', 'G5')]

    # 创建三和弦
    if thisChord.multisetCardinality == 3:
        pitches = [p.name for p in thisChord]
        # 得到每一个音可能的位置，做成列表(在根音之上)
        i = keyNotes.index(thisChord.bass().nameWithOctave)
        allPitches = [x for x in keyNotes[i + 1:] if pitches[0] in x]
        allPitches.extend([x for x in keyNotes[i + 1:] if pitches[1] in x])
        allPitches.extend([x for x in keyNotes[i + 1:] if pitches[2] in x])
        # 从该列表中创建一个三和弦，可以同音重复（unison）(但这样也会造成很多重复！)
        allSols = [chord.Chord(x) for x in itertools.combinations_with_replacement(allPitches, r = 3)]
        for sol in allSols:
            sol.add(bass)
            sol.sortAscending()

    # 当该和弦是7和弦时，我们决定用上全部四个音
    elif thisChord.multisetCardinality == 4:
        # 找到除了底音之外的三个音
        pitches = [p.name for p in thisChord]
        pitches.remove(thisChord.bass().name)
        # 得到每一个音可能的位置，做成列表(在根音之上)
        i = keyNotes.index(thisChord.bass().nameWithOctave)
        p1 = [x for x in keyNotes[i:] if pitches[0] in x]
        p2 = [x for x in keyNotes[i:] if pitches[1] in x]
        p3 = [x for x in keyNotes[i:] if pitches[2] in x]
        # 根据列表排列组合，得到所有可能的和弦排布
        for i in p1:
            for j in p2:
                for k in p3:
                    ii = pitch.Pitch(i)
                    jj = pitch.Pitch(j)
                    kk = pitch.Pitch(k)
                    tmp = chord.Chord([ii,jj,kk])
                    tmp.add(bass)
                    tmp.sortAscending()
                    allSols.append(tmp)

    return allSols


#############################################################################

# rightChord = chord.Chord(['F2','C4','F4','A4'])
# bass = findBassChord(4).bass()
# thisInv = chordsInfo[6-1].get('inversion')
# preInv = chordsInfo[2-2].get('inversion')
# 直接输入某一个和弦，检查是否有大错误
def checkBigMistake(thisChord, preChord, thisInv):
    if checks.checkValidChord(thisChord, thisInv, globalKey):
        print "checkValidChord True"
    else: print "checkValidChord False"
    if checks.checkUpperIntervals(thisChord):
        print "checkUpperIntervals True"
    else: print "checkUpperIntervals False"
    if checks.checkOverlapping(thisChord, preChord):
        print "checkOverlapping True"
    else: "checkOverlapping False"
    if checks.checkFifthOctave(thisChord, preChord):
        print "checkFifthOctave True"
    else: print "checkFifthOctave False"
    if checks.checkBadLeap(thisChord, preChord):
        print "checBadLeap True"
    else: print "checkBadLeap False"



def checkSmallMistake(bass, thisChord, preChord):
    print 'points in checkLeaps: %s' %checks.checkLeaps(thisChord, preChord)
    print 'points in checkUnequalFifths: %s' %checks.checkUnequalFifths(thisChord, preChord)
    print 'points in checkHDFifths: %s' %checks.checkHDFifths(thisChord, preChord)
    # print 'points in checkProperResolution: %s' %checks.checkProperResolution(thisChord, preChord)
    print 'points in checkc7DecendingLeap: %s' %checks.checkc7DecendingLeap(thisChord, preChord)
    return


#############################################################################


# 根据前一个和弦写下一个和弦，返回一个列表，所有没有大错误的写法
def writeNextChord(question, chordNo, preChord):

    chordsInfo = question.chordsInfo

    oldKey = key.Key(question.keySign)
    thisInv = int(chordsInfo[chordNo-1].get('inversion')) if chordsInfo[chordNo - 1].get('inversion') != '' else ''
    thisSec = int(chordsInfo[chordNo-1].get('secondary')) if chordsInfo[chordNo - 1].get('secondary') != '' else ''
    preInv = int(chordsInfo[chordNo-2].get('inversion')) if chordsInfo[chordNo - 2].get('inversion') != '' else ''

    # 获得所有可能排布
    allSols = getAllSols(question, chordNo); newSols = []

    # 筛选出合理和弦（有至少三个音，64和弦重复底音，导音不重复）
    for sol in allSols:
        # 在检查合理和弦的之前一定要引入一个正确的key！因为附属和弦
        if thisSec == '':
            thisKey = oldKey
        else:
            thisKey = findKey(question, thisSec)
        if checks.checkValidChord(sol, thisInv, thisKey):
            newSols.append(sol)
    # 立即将所有可能的和弦换成新的列表
    allSols = newSols; newSols = []

    # 检查和弦上方的音程
    for sol in allSols:
        if checks.checkUpperIntervals(sol):
            newSols.append(sol)
    if newSols == []:
        question.bigError.append('No chord pass the checkUpperIntervals test')
    allSols = newSols; newSols = []

    # 检查和弦与前一个和弦的相对位置，有没有交叉的声部
    for sol in allSols:
        if checks.checkOverlapping(sol, preChord):
            newSols.append(sol)
    if newSols == []:
        question.bigError.append('No chord pass the checkOverlapping test')

    allSols = newSols; newSols = []

    # 检查平行/相对五度/八度
    for sol in allSols:
        if checks.checkFifthOctave(sol, preChord):
            newSols.append(sol)
    if newSols == []:
        question.bigError.append('No chord pass the checkFifthOctave test')
    allSols = newSols;  newSols = []

    # 检查跳跃的时候有无不协和音程
    for sol in allSols:
        if checks.checkBadLeap(sol, preChord):
            newSols.append(sol)
    if newSols == []:
        question.bigError.append('No chord pass the checkBadLeap test')
    allSols = newSols;  newSols = []

    if allSols == []:
        question.bigError.append('Error: there doesn\'t exist solution without big mistakes.')

    return allSols


# 经过小错误的检查，选出列表中小错误最少的和弦，返回列表
def chooseBestChord(allChords, preChord, preInv):
    min = 10
    bestChords = []
    for chord in allChords:
        tmp = 0
        tmp += checks.checkLeaps(chord, preChord)
        tmp += checks.checkUnequalFifths(chord, preChord)
        tmp += checks.checkHDFifths(chord, preChord)
        tmp += checks.checkc7DecendingLeap(chord, preChord)
        tmp += checks.checkResolution(chord, preChord, preInv)
        if tmp == min:
            bestChords.append(chord)
        elif tmp < min:
            bestChords = []
            bestChords.append(chord)
            min = tmp
    return bestChords


# 使用递归，一个个推出和弦！
# 给和弦加上时值，并且写入midi文件
# 返回和弦列表
def findChordList(question, chordNo):

    # 先把question的格式弄对
    question = translateQuestion(question)
    chordsInfo = question.chordsInfo
    preInv = int(chordsInfo[chordNo - 2].get('inversion')) if chordsInfo[chordNo - 2].get('inversion') != '' else ''

    # Base Case: 只求一个和弦，则返回首个和弦
    if chordNo == 1:
        chord1 = chord.Chord(question.firstChord[:4])
        chord1.sortAscending()
        return [chord1]
    else:
        # 得到之前的所有和弦列表
        chordsList = findChordList(question, chordNo-1)
        if chordsList == []:
            return []
        # 列表的最后一个就是最新的和弦，用它来创建新和弦
        preChord = chordsList[-1]
        # 如果chooseBestChord中有不同的高分选择，则随机选一个(如果已经没有选择，报错)
        bestChords = chooseBestChord(writeNextChord(question, chordNo, preChord), preChord, preInv)
        if bestChords == []:
            return []
        newChord = random.choice(bestChords)
        # 新和弦加入列表，返回列表
        chordsList.append(newChord)

        return chordsList


# 添加时值
def addDuration(question, chordsList):
    # 添加时值
    d = duration.Duration(question.firstChord[4])
    # 每一个和弦的时值都跟第一个一样

    for c in chordsList:
        c.duration = d
        # 最后一个和弦的时值是普通的两倍
    chordsList[-1].duration = d.augmentOrDiminish(2)

    return chordsList


# 因为返回了music21格式的和弦，和VF的显示情况并不兼容，所以需要翻译
def finalSolution(question, solution1):

    # 最终答案是一个字典
    translated_sol = {}

    # 用户输入的调号和拍号格式和VF是一样的，直接转入
    keySign = question.keySign
    if '-' in keySign:
        keySign = keySign.replace('-','b')
    timeSign = question.timeSign
    translated_sol['keySign'] = keySign
    translated_sol['timeSign'] = timeSign

    # 对于每一个和弦音：要在中间放入斜杠/，要将降号-变成b
    for x in xrange(0, 7):
        for y in xrange(0, 4):
            name = solution1[x].pitches[y].nameWithOctave

            if '-' in name:
                print name
                name = name.replace('-','b')

            # 加上斜杠
            name = name[:-1] + '/' + name[-1]
            translated_sol['v%sn%sKey' % (4 - y, x + 1)] = name

    # 得到时值，取第一个字母
    translated_sol['v1n1Dur'] = solution1[0].duration.type[0]
    translated_sol['v1n7Dur'] = solution1[6].duration.type[0]

    return translated_sol



#############################################################################


chord2 = chord.Chord(['E-3', 'B-3', 'E-4', 'G4']).sortAscending()
chord3 = chord.Chord(['E-3', 'C4', 'F4', 'A4']).sortAscending()
chord4 = chord.Chord(['D3', 'D4', 'F4', 'B-4']).sortAscending()
chord5 = chord.Chord(['E3', 'C4', 'G4', 'B-4']).sortAscending()
chord6 = chord.Chord(['F2', 'C4', 'F4', 'A4']).sortAscending()





print 'test'