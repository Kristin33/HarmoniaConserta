# encoding: utf-8

import algorithm
import demoQuestions

question1 = demoQuestions.q2006

# 进行计算，返回最终字典, 建立global对象
global solution1
# print 'firstchord 2: ' + question1.firstChord[2]
chordsList = algorithm.findChordList(question1,7)
chordsList = algorithm.addDuration(question1,chordsList)
solution1 = algorithm.finalSolution(question1, chordsList)

print chordsList
print solution1