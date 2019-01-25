# grading.py
import cgi
import time
import sys
import json
import traceback
import pdb
from collections import defaultdict
import util

class Grades:

  def __init__(self, projectName, questionsAndMaxesList,
               gsOutput=False, edxOutput=False, muteOutput=False):
    """
   Bir projenin derecelendirme şemasını tanımlar
       projectName: proje adı
       questionsAndMaxesDict: (soru adı, soru başına maksimum puan) listesi
    """
    self.questions = [el[0] for el in questionsAndMaxesList]
    self.maxes = dict(questionsAndMaxesList)
    self.points = Counter()
    self.messages = dict([(q, []) for q in self.questions])
    self.project = projectName
    self.start = time.localtime()[1:6]
    self.sane = True
    self.currentQuestion = None
    self.edxOutput = edxOutput
    self.gsOutput = gsOutput
    self.mute = muteOutput
    self.prereqs = defaultdict(set)

    print 'başlangıç on %d-%d at %d:%02d:%02d' % self.start

  def addPrereq(self, question, prereq):
    self.prereqs[question].add(prereq)

  def grade(self, gradingModule, exceptionMap = {}, bonusPic = False):

    completedQuestions = set([])
    for q in self.questions:
      print '\nQuestion %s' % q
      print '=' * (9 + len(q))
      print
      self.currentQuestion = q

      incompleted = self.prereqs[q].difference(completedQuestions)
      if len(incompleted) > 0:
          prereq = incompleted.pop()
          print \
% (prereq, q, q, prereq)
          continue

      if self.mute: util.mutePrint()
      try:
        util.TimeoutFunction(getattr(gradingModule, q),1800)(self)
      except Exception, inst:
        self.addExceptionMessage(q, inst, traceback)
        self.addErrorHints(exceptionMap, inst, q[1])
      except:
        self.fail('FAIL: Bir dizgi istisnası ile sonlandırıldı.')
      finally:
        if self.mute: util.unmutePrint()

      if self.points[q] >= self.maxes[q]:
        completedQuestions.add(q)

      print ('\n### Question %s: %d/%d ###\n' % (q, self.points[q], self.maxes[q]))


    print ('\nFinished at %d:%02d:%02d' % time.localtime()[3:6])
    print ("\nProvisional grades\n==================")

    for q in self.questions:
      print ('Question %s: %d/%d' % (q, self.points[q], self.maxes[q]))
    print ('------------------')
    print ('Total: %d/%d' % (self.points.totalCount(), sum(self.maxes.values())))
    if bonusPic and self.points.totalCount() == 25:
       """

                  

                  ---      ----      ---
                  |  \    /  + \    /  |
                  | + \--/      \--/ + |
                  |   +     +          |
                  | +     +        +   |
                @@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              V   \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@
                   \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@
                    V     @@@@@@@@@@@@@@@@@@@@@@@@
                            @@@@@@@@@@@@@@@@@@@@@@
                    /\      @@@@@@@@@@@@@@@@@@@@@@
                   /  \  @@@@@@@@@@@@@@@@@@@@@@@@@
              /\  /    @@@@@@@@@@@@@@@@@@@@@@@@@@@
             /  \ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            /    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@@@@@@@
                    @@@@@@@@@@@@@@@@@@

"""

    if self.edxOutput:
        self.produceOutput()
    if self.gsOutput:
        self.produceGradeScopeOutput()

  def addExceptionMessage(self, q, inst, traceback):

    self.fail('FAIL: Exception raised: %s' % inst)
    self.addMessage('')
    for line in traceback.format_exc().split('\n'):
        self.addMessage(line)

  def addErrorHints(self, exceptionMap, errorInstance, questionNum):
    typeOf = str(type(errorInstance))
    questionName = 'q' + questionNum
    errorHint = ''
    if exceptionMap.get(questionName):
      questionMap = exceptionMap.get(questionName)
      if (questionMap.get(typeOf)):
        errorHint = questionMap.get(typeOf)
    # hata varsa başa dön

    if (exceptionMap.get(typeOf)):
      errorHint = exceptionMap.get(typeOf)

    if not errorHint:
      return ''

    for line in errorHint.split('\n'):
      self.addMessage(line)

  def produceGradeScopeOutput(self):
    out_dct = {}

    # gönderimin toplamı
    total_possible = sum(self.maxes.values())
    total_score = sum(self.points.values())
    out_dct['score'] = total_score
    out_dct['max_score'] = total_possible
    out_dct['output'] = "Total score (%d / %d)" % (total_score, total_possible)
    tests_out = []
    for name in self.questions:
      test_out = {}
      test_out['name'] = name
      test_out['score'] = self.points[name]
      test_out['max_score'] = self.maxes[name]

      is_correct = self.points[name] >= self.maxes[name]
      test_out['output'] = "  Question {num} ({points}/{max}) {correct}".format(
          num=(name[1] if len(name) == 2 else name),
          points=test_out['score'],
          max=test_out['max_score'],
          correct=('X' if not is_correct else ''),
      )
      test_out['tags'] = []
      tests_out.append(test_out)
    out_dct['tests'] = tests_out

    with open('gradescope_response.json', 'w') as outfile:
        json.dump(out_dct, outfile)
    return

  def produceOutput(self):
    edxOutput = open('edx_response.html', 'w')
    edxOutput.write("<div>")

    # birinci
    total_possible = sum(self.maxes.values())
    total_score = sum(self.points.values())
    checkOrX = '<span class="incorrect"/>'
    if (total_score >= total_possible):
        checkOrX = '<span class="correct"/>'
    header = """
        <h3>
            Total score ({total_score} / {total_possible})
        </h3>
    """.format(total_score = total_score,
      total_possible = total_possible,
      checkOrX = checkOrX
    )
    edxOutput.write(header)

    for q in self.questions:
      if len(q) == 2:
          name = q[1]
      else:
          name = q
      checkOrX = '<span class="incorrect"/>'
      if (self.points[q] >= self.maxes[q]):
        checkOrX = '<span class="correct"/>'
      messages = "<pre>%s</pre>" % '\n'.join(self.messages[q])
      output = """
        <div class="test">
          <section>
          <div class="shortform">
            Question {q} ({points}/{max}) {checkOrX}
          </div>
        <div class="longform">
          {messages}
        </div>
        </section>
      </div>
      """.format(q = name,
        max = self.maxes[q],
        messages = messages,
        checkOrX = checkOrX,
        points = self.points[q]
      )
      edxOutput.write(output)
    edxOutput.write("</div>")
    edxOutput.close()
    edxOutput = open('edx_grade', 'w')
    edxOutput.write(str(self.points.totalCount()))
    edxOutput.close()

  def fail(self, message, raw=False):
    self.sane = False
    self.assignZeroCredit()
    self.addMessage(message, raw)

  def assignZeroCredit(self):
    self.points[self.currentQuestion] = 0

  def addPoints(self, amt):
    self.points[self.currentQuestion] += amt

  def deductPoints(self, amt):
    self.points[self.currentQuestion] -= amt

  def assignFullCredit(self, message="", raw=False):
    self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
    if message != "":
      self.addMessage(message, raw)

  def addMessage(self, message, raw=False):
    if not raw:
        if self.mute: util.unmutePrint()
        print ('*** ' + message)
        if self.mute: util.mutePrint()
        message = cgi.escape(message)
    self.messages[self.currentQuestion].append(message)

  def addMessageToEmail(self, message):
    print ("WARNING**** addMessageToEmail is deprecated %s" % message)
    for line in message.split('\n'):
      pass


class Counter(dict):

  def __getitem__(self, idx):
    try:
      return dict.__getitem__(self, idx)
    except KeyError:
      return 0

  def totalCount(self):
    """
    toplamını döndürür
    """
    return sum(self.values())

