import { useState } from 'react';
import { Volume2, Mic, RotateCcw, Check, ChevronRight, Play } from 'lucide-react';

interface SpeakingPractice {
  id: string;
  text: string;
  translation: string;
  phonetic?: string;
}

const mockSpeaking: SpeakingPractice[] = [
  {
    id: '1',
    text: 'Hello, how are you?',
    translation: '你好，你好吗？',
    phonetic: 'həˈloʊ, haʊ ɑːr juː?',
  },
  {
    id: '2',
    text: 'I am fine, thank you.',
    translation: '我很好，谢谢。',
    phonetic: 'aɪ æm faɪn, θæŋk juː.',
  },
  {
    id: '3',
    text: 'Nice to meet you.',
    translation: '很高兴认识你。',
    phonetic: 'naɪs tuː miːt juː.',
  },
  {
    id: '4',
    text: 'Where are you from?',
    translation: '你来自哪里？',
    phonetic: 'wer ɑːr juː frʌm?',
  },
  {
    id: '5',
    text: 'I love learning languages.',
    translation: '我喜欢学习语言。',
    phonetic: 'aɪ lʌv ˈlɜːrnɪŋ ˈlæŋɡwɪdʒɪz.',
  },
];

const Speaking = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [completedPractices, setCompletedPractices] = useState<Set<string>>(new Set());
  const [showResult, setShowResult] = useState(false);

  const currentPractice = mockSpeaking[currentIndex];
  const isCompleted = completedPractices.has(currentPractice.id);
  const progress = Math.round(((currentIndex + (showResult ? 1 : 0)) / mockSpeaking.length) * 100);

  const playAudio = () => {
    setIsPlaying(true);
    setTimeout(() => setIsPlaying(false), 2000);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setTimeout(() => {
        setIsRecording(false);
        setCompletedPractices((prev) => new Set(prev).add(currentPractice.id));
      }, 2000);
    }
  };

  const nextPractice = () => {
    if (currentIndex < mockSpeaking.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResult(true);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setCompletedPractices(new Set());
    setShowResult(false);
  };

  if (showResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-3xl p-8 shadow-xl text-center">
            <div className="w-24 h-24 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Mic className="w-12 h-12 text-orange-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">口语练习完成！</h2>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">已完成练习</span>
                <span className="text-2xl font-bold text-green-600">{completedPractices.size}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">总练习数</span>
                <span className="text-2xl font-bold text-gray-900">{mockSpeaking.length}</span>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">口语跟读</h1>
          <p className="text-gray-600">跟着标准发音练习口语</p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>进度</span>
            <span>{currentIndex + 1} / {mockSpeaking.length}</span>
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
              className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto transition-all ${
                isPlaying
                  ? 'bg-indigo-600 animate-pulse'
                  : 'bg-blue-100 hover:bg-blue-200'
              }`}
            >
              {isPlaying ? (
                <Volume2 className="w-8 h-8 text-white" />
              ) : (
                <Play className="w-8 h-8 text-blue-600 ml-1" />
              )}
            </button>
            <p className="mt-3 text-gray-500">点击播放标准发音</p>
          </div>

          <div className="text-center mb-8">
            <div className="text-3xl font-bold text-gray-900 mb-4">{currentPractice.text}</div>
            {currentPractice.phonetic && (
              <div className="text-lg text-gray-500 mb-2">{currentPractice.phonetic}</div>
            )}
            <div className="text-xl text-gray-600">{currentPractice.translation}</div>
          </div>

          <div className="text-center">
            <button
              onClick={toggleRecording}
              className={`w-28 h-28 rounded-full flex items-center justify-center mx-auto transition-all ${
                isRecording
                  ? 'bg-red-500 animate-pulse'
                  : 'bg-gradient-to-br from-orange-500 to-red-500 hover:scale-105'
              }`}
            >
              <Mic className={`w-12 h-12 text-white ${isRecording ? 'animate-bounce' : ''}`} />
            </button>
            <p className="mt-4 text-gray-500">
              {isRecording ? '正在录音...' : '点击开始录音'}
            </p>
          </div>

          {isCompleted && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl text-center">
              <Check className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <p className="text-green-800 font-medium">已完成跟读练习！</p>
            </div>
          )}
        </div>

        {isCompleted && (
          <button
            onClick={nextPractice}
            className="w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            {currentIndex === mockSpeaking.length - 1 ? '完成练习' : '下一句'}
            <ChevronRight className="w-5 h-5" />
          </button>
        )}

        <div className="mt-8 bg-white rounded-3xl p-6 shadow-lg">
          <h3 className="font-bold text-gray-900 mb-4">练习列表</h3>
          <div className="space-y-3">
            {mockSpeaking.map((practice, index) => (
              <div
                key={practice.id}
                onClick={() => setCurrentIndex(index)}
                className={`flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all ${
                  index === currentIndex
                    ? 'bg-indigo-50 border-2 border-indigo-500'
                    : completedPractices.has(practice.id)
                    ? 'bg-green-50'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  index === currentIndex
                    ? 'bg-indigo-600 text-white'
                    : completedPractices.has(practice.id)
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {completedPractices.has(practice.id) ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <span className="font-semibold">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">{practice.text}</p>
                  <p className="text-sm text-gray-500 truncate">{practice.translation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Speaking;
