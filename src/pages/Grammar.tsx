import { useState } from 'react';
import { Check, X, RotateCcw, ChevronRight, ChevronLeft, BookOpen, Trophy } from 'lucide-react';

interface GrammarQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

const mockQuestions: GrammarQuestion[] = [
  {
    id: '1',
    question: 'I ___ to school every day.',
    options: ['go', 'goes', 'going', 'went'],
    correctAnswer: 0,
    explanation: '一般现在时，主语是第一人称，动词用原形。',
  },
  {
    id: '2',
    question: 'She ___ a book now.',
    options: ['read', 'reads', 'is reading', 'reading'],
    correctAnswer: 2,
    explanation: '现在进行时，结构是 be + 动词ing。',
  },
  {
    id: '3',
    question: 'They ___ to the park yesterday.',
    options: ['go', 'goes', 'went', 'going'],
    correctAnswer: 2,
    explanation: '一般过去时，动词用过去式。',
  },
  {
    id: '4',
    question: 'We ___ English for two years.',
    options: ['learn', 'learned', 'have learned', 'learning'],
    correctAnswer: 2,
    explanation: '现在完成时，表示过去开始并持续到现在的动作。',
  },
  {
    id: '5',
    question: '___ you like coffee?',
    options: ['Do', 'Does', 'Are', 'Is'],
    correctAnswer: 0,
    explanation: '一般现在时的疑问句，第二人称用助动词 do。',
  },
];

const Grammar = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState<Set<string>>(new Set());

  const currentQuestion = mockQuestions[currentIndex];
  const isAnswered = answeredQuestions.has(currentQuestion.id);
  const progress = Math.round(((currentIndex + (showResult ? 1 : 0)) / mockQuestions.length) * 100);

  const handleAnswer = (index: number) => {
    if (isAnswered) return;
    setSelectedAnswer(index);
    setAnsweredQuestions((prev) => new Set(prev).add(currentQuestion.id));
    if (index === currentQuestion.correctAnswer) {
      setScore(score + 1);
    }
  };

  const nextQuestion = () => {
    setSelectedAnswer(null);
    if (currentIndex < mockQuestions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResult(true);
    }
  };

  const previousQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setSelectedAnswer(null);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setScore(0);
    setShowResult(false);
    setAnsweredQuestions(new Set());
  };

  if (showResult) {
    const percentage = Math.round((score / mockQuestions.length) * 100);
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-3xl p-8 shadow-xl text-center">
            <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Trophy className="w-12 h-12 text-yellow-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">练习完成！</h2>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">正确答案</span>
                <span className="text-2xl font-bold text-green-600">{score}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">总题数</span>
                <span className="text-2xl font-bold text-gray-900">{mockQuestions.length}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">正确率</span>
                <span className="text-2xl font-bold text-blue-600">{percentage}%</span>
              </div>
            </div>
            <button
              onClick={restart}
              className="w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              再练一遍
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">语法练习</h1>
          <p className="text-gray-600">通过选择题巩固语法知识</p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>进度</span>
            <span>{currentIndex + 1} / {mockQuestions.length}</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-xl mb-6">
          <div className="flex items-center gap-2 mb-6">
            <span className="text-sm font-medium text-indigo-600 bg-indigo-100 px-3 py-1 rounded-full">
              第 {currentIndex + 1} 题
            </span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-8">{currentQuestion.question}</h2>

          <div className="space-y-4">
            {currentQuestion.options.map((option, index) => {
              let buttonClass = 'border-2 border-gray-200 hover:border-indigo-300';
              if (isAnswered) {
                if (index === currentQuestion.correctAnswer) {
                  buttonClass = 'border-2 border-green-500 bg-green-50';
                } else if (index === selectedAnswer) {
                  buttonClass = 'border-2 border-red-500 bg-red-50';
                }
              } else if (selectedAnswer === index) {
                buttonClass = 'border-2 border-indigo-500 bg-indigo-50';
              }

              return (
                <button
                  key={index}
                  onClick={() => handleAnswer(index)}
                  disabled={isAnswered}
                  className={`w-full text-left p-4 rounded-xl transition-all flex items-center justify-between ${buttonClass} ${
                    isAnswered ? 'cursor-default' : 'cursor-pointer'
                  }`}
                >
                  <span className="font-medium text-gray-900">{option}</span>
                  {isAnswered && index === currentQuestion.correctAnswer && (
                    <Check className="w-5 h-5 text-green-600" />
                  )}
                  {isAnswered && index === selectedAnswer && index !== currentQuestion.correctAnswer && (
                    <X className="w-5 h-5 text-red-600" />
                  )}
                </button>
              );
            })}
          </div>

          {isAnswered && (
            <div className={`mt-6 p-4 rounded-xl ${
              selectedAnswer === currentQuestion.correctAnswer
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}>
              <p className={`font-medium mb-2 ${
                selectedAnswer === currentQuestion.correctAnswer
                  ? 'text-green-800'
                  : 'text-red-800'
              }`}>
                {selectedAnswer === currentQuestion.correctAnswer ? '回答正确！' : '回答错误'}
              </p>
              <p className="text-gray-600">{currentQuestion.explanation}</p>
            </div>
          )}
        </div>

        <div className="flex gap-4">
          <button
            onClick={previousQuestion}
            disabled={currentIndex === 0}
            className="flex-1 bg-gray-100 text-gray-700 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <ChevronLeft className="w-5 h-5" />
            上一题
          </button>
          {isAnswered ? (
            <button
              onClick={nextQuestion}
              className="flex-1 bg-indigo-600 text-white py-4 rounded-xl font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              {currentIndex === mockQuestions.length - 1 ? '查看结果' : '下一题'}
              <ChevronRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              disabled
              className="flex-1 bg-gray-100 text-gray-400 py-4 rounded-xl font-semibold cursor-not-allowed"
            >
              请先选择答案
            </button>
          )}
        </div>

        <div className="mt-8 bg-white rounded-3xl p-6 shadow-lg">
          <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            题目列表
          </h3>
          <div className="flex flex-wrap gap-3">
            {mockQuestions.map((q, index) => {
              const answered = answeredQuestions.has(q.id);
              const correct = answered && mockQuestions[index].correctAnswer === selectedAnswer;
              return (
                <button
                  key={q.id}
                  onClick={() => {
                    setCurrentIndex(index);
                    setSelectedAnswer(null);
                  }}
                  className={`w-12 h-12 rounded-xl font-semibold flex items-center justify-center transition-all ${
                    index === currentIndex
                      ? 'bg-indigo-600 text-white'
                      : answered
                      ? correct
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {index + 1}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Grammar;
