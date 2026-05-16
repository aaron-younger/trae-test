import { useState } from 'react';
import { Volume2, Check, X, RotateCcw, Play, Pause, Headphones } from 'lucide-react';

interface ListeningQuestion {
  id: string;
  audioUrl: string;
  question: string;
  options: string[];
  correctAnswer: number;
  transcript: string;
  translation: string;
}

const mockListening: ListeningQuestion[] = [
  {
    id: '1',
    audioUrl: '/audio/1.mp3',
    question: 'What is the weather like?',
    options: ['Sunny', 'Rainy', 'Cloudy', 'Snowy'],
    correctAnswer: 0,
    transcript: "It's a beautiful sunny day today.",
    translation: '今天是个阳光明媚的好天气。',
  },
  {
    id: '2',
    audioUrl: '/audio/2.mp3',
    question: 'What time is it?',
    options: ['9 AM', '10 AM', '11 AM', '12 PM'],
    correctAnswer: 1,
    transcript: "It's ten o'clock in the morning.",
    translation: '现在是上午十点。',
  },
  {
    id: '3',
    audioUrl: '/audio/3.mp3',
    question: 'Where are they going?',
    options: ['Park', 'School', 'Store', 'Library'],
    correctAnswer: 2,
    transcript: "We need to go to the store to buy some food.",
    translation: '我们需要去商店买些食物。',
  },
  {
    id: '4',
    audioUrl: '/audio/4.mp3',
    question: 'How is the man feeling?',
    options: ['Happy', 'Sad', 'Tired', 'Angry'],
    correctAnswer: 2,
    transcript: "I'm very tired after working all day.",
    translation: '工作了一整天后，我非常累。',
  },
];

const Listening = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState<Set<string>>(new Set());
  const [isPlaying, setIsPlaying] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);

  const currentQuestion = mockListening[currentIndex];
  const isAnswered = answeredQuestions.has(currentQuestion.id);
  const progress = Math.round(((currentIndex + (showResult ? 1 : 0)) / mockListening.length) * 100);

  const playAudio = () => {
    setIsPlaying(true);
    setTimeout(() => setIsPlaying(false), 2000);
  };

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
    setShowTranscript(false);
    if (currentIndex < mockListening.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResult(true);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setScore(0);
    setShowResult(false);
    setAnsweredQuestions(new Set());
    setShowTranscript(false);
  };

  if (showResult) {
    const percentage = Math.round((score / mockListening.length) * 100);
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-3xl p-8 shadow-xl text-center">
            <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Headphones className="w-12 h-12 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">听力训练完成！</h2>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">正确答案</span>
                <span className="text-2xl font-bold text-green-600">{score}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">总题数</span>
                <span className="text-2xl font-bold text-gray-900">{mockListening.length}</span>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">听力训练</h1>
          <p className="text-gray-600">提升你的听力理解能力</p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>进度</span>
            <span>{currentIndex + 1} / {mockListening.length}</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-xl mb-6">
          <div className="text-center mb-8">
            <button
              onClick={playAudio}
              className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto transition-all ${
                isPlaying
                  ? 'bg-indigo-600 animate-pulse'
                  : 'bg-gradient-to-br from-indigo-500 to-purple-500 hover:scale-105'
              }`}
            >
              {isPlaying ? (
                <Pause className="w-10 h-10 text-white" />
              ) : (
                <Play className="w-10 h-10 text-white ml-1" />
              )}
            </button>
            <p className="mt-4 text-gray-500">点击播放音频</p>
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">{currentQuestion.question}</h2>

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
            <div className="mt-6">
              <button
                onClick={() => setShowTranscript(!showTranscript)}
                className="text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-2 mx-auto"
              >
                <Volume2 className="w-4 h-4" />
                {showTranscript ? '隐藏' : '显示'}原文和翻译
              </button>
              {showTranscript && (
                <div className="mt-4 p-6 bg-gray-50 rounded-xl">
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-500 mb-1">原文</p>
                    <p className="text-gray-900">{currentQuestion.transcript}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-1">翻译</p>
                    <p className="text-gray-700">{currentQuestion.translation}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {isAnswered && (
          <button
            onClick={nextQuestion}
            className="w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold hover:bg-indigo-700 transition-colors"
          >
            {currentIndex === mockListening.length - 1 ? '查看结果' : '下一题'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Listening;
