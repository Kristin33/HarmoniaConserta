# encoding: utf-8

from music21 import *
import itertools
import copy

#########################################################################
# 大错误
#########################################################################


# （加入根音一起）检查这个和弦是否合理：
# 不考虑省略五音的情况，检查一个和弦中是否有三个不同的音
# 导音不能重复，64和弦必须重复底音
# 关于导音所在的调，引用一个调，一般输入全局变量
def checkValidChord(thisChord, inv, key):
    # 和弦要有三个不同的音
    if (len({x.name for x in thisChord}) < 3):
        return False
    # 重复导音
    l = key.getLeadingTone()
    if (len([x for x in thisChord if x.name==l.name]) > 1):
        return False
    # 64和弦重复底音
    if inv == 64:
        if (len([x for x in thisChord if x.name==thisChord.pitches[0].name]) != 2):
            return False
    return True


# 检查上方三个声部之间有没有隔开八度以上
def checkUpperIntervals(thisChord):
    if (abs(interval.Interval(thisChord.pitches[1],thisChord.pitches[2]).semitones) >= 12 or
            abs(interval.Interval(thisChord.pitches[2], thisChord.pitches[3]).semitones) >= 12):
        return False
    else:
        return True

# 对比前面的声部，有没有越界
def checkOverlapping(thisChord, preChord):
    if (thisChord.pitches[1] < preChord.pitches[0] or
            thisChord.pitches[1] > preChord.pitches[2] or
            thisChord.pitches[2] < preChord.pitches[1] or
            thisChord.pitches[2] > preChord.pitches[3] or
            thisChord.pitches[3] < preChord.pitches[2] ):
        return False
    return True

# 检查有没有出现平行/相反的五度和八度，以及平行Unison
def checkFifthOctave(thisChord, preChord):
    # 检查prechord的六个音程，如果里面有五度或八度，则相应检查新和弦是否也是五度或八度
    for i in range(0,4):
        for j in range(i+1,4):
            intv = interval.Interval(preChord.pitches[i],preChord.pitches[j])
            if intv.directedSimpleName == 'P5':
                if interval.Interval(thisChord.pitches[i],thisChord.pitches[j]).directedSimpleName == "P5":
                    return False
            if intv.directedSimpleName == 'P8':
                if interval.Interval(thisChord.pitches[i],thisChord.pitches[j]).directedSimpleName == "P8":
                    return False
            if intv.directedSimpleName == 'P1':
                if interval.Interval(thisChord.pitches[i],thisChord.pitches[j]).directedSimpleName == "P1":
                    return False
    return True


# 检查从前一个和弦过过来有没有出现不和谐的leap：
# 增二度，减五度，或是leap五度以上
def checkBadLeap(thisChord, preChord):
    for i in range(1,4):
        intv = interval.Interval(preChord.pitches[i],thisChord.pitches[i])
        if abs(intv.semitones) > 7:
            return False
        if abs(intv.semitones) == 6:
            return False
        # 增二度：由于限制太多，这个被移入小错误中
        # if abs(intv.semitones) == 3:
        #     return False
    return True


#########################################################################
# 小错误: 返回要扣的分数，1至3
#########################################################################

# 如果前一个和弦是64和弦，检查6音和4音有没有step向下解决
# 如果前一个和弦是7和弦，检查7音有没有step解决
def checkResolution(thisChord, preChord, inv):
    tmp = 0
    if inv == 64 :
        # 获取6音和4音在前和弦中的位置
        i6 = preChord.pitches.index(preChord.third)
        i4 = preChord.pitches.index(preChord.root())
        intv6 = interval.Interval(preChord.pitches[i6],thisChord.pitches[i6])
        intv4 = interval.Interval(preChord.pitches[i4],thisChord.pitches[i4])
        if (intv6.semitones != -2 or intv6.semitones != -1 or
                intv4.semitones != -2 or intv4.semitones != -1):
            tmp += 4
    if inv == 7 or inv == 65 or inv == 43 or inv ==42 :
        # 获取7音在前和弦中的位置
        i7 = preChord.pitches.index(preChord.seventh)
        intv7 = interval.Interval(preChord.pitches[i7],thisChord.pitches[i7])
        if (abs(intv7.semitones) > 2):
            tmp += 4
    return tmp


# 检查上方三个声部的走向，有一个leap则扣一分
# 如果有增二度leap，则再扣一分
def checkLeaps(thisChord, preChord):
    tmp = 0
    intv1 = interval.Interval(preChord[1], thisChord[1])
    intv2 = interval.Interval(preChord[2], thisChord[2])
    intv3 = interval.Interval(preChord[3], thisChord[3])
    if abs(intv1.semitones) >= 3:
        tmp += 1
        if abs(intv1.semitones) == 3: tmp += 1
    if abs(intv2.semitones) >= 3:
        tmp += 1
        if abs(intv2.semitones) == 3: tmp += 1
    if abs(intv3.semitones) >= 3:
        tmp += 1
        if abs(intv1.semitones) == 3: tmp += 1
    return tmp


# 如果出现了Unequal Fifths，即d5-P5，则扣1分
def checkUnequalFifths(thisChord, preChord):
    # 检查本和弦的所有六个音程
    for i in range(0,4):
        for j in range(i+1,4):
            intv = interval.Interval(thisChord.pitches[i], thisChord.pitches[j])
            # 如果这个音程是纯五度
            if intv.directedSimpleName == 'P5':
                preIntv = interval.Interval(preChord.pitches[i], preChord.pitches[j])
                # 如果前一和弦的这个音程是减五度
                if preIntv.directedSimpleName == 'd5':
                    return 2
    return 0


# 检查对于最外两个声部是否有Hidden或Direct五度：(有则先扣1分)
# 同向运动达到五度，如果高声部跳进则扣两分
def checkHDFifths(thisChord, preChord):
    tmp = 0
    intv = interval.Interval(thisChord.pitches[0],thisChord.pitches[3])
    # 是否在外声部达到了五度
    if intv.directedSimpleName == 'P5':
        tmp += 1
        intv1len = interval.Interval(preChord.pitches[0], thisChord.pitches[0]).semitones
        intv2len = interval.Interval(preChord.pitches[3], thisChord.pitches[3]).semitones
        # 是否同向行走
        if (intv1len>0 and intv2len>0) or (intv1len<0 and intv2len<0):
            # 高声部是否跳进
            if abs(intv2len) > 3 :
                tmp += 2
    return tmp


# 这个功能目前似乎不work
# 使用music21定义的功能，检查所有六个音程，如果前一个和弦
# 有不和谐音程（P4, d5, A4, or m7）而没有解决，则扣1分
def checkProperResolution(thisChord, preChord):
    tmp = 0
    for i in range(0,4):
        for j in range(i,4):
            n1 = pitch.Pitch(preChord.pitches[j])
            n2 = pitch.Pitch(thisChord.pitches[j])
            m1 = pitch.Pitch(preChord.pitches[i])
            m2 = pitch.Pitch(thisChord.pitches[i])
            vl = voiceLeading.VoiceLeadingQuartet(n1,n2,m1,m2)
            if vl.isProperResolution == False:
                tmp += 1
    return tmp


# 如果7和弦的7音是被向下跳进连接的，则扣2分
def checkc7DecendingLeap(thisChord, preChord):
    # 如果该和弦是7和弦
    if thisChord.containsSeventh():
        # 得到7音的位置
        i = thisChord.pitches.index(thisChord.seventh)
        intv = interval.Interval(preChord.pitches[i], thisChord.pitches[i])
        if intv.semitones < -3:
            return 2
    return 0


