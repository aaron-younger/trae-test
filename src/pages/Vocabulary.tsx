import { useState } from 'react';
import { Volume2, Check, X, RotateCcw, ChevronRight, ChevronLeft, BookOpen } from 'lucide-react';
import { mockVocabulary } from '../data/mockData';

const Vocabulary = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownWords, setKnownWords] = useState<Set<string>>(new Set());
  const [showResult, setShowResult] = useState(false);

  const currentWord = mockVocabulary[currentIndex];
  const progress = Math.round(((currentIndex + (showResult ? 1 : 0)) / mockVocabulary.length) * 100);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleKnown = () => {
    setKnownWords((prev) => new Set(prev).add(currentWord.id));
    nextWord();
  };

  const handleUnknown = () => {
    nextWord();
  };

  const nextWord = () => {
    setIsFlipped(false);
    if (currentIndex < mockVocabulary.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResult(true);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setKnownWords(new Set());
    setShowResult(false);
  };

  const previousWord = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    }
  };

  const playPronunciation = () => {
    console.log('Playing pronunciation:', currentWord.pronunciation);
  };

  if (showResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-3xl p-8 shadow-xl text-center">
            <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="w-12 h-12 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">学习完成！</h2>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">已掌握单词</span>
                <span className="text-2xl font-bold text-green-600">{knownWords.size}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">总单词数</span>
                <span className="text-2xl font-bold text-gray-900">{mockVocabulary.length}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
                <span className="text-gray-600">掌握率</span>
                <span className="text-2xl font-bold text-blue-600">
                  {Math.round((knownWords.size / mockVocabulary.length) * 100)}%
                </span>
              </div>
            </div>
            <button
              onClick={restart}
              className="w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              再学一遍
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">单词学习</h1>
          <p className="text-gray-600">通过闪卡高效记忆单词</p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>进度</span>
            <span>{currentIndex + 1} / {mockVocabulary.length}</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="relative perspective-1000 mb-8">
          <div
            className={`relative w-full h-96 cursor-pointer transform-style-preserve-3d transition-transform duration-600 ${
              isFlipped ? 'rotate-y-180' : ''
            }`}
            onClick={handleFlip}
          >
            <div className="absolute inset-0 backface-hidden bg-white rounded-3xl shadow-xl p-8 flex flex-col items-center justify-center">
              <div className="text-6xl font-bold text-gray-900 mb-6">{currentWord.word}</div>
              <div className="text-gray-500 text-lg mb-4">{currentWord.pronunciation}</div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  playPronunciation();
                }}
                className="flex items-center gap-2 bg-blue-100 text-blue-600 px-6 py-3 rounded-xl hover:bg-blue-200 transition-colors"
              >
                <Volume2 className="w-5 h-5" />
                听发音
              </button>
              <div className="absolute bottom-8 text-gray-400 text-sm">点击卡片查看释义</div>
            </div>

            <div className="absolute inset-0 backface-hidden bg-gradient-to-br from-indigo-600 to-purple-600 rounded-3xl shadow-xl p-8 flex flex-col items-center justify-center rotate-y-180">
              <div className="text-4xl font-bold text-white mb-4">{currentWord.translation}</div>
              <div className="text-white/90 text-center max-w-md mb-6">
                <div className="text-lg font-medium mb-2">例句：</div>
                <div className="text-white/80">{currentWord.example}</div>
              </div>
              <div className="absolute bottom-8 text-white/60 text-sm">点击卡片返回</div>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <button
            onClick={previousWord}
            disabled={currentIndex === 0}
            className="flex-1 bg-gray-100 text-gray-700 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <ChevronLeft className="w-5 h-5" />
            上一个
          </button>
          <button
            onClick={nextWord}
            className="flex-1 bg-gray-100 text-gray-700 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
          >
            下一个
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={handleUnknown}
            className="bg-red-100 text-red-600 py-4 rounded-xl font-semibold hover:bg-red-200 transition-colors flex items-center justify-center gap-2"
          >
            <X className="w-5 h-5" />
            还不认识
          </button>
          <button
            onClick={handleKnown}
            className="bg-green-100 text-green-600 py-4 rounded-xl font-semibold hover:bg-green-200 transition-colors flex items-center justify-center gap-2"
          >
            <Check className="w-5 h-5" />
            已掌握
          </button>
        </div>

        <div className="mt-8 bg-white rounded-3xl p-6 shadow-lg">
          <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            单词列表
          </h3>
          <div className="space-y-3">
            {mockVocabulary.map((word, index) => (
              <div
                key={word.id}
                onClick={() => {
                  setCurrentIndex(index);
                  setIsFlipped(false);
                }}
                className={`flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all ${
                  index === currentIndex
                    ? 'bg-indigo-50 border-2 border-indigo-500'
                    : knownWords.has(word.id)
                    ? 'bg-green-50'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 font-medium">{index + 1}</span>
                  <div>
                    <div className="font-semibold text-gray-900">{word.word}</div>
                    <div className="text-sm text-gray-500">{word.translation}</div>
                  </div>
                </div>
                {knownWords.has(word.id) && <Check className="w-5 h-5 text-green-600" />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Vocabulary;
